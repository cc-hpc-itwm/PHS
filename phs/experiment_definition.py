import time
import os
import pandas as pd
import json as js
import importlib
import sys
import pickle
from contextlib import redirect_stdout
from shutil import copy2

import phs.proxy
import phs.bayes
import phs.utils
import phs.utils_parameter_io
import phs.global_names
import phs.utils_tree


class ExperimentDefinition:
    """ """

    def __init__(self,
                 parameter_definitions=None,
                 parameter_definitions_root_dir_in=False,
                 **kwargs_dict):

        phs.utils.print_section(header='ExperimentDefinition')
        if 'config_json_path' in kwargs_dict:
            with open(kwargs_dict['config_json_path']) as f:
                config_dict = js.load(f)
        else:
            config_dict = kwargs_dict

        if parameter_definitions is not None:
            (self.parameter_frame,
             self.bayesian_register_frame,
             self.bayesian_options_bounds_low_frame,
             self.bayesian_options_bounds_high_frame,
             self.data_types_ordered_list) = parameter_definitions

            print('\t{0:40}{1:}\n'.format('parameter definition', 'inline'))
        elif parameter_definitions_root_dir_in is not False:
            self.parameter_definitions_root_dir_in = parameter_definitions_root_dir_in

            (self.parameter_frame,
             self.bayesian_register_frame,
             self.bayesian_options_bounds_low_frame,
             self.bayesian_options_bounds_high_frame,
             self.data_types_ordered_list) = phs.utils_parameter_io.load_parameter_definitions(
                import_path=self.parameter_definitions_root_dir_in)

            print('\t{0:40}{1:}\n'.format('parameter definition imported from',
                                          parameter_definitions_root_dir_in))
        else:
            raise ValueError('no parameter definitions provided.')

        self.experiment_dir = config_dict['experiment_dir']
        self.target_module_root_dir = config_dict['target_module_root_dir']
        self.target_module_name = config_dict['target_module_name']
        self.target_function_name = config_dict['target_function_name']

        for key, value in config_dict.items():
            print('\t{0:40}{1:}'.format(key, value))

        glob = phs.global_names.GlobalNames()
        self.result_path = glob.get_lev1_res(self.experiment_dir)
        self.parameter_definitions_root_dir_out = glob.get_lev1_par(self.experiment_dir)
        self.source_code_target = glob.get_lev1_source(self.experiment_dir)

        if os.path.exists(self.experiment_dir) and os.path.isdir(self.experiment_dir):
            phs.utils.format_stderr()
            raise ValueError('\n\ndirectory ' + self.experiment_dir +
                             ' already exists. Please choose a different experiment directory.\n\n')
        else:
            os.mkdir(self.experiment_dir)
            os.mkdir(self.result_path)
            os.mkdir(self.parameter_definitions_root_dir_out)
            os.mkdir(self.source_code_target)

            with open(self.source_code_target + '/func_name.txt', 'w') as f:
                f.write(self.target_function_name)

        # copy target function to experiment folder
        copy2(self.target_module_root_dir + '/' + self.target_module_name +
              '.py', self.source_code_target + '/' + self.target_module_name + '.py')

        # save parameter definitions to experiment folder
        phs.utils_parameter_io.save_parameter_definitions(
            export_path=self.parameter_definitions_root_dir_out,
            parameter_frame=self.parameter_frame,
            bayesian_register_frame=self.bayesian_register_frame,
            bayesian_options_bounds_low_frame=self.bayesian_options_bounds_low_frame,
            bayesian_options_bounds_high_frame=self.bayesian_options_bounds_high_frame,
            data_types_ordered_list=self.data_types_ordered_list)

        phs.utils.print_subsection(header='DirectoryLayout')
        phs.utils_tree.print_dir_tree(self.experiment_dir)
