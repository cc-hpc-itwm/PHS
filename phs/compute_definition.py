import time
import os
import pandas as pd
import importlib
import sys
import pickle
import pprint
import glob
import ntpath
import shutil

import phs.proxy
import phs.bayes
import phs.utils
import phs.utils_parameter_io
import phs.global_names


class ComputeDefinition:
    """ """

    def __init__(self,
                 ** kwargs_dict):

        phs.utils.print_section(header='ComputeDefinition')

        config_dict = kwargs_dict

        self.experiment_dir = phs.utils.set_default_value_to_optional_key(
            'experiment_dir', None, config_dict)
        self.parallelization = phs.utils.set_default_value_to_optional_key(
            'parallelization', 'local_processes', config_dict)
        self.local_processes_num_workers = phs.utils.set_default_value_to_optional_key(
            'local_processes_num_workers', 2, config_dict)
        self.provide_worker_path = phs.utils.set_default_value_to_optional_key(
            'provide_worker_path', True, config_dict)
        self.redirect_stdout = phs.utils.set_default_value_to_optional_key(
            'redirect_stdout', True, config_dict)
        self.bayesian_wait_for_all = phs.utils.set_default_value_to_optional_key(
            'bayesian_wait_for_all', False, config_dict)
        self.monitor_root_dir = phs.utils.set_default_value_to_optional_key(
            'monitor_root_dir', None, config_dict)
        self.monitor_module_name = phs.utils.set_default_value_to_optional_key(
            'monitor_module_name', None, config_dict)
        self.monitor_func_name_with_args = phs.utils.set_default_value_to_optional_key(
            'monitor_func_name_with_args', {}, config_dict)

        for key, value in config_dict.items():
            print('\t{0:40}{1:}'.format(key, value))

        self.result_col_name = 'result'
        self.symbol_for_best = '+'
        self.expression_data_type_flag = 'expr'
        self.pp = pprint.PrettyPrinter(indent=4)

        glob = phs.global_names.GlobalNames()
        self.target_module_root_dir = glob.get_lev1_source(self.experiment_dir)
        for file in os.listdir(self.target_module_root_dir):
            if file.endswith('.py'):
                self.target_module_name = os.path.splitext(file)[0]
                continue
            if file.endswith('.txt'):
                with open(self.target_module_root_dir + '/' + file, 'r') as f:
                    self.target_function_name = f.read()

        self.worker_save_path_root = glob.get_lev1_worker(self.experiment_dir)
        self.parameter_definitions_root_dir_in = glob.get_lev1_par(self.experiment_dir)
        self.result_file_path = glob.get_lev1_res(self.experiment_dir) + '/result_frame.csv'
        self.lock_result_path = glob.get_lev1_res(self.experiment_dir) + '/LOCK'
        self.additional_information_file_path = glob.get_lev1_res(
            self.experiment_dir) + '/additional_information_frame.csv'

        self.path_out_to_data_types_additional_information_dict = self.parameter_definitions_root_dir_in + \
            glob.get_name_data_types_additional_inf()

        self.path_out_to_bayesian_register_frame = self.parameter_definitions_root_dir_in + \
            glob.get_name_bay_reg()

        self.sub_future = []
        self.result_frame = pd.DataFrame()
        self.additional_information_frame = pd.DataFrame()

        (self.parameter_frame,
         self.bayesian_register_frame,
         self.bayesian_options_bounds_low_frame,
         self.bayesian_options_bounds_high_frame,
         self.data_types_ordered_list) = phs.utils_parameter_io.load_parameter_definitions(
            import_path=self.parameter_definitions_root_dir_in)

        if self.monitor_root_dir is not None:
            self.monitor_path = self.experiment_dir + '/monitor'
            os.mkdir(self.monitor_path)

        # import target function via strings
        sys.path.append(self.target_module_root_dir)
        self.target_module = importlib.import_module(self.target_module_name)
        self.target_function = getattr(self.target_module, self.target_function_name)

        # import monitor function via strings
        if self.monitor_root_dir:
            sys.path.append(self.monitor_root_dir)
        if self.monitor_module_name:
            self.monitor_module = importlib.import_module(self.monitor_module_name)

        self.monitor_functions_dict = {}
        for func_name in self.monitor_func_name_with_args:
            self.monitor_functions_dict[func_name] = getattr(self.monitor_module, func_name)

        self.get_experiment_state()

    def get_experiment_state(self):
        """
        Investigate the state of the experiment.
        Possible states are:
        - clean (no computations done at all)
        - incomplete (some parameter sets are computed)
        - finished (all parameter sets are computed)

        The existence and content of the result frame serves as a marker for the state. If the files does not
        exist the state is 'clean' and the a method to remove any remaining results will be called. The state is also
        'clean' if result file is empty (beside header).
        The state is 'incomplete' if result file has content and not computed indices are found.
        The state is 'finished' if result file has content and all indices are computed.
        """

        phs.utils.print_subsection('Experiment State')

        all_indices = self.parameter_frame.index.values.tolist()
        computed_indices = []

        # 'clean' state if result file does not exists
        if not os.path.isfile(self.result_file_path):
            self._ensure_clean_state()
        else:
            with open(self.result_file_path, 'r') as f:
                self.result_frame = pd.read_csv(f, index_col='index')
            with open(self.additional_information_file_path, 'r') as f:
                self.additional_information_frame = pd.read_csv(f, index_col='index')
            # 'clean' state if result file is empty (beside header)
            if self.result_frame.empty:
                self._ensure_clean_state()
            else:
                computed_indices = self.result_frame.index.values.tolist()

                self.remaining_parameter_index_list = list(
                    set(all_indices).difference(computed_indices))

                # 'incomplete' state if result file has content and not computed indices are found
                if self.remaining_parameter_index_list:
                    self.exp_state = 'incomplete'
                # 'finished' state if result file has content and all indices are computed
                else:
                    self.exp_state = 'finished'

        self.remaining_parameter_index_list.sort()

        print('\t{0:40}{1:}'.format('state', self.exp_state))
        print('\t{0:40}{1:}'.format('number of all parameter sets', len(all_indices)))
        print('\t{0:40}{1:}'.format('number of computed parameter sets', len(computed_indices)))

    def _ensure_clean_state(self):
        """
        Remove any results of previous computations on the current experiment and define clean state.
        """

        try:
            os.remove(self.result_file_path)
        except OSError:
            pass

        try:
            os.remove(self.additional_information_file_path)
        except OSError:
            pass

        for worker_path_file in glob.glob(self.worker_save_path_root + '/*'):
            if os.path.isfile(worker_path_file):
                phs.utils.format_stderr()
                raise ValueError('\n\n' + self.worker_save_path_root +
                                 ' should not contain any files.\nPlease investigate and delete by hand.\n')
            if os.path.isdir(worker_path_file):
                if ntpath.basename(worker_path_file).isdigit():
                    try:
                        shutil.rmtree(worker_path_file)
                    except OSError:
                        pass
                else:
                    phs.utils.format_stderr()
                    raise ValueError('\n\n' + self.worker_save_path_root +
                                     ' should only contain folders with all digit names.\
                                     \nPlease investigate and delete by hand.\n')
        try:
            os.remove(self.worker_save_path_root)
        except OSError:
            pass

        self.exp_state = 'clean'
        self.remaining_parameter_index_list = self.parameter_frame.index.values.tolist()

    def _initialize_result_file(self):
        header_list = list(self.parameter_frame.columns.values)
        header_string = 'index'
        for i in header_list:
            header_string = header_string + ',' + str(i)
        header_string = header_string + ',' + self.result_col_name + '\n'
        with open(self.result_file_path, 'w') as f:
            f.write(header_string)

    def start_execution(self):
        """ """
        if self.exp_state == 'finished':
            print('\n\tNothing to compute, all parameter sets have been computed.')
            return 1
        elif self.exp_state == 'clean':
            self._initialize_result_file()
            self.append_additional_information_init = False
        # in case of 'incomplete' state the initialization has to be skipped
        elif self.exp_state == 'incomplete':
            self.append_additional_information_init = True

        if not os.path.isdir(self.worker_save_path_root) and (self.provide_worker_path or self.redirect_stdout):
            os.mkdir(self.worker_save_path_root)

        phs.utils.print_subsection('Compute Environment')

        self.additional_submit_kwargs = {}

        if self.parallelization == 'local_processes':
            from concurrent.futures import ProcessPoolExecutor as PoolExecutor
            from concurrent.futures import wait, as_completed
            with PoolExecutor(max_workers=self.local_processes_num_workers) as executor:
                self.pp.pprint(executor.__dict__)
                self.start_execution_kernel(executor, wait, as_completed)
                self.as_completed_functions(as_completed)

            '''
            elif self.parallelization == 'mpi':
            from mpi4py.futures import MPIPoolExecutor as PoolExecutor
            from mpi4py.futures import wait, as_completed
            with PoolExecutor(max_workers=2) as executor:
                self.start_mpi_execution_kernel(executor, wait, as_completed)
                self.as_completed_functions(as_completed)'''

        elif self.parallelization == 'dask':
            self.additional_submit_kwargs = {'fifo_timeout': '0ms'}
            from dask.distributed import Client, progress, as_completed, wait
            DASK_MASTER_IP = os.environ['DASK_MASTER_IP']
            DASK_MASTER_PORT = os.environ['DASK_MASTER_PORT']
            with Client(DASK_MASTER_IP + ':' + DASK_MASTER_PORT, timeout='10s') as client:
                client.restart()
                self.pp.pprint(client.scheduler_info())
                client.upload_file(os.path.abspath(phs.bayes.__file__))  # probably not necessary
                client.upload_file(os.path.abspath(phs.proxy.__file__))  # probably not necessary
                client.upload_file(os.path.abspath(phs.utils.__file__))  # probably not necessary
                client.upload_file(self.target_module_root_dir + '/' +
                                   self.target_module_name + '.py')
                self.start_execution_kernel(client, wait, as_completed)
                self.as_completed_functions(as_completed)
        return 1

    def start_execution_kernel(self, executor, wait, as_completed):
        """

        Parameters
        ----------
        executor :

        wait :

        as_completed :


        Returns
        -------

        """
        phs.utils.print_subsection(header='start execution')
        print('\t\'watch -n 1 "(head -n 1; tail -n 10) < %s\"\'' %
              (self.result_file_path))
        paths = {'lock_result_path': self.lock_result_path,
                 'result_file_path': self.result_file_path}

        # list_of_parameter_dicts = self.parameter_frame.to_dict(orient='records')  # dtypes are not preserved
        # print(self.parameter_frame)
        # print(self.data_types_ordered_list)
        # list_of_parameter_dicts = []
        # for row in self.parameter_frame.itertuples(name=None, index=False):
        #   print(row)
        #  list_of_parameter_dicts.append(4)
        # list_of_parameter_dicts =
        # [{col:getattr(row, col) for col in self.parameter_frame} for row in self.parameter_frame.itertuples()]
        # print(list_of_parameter_dicts)
        list_of_bayesian_register_dicts = self.bayesian_register_frame.to_dict(
            orient='records')
        list_of_bayesian_options_bounds_low_dicts = self.bayesian_options_bounds_low_frame.to_dict(
            orient='records')
        list_of_bayesian_options_bounds_high_dicts = self.bayesian_options_bounds_high_frame.to_dict(
            orient='records')
        for i in self.remaining_parameter_index_list:
            parameter_dict = {}
            for col in self.parameter_frame.columns.values:
                parameter_dict[col] = self.parameter_frame.at[i, col]
            bayesian_register_dict_i = list_of_bayesian_register_dicts[i]
            auxiliary_information = {'provide_worker_path': self.provide_worker_path,
                                     'redirect_stdout': self.redirect_stdout,
                                     'worker_save_path_root': self.worker_save_path_root}
            if not any(bayesian_register_dict_i.values()):
                self.sub_future.append(
                    executor.submit(phs.proxy.proxy_function,
                                    self.parallelization,
                                    self.target_function,
                                    arg=parameter_dict,
                                    index=i,
                                    data_types_ordered_list=self.data_types_ordered_list,
                                    expression_data_type_flag=self.expression_data_type_flag,
                                    auxiliary_information=auxiliary_information,
                                    **self.additional_submit_kwargs))
            else:
                bayesian_register_dict_i = list_of_bayesian_register_dicts[i]
                bayesian_options_bounds_low_dict_i = list_of_bayesian_options_bounds_low_dicts[i]
                bayesian_options_bounds_high_dict_i = list_of_bayesian_options_bounds_high_dicts[i]
                self.sub_future.append(
                    executor.submit(phs.proxy.proxy_function,
                                    self.parallelization,
                                    self.target_function,
                                    arg=parameter_dict,
                                    index=i,
                                    data_types_ordered_list=self.data_types_ordered_list,
                                    expression_data_type_flag=self.expression_data_type_flag,
                                    auxiliary_information=auxiliary_information,
                                    with_bayesian=True,
                                    paths=paths,
                                    result_col_name=self.result_col_name,
                                    bayesian_wait_for_all=self.bayesian_wait_for_all,
                                    bayesian_register_dict=bayesian_register_dict_i,
                                    bayesian_options_bounds_low_dict=bayesian_options_bounds_low_dict_i,
                                    bayesian_options_bounds_high_dict=bayesian_options_bounds_high_dict_i,
                                    **self.additional_submit_kwargs))
        return 1

    def as_completed_functions(self, as_completed):
        """

        Parameters
        ----------
        as_completed :


        Returns
        -------

        """
        print('', end='\n')
        sub_future_len = len(self.sub_future)
        progress_bar_len = 40
        for count_finished, f in enumerate(as_completed(self.sub_future), 1):
            finished_portion = count_finished/sub_future_len
            progress_bar_signs = int(round(progress_bar_len * finished_portion))
            print('[{0}] | {1:>3}% | {2:>6} of {3:>6}' .format(
                '='*progress_bar_signs + ' '*(progress_bar_len-progress_bar_signs),
                int(round(finished_portion*100)), count_finished, len(self.sub_future)), end='\r')
            self.append_result(f)
            self.append_additional_information(f)
            self.monitor_functions()
        print('\n')
        return 1

    def append_result(self, future):
        """

        Parameters
        ----------
        future :


        Returns
        -------

        """
        index = (future.result())[0]
        current_result_dict = self.parameter_frame.iloc[[index]].to_dict(orient='list')
        if (future.result())[5] is not None:
            bayesian_replacement_dict = (future.result())[5]
            for col_name in bayesian_replacement_dict:
                current_result_dict[col_name] = bayesian_replacement_dict[col_name]
        current_result_dict[self.result_col_name] = (future.result())[1]
        current_result_df = pd.DataFrame(current_result_dict, index=[index])

        self.result_frame = self.result_frame.append(
            current_result_df, ignore_index=False, verify_integrity=False)

        # self.result_frame = self.result_frame.applymap(
        #     lambda x: round(x, 4) if isinstance(x, (int, float)) else x)
        while True:
            try:
                os.mkdir(self.lock_result_path)
                break
            except OSError:
                # print('write locked')
                time.sleep(0.5)
                continue

        with open(self.result_file_path, 'a') as f:
            current_result_df.to_csv(f, header=False, index=True)

        if os.path.exists(self.lock_result_path) and os.path.isdir(self.lock_result_path):
            os.rmdir(self.lock_result_path)

        return 1

    def append_additional_information(self, future):
        """

        Parameters
        ----------
        future :


        Returns
        -------

        """
        index = (future.result())[0]
        current_additional_information_dict = {}
        current_additional_information_dict['started'] = (future.result())[2]
        current_additional_information_dict['ended'] = (future.result())[3]
        current_additional_information_dict['execution time'] = (future.result())[
            3] - (future.result())[2]
        current_additional_information_dict['worker'] = (future.result())[4]
        current_additional_information_dict['state'] = (future._state)
        current_additional_information_df = pd.DataFrame(
            current_additional_information_dict, index=[index])
        self.additional_information_frame = self.additional_information_frame.append(
            current_additional_information_df, ignore_index=False, verify_integrity=False)

        if not self.append_additional_information_init:

            header_list = list(current_additional_information_df.columns.values)
            header_string = 'index'
            for i in header_list:
                header_string = header_string + ',' + str(i)
            header_string += '\n'
            with open(self.additional_information_file_path, 'w') as f:
                f.write(header_string)

            self.data_types_additional_information_dict = {}
            for key, value in current_additional_information_dict.items():
                self.data_types_additional_information_dict[key] = type(value)
            with open(self.path_out_to_data_types_additional_information_dict + '.pkl', 'wb') as f:
                pickle.dump(self.data_types_additional_information_dict, f)
            with open(self.path_out_to_data_types_additional_information_dict + '.txt', 'w') as f:
                f.write(str(self.data_types_additional_information_dict))

            self.append_additional_information_init = True

        with open(self.additional_information_file_path, 'a') as f:
            current_additional_information_df.to_csv(f, header=False, index=True)

        return 1

    def monitor_functions(self):
        """ """
        for monitor_function_string in self.monitor_func_name_with_args:
            kwargs_dict = self.monitor_func_name_with_args[monitor_function_string]
            kwargs_dict['path_out'] = self.monitor_path
            kwargs_dict['result_frame'] = self.result_frame
            kwargs_dict['additional_information_frame'] = self.additional_information_frame
            kwargs_dict['path_to_bayesian_register_frame'] = self.path_out_to_bayesian_register_frame
            self.monitor_functions_dict[monitor_function_string](**kwargs_dict)
        return 1
