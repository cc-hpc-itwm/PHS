import time
import datetime as dt
import os
import numpy as np
import pandas as pd
import random as rd
import json as js
import importlib
import sys
import io
from contextlib import redirect_stdout
from shutil import copy2

from phs import proxy
from phs import utils


class ParallelHyperparameterSearch:
    def __init__(self,
                 experiment_name,
                 working_dir,
                 custom_module_root_dir,
                 custom_module_name, custom_function_name,
                 parallelization,
                 parameter_data_types={},
                 monitor_root_dir=None,
                 monitor_module_name=None,
                 monitor_func_name_with_args={},
                 provide_insights_path=False):
        self.custom_module_root_dir = custom_module_root_dir
        self.custom_module_name = custom_module_name
        self.custom_function_name = custom_function_name
        self.monitor_root_dir = monitor_root_dir
        self.monitor_module_name = monitor_module_name
        self.monitor_func_name_with_args = monitor_func_name_with_args
        self.sub_future = []
        self.data_types = parameter_data_types
        self.parameter_dict = {}
        self.parameter_dict_list = []
        self.parameter_frame = pd.DataFrame()
        self.result_frame = pd.DataFrame()
        self.additional_information_frame = pd.DataFrame()
        self.bayesian_register_dict = {}
        self.bayesian_register_dict_list = []
        self.bayesian_register_frame = pd.DataFrame()
        self.bayesian_options_bounds_low_dict = {}
        self.bayesian_options_bounds_low_dict_list = []
        self.bayesian_options_bounds_low_frame = pd.DataFrame()
        self.bayesian_options_bounds_high_dict = {}
        self.bayesian_options_bounds_high_dict_list = []
        self.bayesian_options_bounds_high_frame = pd.DataFrame()
        self.bayesian_options_round_digits_dict = {}
        self.bayesian_options_round_digits_dict_list = []
        self.bayesian_options_round_digits_frame = pd.DataFrame()
        self.parameter_string_list = []
        self.parameter_index_list = []
        self.bayesian_placeholder_phrase = 888888
        self.experiment_name = experiment_name
        self.working_dir = working_dir
        self.experiment_dir = self.working_dir + '/' + self.experiment_name
        self.result_path = self.experiment_dir + '/results'
        self.result_file_path = self.result_path + '/result_frame.csv'
        self.lock_result_path = self.result_path + '/LOCK'
        self.parameter_definitions_path = self.experiment_dir + '/parameter_definitions'
        self.source_code = self.experiment_dir + '/source_code_func'
        self.model_preview_path = self.experiment_dir + '/model_preview'
        self.path_to_parameter_frame = self.parameter_definitions_path + '/parameter_frame'
        self.path_to_bayesian_register_frame = self.parameter_definitions_path + '/bayesian_register_frame'
        self.path_to_bayesian_options_bounds_low_frame = self.parameter_definitions_path + \
            '/bayesian_options_bounds_low_frame'
        self.path_to_bayesian_options_bounds_high_frame = self.parameter_definitions_path + \
            '/bayesian_options_bounds_high_frame'
        self.path_to_bayesian_options_round_digits_frame = self.parameter_definitions_path + \
            '/bayesian_options_round_digits'
        self.parallelization = parallelization
        self.result_col_name = 'result'
        self.symbol_for_best = '+'

        if os.path.exists(self.working_dir) and os.path.isdir(self.working_dir):
            if os.path.exists(self.experiment_dir) and os.path.isdir(self.experiment_dir):
                raise ValueError('directory ' + self.experiment_dir +
                                 ' already exists. Please choose a different experiment name.')
            else:
                os.mkdir(self.experiment_dir)
                os.mkdir(self.result_path)
                os.mkdir(self.parameter_definitions_path)
                os.mkdir(self.source_code)

            if self.monitor_root_dir is not None:
                self.monitor_path = self.experiment_dir + '/monitor'
                os.mkdir(self.monitor_path)

            if provide_insights_path:
                self.worker_save_path = self.experiment_dir + '/insights'
                os.mkdir(self.worker_save_path)
            else:
                self.worker_save_path = False

        else:
            raise ValueError('directory ' + self.working_dir + ' doesn\'t exist.')

        copy2(self.custom_module_root_dir + '/' + self.custom_module_name +
              '.py', self.source_code + '/' + self.custom_module_name + '.py')

        sys.path.append(self.custom_module_root_dir)
        self.custom_module = importlib.import_module(self.custom_module_name)
        self.custom_function = getattr(self.custom_module, self.custom_function_name)

        if self.monitor_root_dir:
            sys.path.append(self.monitor_root_dir)
        if self.monitor_module_name:
            self.monitor_module = importlib.import_module(self.monitor_module_name)

        self.monitor_functions_dict = {}
        for func_name in self.monitor_func_name_with_args:
            self.monitor_functions_dict[func_name] = getattr(self.monitor_module, func_name)

    def add_random_numeric_parameter(self, parameter_name, bounds, distribution, dist_options={}, round_digits=None, resample_duplicate=True):
        value = bounds[0] + rd.random() * (bounds[1] - bounds[0])
        if round_digits is not None:
            value = round(value, round_digits)
            if round_digits <= 0:
                value = int(value)
        if resample_duplicate is True:
            if parameter_name in self.parameter_frame:
                if value in self.parameter_frame[parameter_name].tolist():
                    self.add_random_numeric_parameter(
                        parameter_name, bounds, distribution, dist_options, round_digits, resample_duplicate)
        self.parameter_dict[parameter_name] = value
        self.bayesian_register_dict[parameter_name] = 0

    def add_random_parameter_from_list(self, parameter_name, lst):
        value = rd.choice(lst)
        self.parameter_dict[parameter_name] = value
        self.bayesian_register_dict[parameter_name] = 0

    # TODO: https://github.com/jaberg/hyperopt/wiki/FMin

    def add_numeric_parameter(self, parameter_name, value):
        self.parameter_dict[parameter_name] = value
        self.bayesian_register_dict[parameter_name] = 0
        # TODO

    def add_bayesian_parameter(self, parameter_name, bounds, round_digits=None):
        self.parameter_dict[parameter_name] = self.bayesian_placeholder_phrase
        self.bayesian_register_dict[parameter_name] = 1
        self.bayesian_options_bounds_low_dict[parameter_name] = bounds[0]
        self.bayesian_options_bounds_high_dict[parameter_name] = bounds[1]
        self.bayesian_options_round_digits_dict[parameter_name] = round_digits

    def register_parameter_set(self):
        self.parameter_dict_list.append(self.parameter_dict)
        self.bayesian_register_dict_list.append(self.bayesian_register_dict)
        self.bayesian_options_bounds_low_dict_list.append(self.bayesian_options_bounds_low_dict)
        self.bayesian_options_bounds_high_dict_list.append(self.bayesian_options_bounds_high_dict)
        self.bayesian_options_round_digits_dict_list.append(self.bayesian_options_round_digits_dict)

        self.parameter_dict = {}
        self.bayesian_register_dict = {}
        self.bayesian_options_bounds_low_dict = {}
        self.bayesian_options_bounds_high_dict = {}
        self.bayesian_options_round_digits_dict = {}

    def show_parameter_set_dtypes(self):
        print(self.parameter_frame.dtypes)

    def show_parameter_set(self):
        print(self.parameter_frame)

    def show_bayesian_options_bounds_low_frame(self):
        print('bayesian_options_bounds_low_frame')
        print(self.bayesian_options_bounds_low_frame)

    def show_bayesian_options_bounds_high_frame(self):
        print('bayesian_options_bounds_high_frame')
        print(self.bayesian_options_bounds_high_frame)

    def show_bayesian_options_round_digits_frame(self):
        print('bayesian_options_round_digits_frame')
        print(self.bayesian_options_round_digits_frame)

    def create_parameter_string_list(self):
        self.parameter_string_list = []
        list_of_dicts = self.parameter_frame.to_dict(orient='records')
        for dict_i in list_of_dicts:
            for key in dict_i:
                dict_i[key] = dict_i[key].item()
            string = js.dumps(dict_i, separators=['\n', '='])
            string = string.replace('"', "")
            string = string.strip('{}')
            self.parameter_string_list.append(string)
        return self.parameter_string_list

    def show_model_preview(self, preview_function_name):
        os.mkdir(self.model_preview_path)
        with open(self.model_preview_path + '/model_preview.txt', 'w') as f:
            with redirect_stdout(f):
                self.model_preview_out(preview_function_name)
        self.model_preview_out(preview_function_name)

    def model_preview_out(self, preview_function_name):
        self.preview_function_name = preview_function_name
        self.loaded_preview_function = getattr(self.custom_module, self.preview_function_name)

        parameter_string_list_preview = self.create_parameter_string_list()
        parameter_index_list_preview = self.parameter_frame.index.values.tolist()
        list_of_parameter_dicts_preview = self.parameter_frame.astype(
            object).to_dict(orient='records')
        for i in parameter_index_list_preview:
            parameter_dict_i = list_of_parameter_dicts_preview[i]
            string = js.dumps(parameter_dict_i, separators=['\n', '='])
            # string = string.strip('{}')
            string = string[1:-1]
            for key in parameter_dict_i:
                string = string.replace("\"" + key + "\"", key)
            print('\nparameter set ' + str(i) + ':')
            self.loaded_preview_function(string)

    def save_parameter_definitions(self):
        start_time = time.time()

        self.parameter_frame = pd.DataFrame(self.parameter_dict_list)

        for par in self.data_types:
            self.parameter_frame[par] = self.parameter_frame[par].astype(self.data_types[par])

        self.bayesian_register_frame = pd.DataFrame(self.bayesian_register_dict_list)
        self.bayesian_options_bounds_low_frame = pd.DataFrame(
            self.bayesian_options_bounds_low_dict_list)
        self.bayesian_options_bounds_high_frame = pd.DataFrame(
            self.bayesian_options_bounds_high_dict_list)
        self.bayesian_options_round_digits_frame = pd.DataFrame(
            self.bayesian_options_round_digits_dict_list)

        if True:
            self.parameter_frame.to_pickle(self.path_to_parameter_frame + '.pkl')
            with open(self.path_to_parameter_frame + '.txt', 'w') as f:
                f.write(self.parameter_frame.to_string())
            self.parameter_frame.to_csv(self.path_to_parameter_frame +
                                        '.csv', sep='\t', index=True, header=True)

            self.bayesian_register_frame.to_pickle(self.path_to_bayesian_register_frame + '.pkl')
            with open(self.path_to_bayesian_register_frame + '.txt', 'w') as f:
                f.write(self.bayesian_register_frame.to_string())
            self.bayesian_options_bounds_low_frame.to_pickle(
                self.path_to_bayesian_options_bounds_low_frame + '.pkl')
            with open(self.path_to_bayesian_options_bounds_low_frame + '.txt', 'w') as f:
                f.write(self.bayesian_options_bounds_low_frame.to_string())
            self.bayesian_options_bounds_high_frame.to_pickle(
                self.path_to_bayesian_options_bounds_high_frame + '.pkl')
            with open(self.path_to_bayesian_options_bounds_high_frame + '.txt', 'w') as f:
                f.write(self.bayesian_options_bounds_high_frame.to_string())
            self.bayesian_options_round_digits_frame.to_pickle(
                self.path_to_bayesian_options_round_digits_frame + '.pkl')
            with open(self.path_to_bayesian_options_round_digits_frame + '.txt', 'w') as f:
                f.write(self.bayesian_options_round_digits_frame.to_string())
        print('\nsave parameter definitions:\t%.3f' % (time.time()-start_time), end='\n')

    def initialize_result_file(self):
        header_list = list(self.parameter_frame.columns.values)
        header_string = 'index'
        for i in header_list:
            header_string = header_string + ',' + str(i)
        header_string = header_string + ',' + self.result_col_name + '\n'
        with open(self.result_file_path, 'w') as f:
            f.write(header_string)

    def start_execution(self):
        self.save_parameter_definitions()
        self.initialize_result_file()
        if self.parallelization == 'processes':
            from concurrent.futures import ProcessPoolExecutor as PoolExecutor
            from concurrent.futures import wait, as_completed
            with PoolExecutor(max_workers=2) as executor:
                self.start_processes_execution_kernel(executor, wait, as_completed)
                self.as_completed_functions(as_completed)

        elif self.parallelization == 'mpi':
            from mpi4py.futures import MPIPoolExecutor as PoolExecutor
            from mpi4py.futures import wait, as_completed
            with PoolExecutor(max_workers=2) as executor:
                self.start_mpi_execution_kernel(executor, wait, as_completed)
                self.as_completed_functions(as_completed)

        elif self.parallelization == 'dask':
            from dask.distributed import Client, progress, as_completed, scheduler, wait
            DASK_MASTER_IP = os.environ['DASK_MASTER_IP']
            DASK_MASTER_PORT = os.environ['DASK_MASTER_PORT']
            with Client(DASK_MASTER_IP + ':' + DASK_MASTER_PORT, timeout='50s') as client:
                # client.upload_file(self.repository_root_dir + '/parallel_hyperparameter_search/phs/utils.py')
                # client.upload_file(self.repository_root_dir + '/parallel_hyperparameter_search/phs/bayes.py')
                # client.upload_file(self.repository_root_dir + '/parallel_hyperparameter_search/phs/proxy.py')
                client.upload_file(self.custom_module_root_dir + '/' +
                                   self.custom_module_name + '.py')
                self.start_dask_execution_kernel(client, wait, as_completed)
                self.as_completed_functions(as_completed)

        # if 'final' in self.plot_modus and self.plots:
        #    print('\n',end='')
        #    self.refresh_plot(contour=True)
        return 1

    def start_processes_execution_kernel(self, executor, wait, as_completed):
        start_time = time.time()
        parameter_index_list = self.parameter_frame.index.values.tolist()
        paths = {'lock_result_path': self.lock_result_path,
                 'result_file_path': self.result_file_path,
                 'path_to_bayesian_options_bounds_low_frame': self.path_to_bayesian_options_bounds_low_frame,
                 'path_to_bayesian_options_bounds_high_frame': self.path_to_bayesian_options_bounds_high_frame,
                 'path_to_bayesian_options_round_digits_frame': self.path_to_bayesian_options_round_digits_frame}

        list_of_parameter_dicts = self.parameter_frame.to_dict(orient='records')
        list_of_bayesian_register_dicts = self.bayesian_register_frame.to_dict(
            orient='records')
        list_of_bayesian_options_bounds_low_dicts = self.bayesian_options_bounds_low_frame.to_dict(
            orient='records')
        list_of_bayesian_options_bounds_high_dicts = self.bayesian_options_bounds_high_frame.to_dict(
            orient='records')
        list_of_bayesian_options_round_digits_dicts = self.bayesian_options_round_digits_frame.to_dict(
            orient='records')
        for i in parameter_index_list:
            parameter_dict_i = list_of_parameter_dicts[i]
            auxiliary_information = {'save_path': self.worker_save_path, 'parameter_index': i}
            if self.bayesian_placeholder_phrase not in parameter_dict_i.values():
                self.sub_future.append(executor.submit(proxy.proxy_function,
                                                       self.parallelization,
                                                       self.custom_function,
                                                       arg=parameter_dict_i,
                                                       index=i,
                                                       auxiliary_information=auxiliary_information))
            else:
                bayesian_register_dict_i = list_of_bayesian_register_dicts[i]
                bayesian_options_bounds_low_dict_i = list_of_bayesian_options_bounds_low_dicts[i]
                bayesian_options_bounds_high_dict_i = list_of_bayesian_options_bounds_high_dicts[i]
                bayesian_options_round_digits_dict_i = list_of_bayesian_options_round_digits_dicts[i]
                self.sub_future.append(executor.submit(proxy.proxy_function,
                                                       self.parallelization,
                                                       self.custom_function,
                                                       arg=parameter_dict_i,
                                                       index=i,
                                                       auxiliary_information=auxiliary_information,
                                                       with_bayesian=True,
                                                       bayesian_placeholder_phrase=self.bayesian_placeholder_phrase,
                                                       paths=paths,
                                                       data_types=self.data_types,
                                                       result_col_name=self.result_col_name,
                                                       bayesian_register_dict=bayesian_register_dict_i,
                                                       bayesian_options_bounds_low_dict=bayesian_options_bounds_low_dict_i,
                                                       bayesian_options_bounds_high_dict=bayesian_options_bounds_high_dict_i,
                                                       bayesian_options_round_digits_dict=bayesian_options_round_digits_dict_i))
        print('\nstart processes:\t%.3f' % (time.time()-start_time), end='\n')
        return 1

    def start_mpi_execution_kernel(self, executor, wait, as_completed):
        parameter_string_list = self.create_parameter_string_list()
        parameter_index_list = self.parameter_frame.index.values.tolist()
        paths = {'lock_result_path': self.lock_result_path, 'result_file_path': self.result_file_path, 'path_to_bayesian_options_bounds_low_frame': self.path_to_bayesian_options_bounds_low_frame,
                 'path_to_bayesian_options_bounds_high_frame': self.path_to_bayesian_options_bounds_high_frame, 'path_to_bayesian_options_round_digits_frame': self.path_to_bayesian_options_round_digits_frame}

        list_of_parameter_dicts = self.parameter_frame.astype(object).to_dict(orient='records')
        for i in parameter_index_list:
            parameter_dict_i = list_of_parameter_dicts[i]
            auxiliary_information = {'save_path': self.worker_save_path, 'parameter_index': i}
            if self.bayesian_placeholder_phrase not in parameter_dict_i.values():
                self.sub_future.append(executor.submit(proxy.proxy_function, self.parallelization,
                                                       self.custom_function, arg=parameter_dict_i, index=i, auxiliary_information=auxiliary_information))
            else:
                self.sub_future.append(executor.submit(proxy.proxy_function, self.parallelization, self.custom_function, arg=parameter_dict_i, index=i, auxiliary_information=auxiliary_information,
                                                       with_bayesian=True, bayesian_placeholder_phrase=self.bayesian_placeholder_phrase, paths=paths, data_types=self.data_types))
        return 1

    def start_dask_execution_kernel(self, executor, wait, as_completed):
        parameter_string_list = self.create_parameter_string_list()
        parameter_index_list = self.parameter_frame.index.values.tolist()
        paths = {'lock_result_path': self.lock_result_path, 'result_file_path': self.result_file_path, 'path_to_bayesian_options_bounds_low_frame': self.path_to_bayesian_options_bounds_low_frame,
                 'path_to_bayesian_options_bounds_high_frame': self.path_to_bayesian_options_bounds_high_frame, 'path_to_bayesian_options_round_digits_frame': self.path_to_bayesian_options_round_digits_frame}

        list_of_parameter_dicts = self.parameter_frame.astype(object).to_dict(orient='records')
        for i in parameter_index_list:
            parameter_dict_i = list_of_parameter_dicts[i]
            auxiliary_information = {'save_path': self.worker_save_path, 'parameter_index': i}
            if self.bayesian_placeholder_phrase not in parameter_dict_i.values():
                self.sub_future.append(executor.submit(proxy.proxy_function, self.parallelization, self.custom_function,
                                                       arg=parameter_dict_i, index=i, auxiliary_information=auxiliary_information, priority=10, fifo_timeout='0ms'))
            else:
                self.sub_future.append(executor.submit(proxy.proxy_function, self.parallelization, self.custom_function, arg=parameter_dict_i, index=i, auxiliary_information=auxiliary_information,
                                                       with_bayesian=True, bayesian_placeholder_phrase=self.bayesian_placeholder_phrase, paths=paths, data_types=self.data_types, priority=-10, fifo_timeout='0ms'))
        return 1

    def as_completed_functions(self, as_completed):
        print('\tparallelized function:\t\t\'%s\'' % (self.custom_function_name))
        print('\tlocated in:\t\t\t\'%s\'' %
              (self.custom_module_root_dir + '/' + self.custom_module_name))
        print('\tparallelized with:\t\t\'%s\'' % (self.parallelization))
        print('\texperiment results saved in:\t\'%s\':\t' % (self.experiment_dir), end='\n')
        print('\twatch individual tasks :\t\'watch -n 1 "(head -n 1; tail -n 10) < %s\"\'' %
              (self.result_file_path))
        for count_finished, f in enumerate(as_completed(self.sub_future), 1):
            # print('finished tasks:\t%i of %i' % (count_finished, len(self.sub_future)), end='\r')
            self.append_result(f)
            self.append_additional_information(f)
            # self.swap_files(count_finished)
            self.monitor_functions()
        print('\n')
        return 1

    def append_result(self, future):
        start_time = time.time()

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

        # print('\nrefresh log:\t%.3f' % (time.time()-start_time), end='\n')
        return 1

    def append_additional_information(self, future):
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
        return 1

    def refresh_log_old(self):
        start_time = time.time()
        self.log_frame = self.parameter_frame.copy(deep=True)
        self.log_frame['result'] = None
        self.log_frame['started'] = None
        self.log_frame['ended'] = None
        self.log_frame['execution time'] = None
        self.log_frame['best'] = ''
        self.log_frame['worker'] = ''
        best = 1000000
        best_i = -1
        for i in range(len(self.sub_future)):
            if self.parallelization == 'processes':
                self.log_frame.loc[i, 'state'] = self.sub_future[i]._state
                if self.sub_future[i]._state == 'FINISHED':
                    self.log_frame.loc[i, 'result'] = (self.sub_future[i].result())[0]
                    self.log_frame.loc[i, 'started'] = (self.sub_future[i].result())[1]
                    self.log_frame.loc[i, 'ended'] = (self.sub_future[i].result())[2]
                    self.log_frame.loc[i, 'execution time'] = (self.sub_future[i].result())[
                        2] - (self.sub_future[i].result())[1]
                    self.log_frame.loc[i, 'worker'] = (self.sub_future[i]._result)[3]
                    if (self.sub_future[i].result())[0] < best:
                        best = (self.sub_future[i].result())[0]
                        best_i = i
                    if (self.sub_future[i].result())[4] != None:
                        bayesian_replacement_dict = self.sub_future[i].result()[4]
                        for col_name in bayesian_replacement_dict:
                            self.log_frame.loc[i, col_name] = bayesian_replacement_dict[col_name]
            elif self.parallelization == 'mpi':
                self.log_frame.loc[i, 'state'] = self.sub_future[i]._state
                if self.sub_future[i]._state == 'FINISHED':
                    self.log_frame.loc[i, 'result'] = (self.sub_future[i]._result)[0]
                    self.log_frame.loc[i, 'started'] = (self.sub_future[i]._result)[1]
                    self.log_frame.loc[i, 'ended'] = (self.sub_future[i]._result)[2]
                    self.log_frame.loc[i, 'execution time'] = (self.sub_future[i]._result)[
                        2] - (self.sub_future[i]._result)[1]
                    self.log_frame.loc[i, 'worker'] = (self.sub_future[i]._result)[3]
                    if (self.sub_future[i]._result)[0] < best:
                        best = (self.sub_future[i]._result)[0]
                        best_i = i
                    if (self.sub_future[i]._result)[4] != None:
                        bayesian_replacement_dict = self.sub_future[i]._result[4]
                        for col_name in bayesian_replacement_dict:
                            self.log_frame.loc[i, col_name] = bayesian_replacement_dict[col_name]
            elif self.parallelization == 'dask':
                self.log_frame.loc[i, 'state'] = self.sub_future[i].status
                if self.sub_future[i].status == 'finished' or self.sub_future[i].status == 'error':
                    self.log_frame.loc[i, 'result'] = (self.sub_future[i].result())[0]
                    self.log_frame.loc[i, 'started'] = (self.sub_future[i].result())[1]
                    self.log_frame.loc[i, 'ended'] = (self.sub_future[i].result())[2]
                    self.log_frame.loc[i, 'execution time'] = (self.sub_future[i].result())[
                        2] - (self.sub_future[i].result())[1]
                    self.log_frame.loc[i, 'worker'] = (self.sub_future[i].result())[3]
                    if (self.sub_future[i].result())[0] < best:
                        best = (self.sub_future[i].result())[0]
                        best_i = i
                    if (self.sub_future[i].result())[4] != None:
                        bayesian_replacement_dict = self.sub_future[i].result()[4]
                        for col_name in bayesian_replacement_dict:
                            self.log_frame.loc[i, col_name] = bayesian_replacement_dict[col_name]
        if best_i != -1:
            self.log_frame.loc[best_i, 'best'] = self.symbol_for_best
        self.log_frame = self.log_frame.applymap(
            lambda x: round(x, 4) if isinstance(x, (int, float)) else x)
        with open(self.result_file_path, 'w') as f:
            f.write(self.log_frame.to_string())

        print('\nrefresh log:\t%.3f' % (time.time()-start_time), end='\n')
        return 1

    def swap_files(self, count_finished):
        start_time = time.time()
        i = count_finished
        fill = 6
        current_folder = self.swap_path + '/' + str(i).zfill(fill)
        os.mkdir(current_folder)
        log_frame_rec = self.log_frame.to_records()
        np.save(current_folder + '/log_frame.npy', log_frame_rec)
        parameter_frame_rec = self.parameter_frame.to_records()
        np.save(current_folder + '/parameter_frame.npy', parameter_frame_rec)
        # self.log_frame.to_pickle(current_folder + '/log_frame.pkl')
        # self.parameter_frame.to_pickle(current_folder + '/parameter_frame.pkl')

        # with open(current_folder + '/log_frame.txt', 'w') as f:
        #     f.write(self.log_frame.to_string())

        old_folder = self.swap_path + '/' + str(i-2).zfill(fill)
        if os.path.exists(old_folder) and os.path.isdir(old_folder):
            os.remove(old_folder + '/log_frame.npy')
            os.remove(old_folder + '/parameter_frame.npy')
            os.rmdir(old_folder)
        print('swap files:\t%.3f' % (time.time()-start_time), end='\n')
        return 1

    def monitor_functions(self):
        start_time = time.time()
        for monitor_function_string in self.monitor_func_name_with_args:
            kwargs_dict = self.monitor_func_name_with_args[monitor_function_string]
            kwargs_dict['monitor_path'] = self.monitor_path
            kwargs_dict['result_frame'] = self.result_frame
            kwargs_dict['additional_information_frame'] = self.additional_information_frame
            kwargs_dict['path_to_bayesian_register_frame'] = self.path_to_bayesian_register_frame
            self.monitor_functions_dict[monitor_function_string](**kwargs_dict)

        # print('refresh plot:\t%.3f' %(time.time()-start_time), end='\t')
        return 1
