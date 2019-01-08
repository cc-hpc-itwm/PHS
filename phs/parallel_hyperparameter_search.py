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

#spec = importlib.util.spec_from_file_location("Record", "/home/HabelitzP/record_root/record/record.py")
#rc = importlib.util.module_from_spec(spec)
#spec.loader.exec_module(rc)

class ParallelHyperparameterSearch:
    def __init__(self, experiment_name, working_dir, repository_root_dir, custom_module_root_dir, custom_module_name, custom_function_name, parallelization, parameter_data_types={}, monitor_root_dir=None, monitor_module_name=None, monitor_func_name_with_args={}):
        self.custom_module_root_dir = custom_module_root_dir
        self.custom_module_name = custom_module_name
        self.custom_function_name = custom_function_name
        self.monitor_root_dir = monitor_root_dir
        self.monitor_module_name = monitor_module_name
        self.monitor_func_name_with_args = monitor_func_name_with_args
        self.sub_future = []
        self.data_types = parameter_data_types
        self.parameter_dict = {}
        self.parameter_frame = pd.DataFrame()
        self.log_frame = pd.DataFrame()
        self.bayesian_register_dict = {}
        self.bayesian_register_frame = pd.DataFrame()
        self.bayesian_options_bounds_low_dict = {}
        self.bayesian_options_bounds_low_frame = pd.DataFrame()
        self.bayesian_options_bounds_high_dict = {}
        self.bayesian_options_bounds_high_frame = pd.DataFrame()
        self.bayesian_options_round_digits_dict = {}
        self.bayesian_options_round_digits_frame = pd.DataFrame()
        self.parameter_string_list = []
        self.parameter_index_list = []
        self.bayesian_placeholder_phrase = 888888
        self.experiment_name = experiment_name
        self.working_dir = working_dir
        self.repository_root_dir = repository_root_dir
        self.experiment_dir = self.working_dir + '/' + self.experiment_name
        self.log_path = self.experiment_dir + '/log'
        self.monitor_path = self.experiment_dir + '/monitor'
        self.swap_path = self.experiment_dir + '/swap_files'
        self.worker_save_path = self.experiment_dir + '/insights'
        self.source_code = self.experiment_dir + '/source_code'
        self.model_preview_path = self.experiment_dir + '/model_preview'
        self.path_to_parameter_frame = self.swap_path + '/parameter_frame'
        self.path_to_bayesian_register_frame = self.swap_path + '/bayesian_register_frame'
        self.path_to_bayesian_options_bounds_low_frame = self.swap_path + '/bayesian_options_bounds_low_frame'
        self.path_to_bayesian_options_bounds_high_frame = self.swap_path + '/bayesian_options_bounds_high_frame'
        self.path_to_bayesian_options_round_digits_frame = self.swap_path + '/bayesian_options_round_digits'
        self.parallelization = parallelization
        self.symbol_for_best = '+'
        
        if os.path.exists(self.working_dir) and os.path.isdir(self.working_dir):
            if os.path.exists(self.experiment_dir) and os.path.isdir(self.experiment_dir):
                raise ValueError('directory ' + self.experiment_dir + ' already exists. Please choose a different experiment name.')
            else:
                os.mkdir(self.experiment_dir)
                os.mkdir(self.log_path)
                os.mkdir(self.monitor_path)
                os.mkdir(self.swap_path)
                os.mkdir(self.worker_save_path)
                os.mkdir(self.source_code)
        else:
            raise ValueError('directory ' + self.working_dir + ' doesn\'t exist.')
        
        copy2(self.custom_module_root_dir + '/' + self.custom_module_name + '.py', self.source_code + '/' + self.custom_module_name + '.py')
        
        sys.path.append(self.custom_module_root_dir)
        self.custom_module = importlib.import_module(self.custom_module_name)
        self.custom_function = getattr(self.custom_module,self.custom_function_name)
        
        if self.monitor_root_dir:
            sys.path.append(self.monitor_root_dir)
        if self.monitor_module_name:
            self.monitor_module = importlib.import_module(self.monitor_module_name)
        
        self.monitor_functions_dict = {}
        for func_name in self.monitor_func_name_with_args:
            self.monitor_functions_dict[func_name] = getattr(self.monitor_module,func_name)
            

    def add_random_numeric_parameter(self,parameter_name,bounds,distribution,dist_options={},round_digits=None):
        value = bounds[0] + rd.random() * (bounds[1] - bounds[0])
        if round_digits is not None:
            value = round(value, round_digits)
            if round_digits <= 0:
                value = int(value)
        self.parameter_dict[parameter_name] = value
        self.bayesian_register_dict[parameter_name] = 0
        
    def add_random_parameter_from_list(self,parameter_name,lst):
        value = rd.choice(lst)
        self.parameter_dict[parameter_name] = value
        self.bayesian_register_dict[parameter_name] = 0
        
    # TODO: https://github.com/jaberg/hyperopt/wiki/FMin
    
    def add_numeric_parameter(self,parameter_name,value):
        self.parameter_dict[parameter_name] = value
        self.bayesian_register_dict[parameter_name] = 0
        # TODO
        
    def add_bayesian_parameter(self,parameter_name,bounds,round_digits=None):
        self.parameter_dict[parameter_name] = self.bayesian_placeholder_phrase
        self.bayesian_register_dict[parameter_name] = 1
        self.bayesian_options_bounds_low_dict[parameter_name] = bounds[0]
        self.bayesian_options_bounds_high_dict[parameter_name] = bounds[1]
        self.bayesian_options_round_digits_dict[parameter_name] = round_digits

    def register_parameter_set(self,ignore_duplicates=True):
        if ignore_duplicates == False:
            self.parameter_frame = self.parameter_frame.append(self.parameter_dict,ignore_index=True,verify_integrity=True)
            self.bayesian_register_frame = self.bayesian_register_frame.append(self.bayesian_register_dict,ignore_index=True,verify_integrity=True)
            self.bayesian_options_bounds_low_frame = self.bayesian_options_bounds_low_frame.append(self.bayesian_options_bounds_low_dict,ignore_index=True,verify_integrity=True)
            self.bayesian_options_bounds_high_frame = self.bayesian_options_bounds_high_frame.append(self.bayesian_options_bounds_high_dict,ignore_index=True,verify_integrity=True)
            self.bayesian_options_round_digits_frame = self.bayesian_options_round_digits_frame.append(self.bayesian_options_round_digits_dict,ignore_index=True,verify_integrity=True)
        else:
            dict_len = len(self.parameter_dict)
            duplicate_flag = False
            for index, row in self.parameter_frame.iterrows():
                if duplicate_flag == True:
                    break
                for i, key in enumerate(self.parameter_dict,start=1):
                    if self.parameter_dict[key] != row[key]:
                        break
                    else:
                        if i == dict_len:
                            duplicate_flag = True
            if duplicate_flag == False:
                self.parameter_frame = self.parameter_frame.append(self.parameter_dict,ignore_index=True,verify_integrity=True)
                self.bayesian_register_frame = self.bayesian_register_frame.append(self.bayesian_register_dict,ignore_index=True,verify_integrity=True)
                self.bayesian_options_bounds_low_frame = self.bayesian_options_bounds_low_frame.append(self.bayesian_options_bounds_low_dict,ignore_index=True,verify_integrity=True)
                self.bayesian_options_bounds_high_frame = self.bayesian_options_bounds_high_frame.append(self.bayesian_options_bounds_high_dict,ignore_index=True,verify_integrity=True)
                self.bayesian_options_round_digits_frame = self.bayesian_options_round_digits_frame.append(self.bayesian_options_round_digits_dict,ignore_index=True,verify_integrity=True)
                
        self.parameter_dict = {}
        self.bayesian_register_dict = {}
        self.bayesian_options_bounds_low_dict = {}
        self.bayesian_options_bounds_high_dict = {}
        self.bayesian_options_round_digits_dict = {}
        
        for par in self.data_types:
            self.parameter_frame[par] = self.parameter_frame[par].astype(self.data_types[par])

        self.parameter_frame.to_pickle(self.path_to_parameter_frame + '.pkl')
        with open(self.path_to_parameter_frame + '.txt','w') as f:
            f.write(self.parameter_frame.to_string())
        self.parameter_frame.to_csv(self.path_to_parameter_frame + '.csv',sep='\t',index=True,header=True)
        
        self.bayesian_register_frame.to_pickle(self.path_to_bayesian_register_frame + '.pkl')
        with open(self.path_to_bayesian_register_frame + '.txt','w') as f:
            f.write(self.bayesian_register_frame.to_string())
        self.bayesian_options_bounds_low_frame.to_pickle(self.path_to_bayesian_options_bounds_low_frame + '.pkl')
        with open(self.path_to_bayesian_options_bounds_low_frame + '.txt','w') as f:
            f.write(self.bayesian_options_bounds_low_frame.to_string())
        self.bayesian_options_bounds_high_frame.to_pickle(self.path_to_bayesian_options_bounds_high_frame + '.pkl')
        with open(self.path_to_bayesian_options_bounds_high_frame + '.txt','w') as f:
            f.write(self.bayesian_options_bounds_high_frame.to_string())
        self.bayesian_options_round_digits_frame.to_pickle(self.path_to_bayesian_options_round_digits_frame + '.pkl')
        with open(self.path_to_bayesian_options_round_digits_frame + '.txt','w') as f:
            f.write(self.bayesian_options_round_digits_frame.to_string())

            
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
            string = js.dumps(dict_i,separators=['\n','='])
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
        list_of_parameter_dicts_preview = self.parameter_frame.astype(object).to_dict(orient='records')
        for i in parameter_index_list_preview:
            parameter_dict_i = list_of_parameter_dicts_preview[i]
            string = js.dumps(parameter_dict_i,separators=['\n','='])
            #string = string.strip('{}')
            string = string[1:-1]
            for key in parameter_dict_i:
                string = string.replace("\"" + key + "\"",key)
            print('\nparameter set ' + str(i) + ':')
            self.loaded_preview_function(string)
    
    def start_execution(self):
        if self.parallelization == 'processes':
            from concurrent.futures import ProcessPoolExecutor as PoolExecutor
            from concurrent.futures import wait, as_completed
            with PoolExecutor(max_workers=4) as executor:
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
            from dask import compute, delayed
            DASK_MASTER_IP = os.environ['DASK_MASTER_IP']
            DASK_MASTER_PORT = os.environ['DASK_MASTER_PORT']
            with Client(DASK_MASTER_IP + ':' + DASK_MASTER_PORT, timeout='50s') as client:
                client.upload_file(self.repository_root_dir + '/parallel_hyperparameter_search/phs/utils.py')
                client.upload_file(self.repository_root_dir + '/parallel_hyperparameter_search/phs/bayes.py')
                client.upload_file(self.repository_root_dir + '/parallel_hyperparameter_search/phs/proxy.py')
                client.upload_file(self.custom_module_root_dir + '/' + self.custom_module_name + '.py')
                self.start_dask_execution_kernel(client, wait, as_completed)
                self.as_completed_functions(as_completed)
        
        #if 'final' in self.plot_modus and self.plots:
        #    print('\n',end='')
        #    self.refresh_plot(contour=True)
        return 1
                
    def start_processes_execution_kernel(self, executor, wait, as_completed):
        parameter_string_list = self.create_parameter_string_list()
        parameter_index_list = self.parameter_frame.index.values.tolist()
        paths={'swap_path':self.swap_path, 'path_to_bayesian_options_bounds_low_frame':self.path_to_bayesian_options_bounds_low_frame, 'path_to_bayesian_options_bounds_high_frame':self.path_to_bayesian_options_bounds_high_frame, 'path_to_bayesian_options_round_digits_frame':self.path_to_bayesian_options_round_digits_frame}
        
        list_of_parameter_dicts = self.parameter_frame.astype(object).to_dict(orient='records')
        for i in parameter_index_list:
            parameter_dict_i = list_of_parameter_dicts[i]
            auxiliary_information = {'save_path':self.worker_save_path, 'parameter_index':i}
            if self.bayesian_placeholder_phrase not in parameter_dict_i.values():
                self.sub_future.append(executor.submit(proxy.proxy_function, self.parallelization, self.custom_function, arg=parameter_dict_i, auxiliary_information=auxiliary_information))
            else:
                self.sub_future.append(executor.submit(proxy.proxy_function, self.parallelization, self.custom_function, arg=parameter_dict_i, auxiliary_information=auxiliary_information, with_bayesian=True, at_index=i, bayesian_placeholder_phrase=self.bayesian_placeholder_phrase, paths=paths, data_types=self.data_types))
        return 1
        
    def start_mpi_execution_kernel(self, executor, wait, as_completed):
        parameter_string_list = self.create_parameter_string_list()
        parameter_index_list = self.parameter_frame.index.values.tolist()
        paths={'swap_path':self.swap_path, 'path_to_bayesian_options_bounds_low_frame':self.path_to_bayesian_options_bounds_low_frame, 'path_to_bayesian_options_bounds_high_frame':self.path_to_bayesian_options_bounds_high_frame, 'path_to_bayesian_options_round_digits_frame':self.path_to_bayesian_options_round_digits_frame}
        
        list_of_parameter_dicts = self.parameter_frame.astype(object).to_dict(orient='records')
        for i in parameter_index_list:
            parameter_dict_i = list_of_parameter_dicts[i]
            auxiliary_information = {'save_path':self.worker_save_path, 'parameter_index':i}
            if self.bayesian_placeholder_phrase not in parameter_dict_i.values():
                self.sub_future.append(executor.submit(proxy.proxy_function, self.parallelization, self.custom_function, arg=parameter_dict_i, auxiliary_information=auxiliary_information))
            else:
                self.sub_future.append(executor.submit(proxy.proxy_function, self.parallelization, self.custom_function, arg=parameter_dict_i, auxiliary_information=auxiliary_information, with_bayesian=True, at_index=i, bayesian_placeholder_phrase=self.bayesian_placeholder_phrase, paths=paths, data_types=self.data_types))
        return 1
        
    def start_dask_execution_kernel(self, executor, wait, as_completed):
        parameter_string_list = self.create_parameter_string_list()
        parameter_index_list = self.parameter_frame.index.values.tolist()
        paths={'swap_path':self.swap_path, 'path_to_bayesian_options_bounds_low_frame':self.path_to_bayesian_options_bounds_low_frame, 'path_to_bayesian_options_bounds_high_frame':self.path_to_bayesian_options_bounds_high_frame, 'path_to_bayesian_options_round_digits_frame':self.path_to_bayesian_options_round_digits_frame}
        
        list_of_parameter_dicts = self.parameter_frame.astype(object).to_dict(orient='records')
        for i in parameter_index_list:
            parameter_dict_i = list_of_parameter_dicts[i]
            auxiliary_information = {'save_path':self.worker_save_path, 'parameter_index':i}
            if self.bayesian_placeholder_phrase not in parameter_dict_i.values():
                self.sub_future.append(executor.submit(proxy.proxy_function, self.parallelization, self.custom_function, arg=parameter_dict_i, auxiliary_information=auxiliary_information, priority=10, fifo_timeout='0ms'))
            else:
                self.sub_future.append(executor.submit(proxy.proxy_function, self.parallelization, self.custom_function, arg=parameter_dict_i, auxiliary_information=auxiliary_information, with_bayesian=True, at_index=i, bayesian_placeholder_phrase=self.bayesian_placeholder_phrase, paths=paths, data_types=self.data_types, priority=-10, fifo_timeout='0ms'))
        return 1
        
    def as_completed_functions(self, as_completed):
        for f in as_completed(self.sub_future):
            self.refresh_log()
            self.swap_files()
            self.monitor()
        return 1
    
    def refresh_log(self):
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
                self.log_frame.loc[i,'state'] = self.sub_future[i]._state
                if self.sub_future[i]._state == 'FINISHED':
                    self.log_frame.loc[i,'result'] = (self.sub_future[i].result())[0]
                    self.log_frame.loc[i,'started'] = (self.sub_future[i].result())[1]
                    self.log_frame.loc[i,'ended'] = (self.sub_future[i].result())[2]
                    self.log_frame.loc[i,'execution time'] = (self.sub_future[i].result())[2] - (self.sub_future[i].result())[1]
                    self.log_frame.loc[i,'worker'] = (self.sub_future[i]._result)[3]
                    if (self.sub_future[i].result())[0] < best:
                        best = (self.sub_future[i].result())[0]
                        best_i = i
                    if (self.sub_future[i].result())[4] != None:
                        bayesian_replacement_dict = self.sub_future[i].result()[4]
                        for col_name in bayesian_replacement_dict:
                            self.log_frame.loc[i,col_name] = bayesian_replacement_dict[col_name]
            elif self.parallelization == 'mpi':
                self.log_frame.loc[i,'state'] = self.sub_future[i]._state
                if self.sub_future[i]._state == 'FINISHED':
                    self.log_frame.loc[i,'result'] = (self.sub_future[i]._result)[0]
                    self.log_frame.loc[i,'started'] = (self.sub_future[i]._result)[1]
                    self.log_frame.loc[i,'ended'] = (self.sub_future[i]._result)[2]
                    self.log_frame.loc[i,'execution time'] = (self.sub_future[i]._result)[2] - (self.sub_future[i]._result)[1]
                    self.log_frame.loc[i,'worker'] = (self.sub_future[i]._result)[3]
                    if (self.sub_future[i]._result)[0] < best:
                        best = (self.sub_future[i]._result)[0]
                        best_i = i
                    if (self.sub_future[i]._result)[4] != None:
                        bayesian_replacement_dict = self.sub_future[i]._result[4]
                        for col_name in bayesian_replacement_dict:
                            self.log_frame.loc[i,col_name] = bayesian_replacement_dict[col_name]
            elif self.parallelization == 'dask':
                self.log_frame.loc[i,'state'] = self.sub_future[i].status
                if self.sub_future[i].status == 'finished' or self.sub_future[i].status == 'error':
                    self.log_frame.loc[i,'result'] = (self.sub_future[i].result())[0]
                    self.log_frame.loc[i,'started'] = (self.sub_future[i].result())[1]
                    self.log_frame.loc[i,'ended'] = (self.sub_future[i].result())[2]
                    self.log_frame.loc[i,'execution time'] = (self.sub_future[i].result())[2] - (self.sub_future[i].result())[1]
                    self.log_frame.loc[i,'worker'] = (self.sub_future[i].result())[3]
                    if (self.sub_future[i].result())[0] < best:
                        best = (self.sub_future[i].result())[0]
                        best_i = i
                    if (self.sub_future[i].result())[4] != None:
                        bayesian_replacement_dict = self.sub_future[i].result()[4]
                        for col_name in bayesian_replacement_dict:
                            self.log_frame.loc[i,col_name] = bayesian_replacement_dict[col_name]
        if best_i != -1:
            self.log_frame.loc[best_i,'best'] = self.symbol_for_best
        self.log_frame = self.log_frame.applymap(lambda x: round(x, 4) if isinstance(x, (int, float)) else x)
        with open(self.log_path + '/log_frame.txt','w') as f:
            f.write(self.log_frame.to_string())
        
        print('\nrefresh log:\t%.3f' %(time.time()-start_time), end='\t')
        return 1
    
    def swap_files(self):
        start_time = time.time()
        i=1
        current_folder = None
        while True:
            current_folder = self.swap_path + '/' + str(i).zfill(5)
            if os.path.exists(current_folder) and os.path.isdir(current_folder):
                i = i + 1
            else:
                break
        os.mkdir(current_folder)
        self.log_frame.to_pickle(current_folder + '/log_frame.pkl')
        self.parameter_frame.to_pickle(current_folder + '/parameter_frame.pkl')
        with open(current_folder + '/log_frame.txt','w') as f:
            f.write(self.log_frame.to_string())
        print('swap files:\t%.3f' %(time.time()-start_time), end='\t')
        return 1
        
    def monitor(self):
        start_time = time.time()
        for monitor_function_string in self.monitor_func_name_with_args:
            kwargs_dict = self.monitor_func_name_with_args[monitor_function_string]
            kwargs_dict['monitor_path'] = self.monitor_path
            kwargs_dict['swap_path'] = self.swap_path
            self.monitor_functions_dict[monitor_function_string](**kwargs_dict)
        
        print('refresh plot:\t%.3f' %(time.time()-start_time), end='\t')
        return 1