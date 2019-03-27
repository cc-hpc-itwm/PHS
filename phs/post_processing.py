from phs import utils
from phs import monitor_functions
import os
import pandas as pd
import imageio
import pickle


class PostProcessing:
    def __init__(self, experiment_dir):
        utils.print_section(header='PostProcessing')
        self.experiment_dir = experiment_dir
        self.result_frame_path_in = self.experiment_dir + '/results/result_frame'
        self.path_in_to_data_types_ordered_list = self.experiment_dir + \
            '/parameter_definitions/data_types_ordered_list'
        self.path_in_to_data_types_additional_information_dict = self.experiment_dir + \
            '/parameter_definitions/data_types_additional_information_dict'
        self.additional_information_frame_path_in = self.experiment_dir + '/results/additional_information_frame'
        self.post_processing_path_out = self.experiment_dir + '/post_processing'

        with open(self.path_in_to_data_types_ordered_list + '.pkl', 'rb') as f:
            self.data_types_ordered_list = pickle.load(f)
        with open(self.path_in_to_data_types_additional_information_dict + '.pkl', 'rb') as f:
            self.data_types_additional_information_dict = pickle.load(f)

        result_dtypes_dict = {}
        for tuple_i in self.data_types_ordered_list:
            result_dtypes_dict[tuple_i[0]] = tuple_i[1]

        self.result_frame = pd.read_csv(self.result_frame_path_in + '.csv', index_col=0)
        self.additional_information_frame = pd.read_csv(
            self.additional_information_frame_path_in + '.csv', index_col=0)
        self.path_to_bayesian_register_frame = self.experiment_dir + \
            '/parameter_definitions/bayesian_register_frame'

        if not os.path.isdir(self.experiment_dir):
            raise ValueError('directory ' + self.experiment_dir + ' doesn\'t exist.')
        else:
            if not os.path.isdir(self.post_processing_path_out):
                os.mkdir(self.post_processing_path_out)

        # print(self.result_frame)
        # print(self.additional_information_frame)
        # print(type(self.additional_information_frame['worker'].values))
        # print(type(self.additional_information_frame['started'].values.tolist()))
        # print(type(self.additional_information_frame['ended'].values.tolist()))

    def result_evolution(self, name):
        monitor_functions.result_evolution(name=name,
                                           path_out=self.post_processing_path_out,
                                           result_frame=self.result_frame,
                                           path_to_bayesian_register_frame=self.path_to_bayesian_register_frame)

    def plot_3d(self,
                name,
                first,
                second,
                third,
                contour=False,
                animated=False,
                animated_step_size=1,
                animated_fps=2):
        if not animated:
            monitor_functions.plot_3d(name=name,
                                      path_out=self.post_processing_path_out,
                                      first=first,
                                      second=second,
                                      third=third,
                                      result_frame=self.result_frame,
                                      path_to_bayesian_register_frame=self.path_to_bayesian_register_frame,
                                      contour=contour,
                                      animated=animated)
        else:
            index_len = len(self.result_frame.index.values.tolist())
            loop_i = index_len//animated_step_size
            remainder = index_len % animated_step_size
            image_plain_list = []
            image_contour_list = []
            index_list = []
            for i in range(1, loop_i + 2):
                if i == loop_i + 1:
                    if remainder != 0:
                        index_list_complete = [j for j in range(index_list[-1] + 1, index_len)]
                        index_list.extend(index_list_complete)
                    else:
                        break
                else:
                    index_list = [j for j in range(i * animated_step_size)]
                result_frame_until_index = self.result_frame.loc[index_list, :]
                image_dict_return = monitor_functions.plot_3d(name=name,
                                                              path_out=self.post_processing_path_out,
                                                              first=first,
                                                              second=second,
                                                              third=third,
                                                              result_frame=result_frame_until_index,
                                                              path_to_bayesian_register_frame=self.path_to_bayesian_register_frame,
                                                              contour=contour,
                                                              animated=animated)

                image_plain_list.append(image_dict_return['plain'])
                # just use '... .mp4' for mp4 export
                writer = imageio.get_writer(
                    self.post_processing_path_out + '/' + name + '.gif', fps=animated_fps, mode='I', subrectangles=True)
                for frame in image_plain_list:
                    writer.append_data(frame)
                writer.close()

                if contour and len(index_list) >= 3:
                    image_contour_list.append(image_dict_return['contour'])
                    # just use '... .mp4' for mp4 export
                    writer = imageio.get_writer(
                        self.post_processing_path_out + '/' + name + '_contour' + '.gif', fps=animated_fps, mode='I', subrectangles=True)
                    for frame in image_contour_list:
                        writer.append_data(frame)
                    writer.close()

    def create_worker_timeline(self, name):
        monitor_functions.create_worker_timeline(name=name,
                                                 path_out=self.post_processing_path_out,
                                                 additional_information_frame=self.additional_information_frame)

    def create_parameter_combination(self, name):
        monitor_functions.create_parameter_combination(name=name,
                                                       path_out=self.post_processing_path_out,
                                                       result_frame=self.result_frame,
                                                       additional_information_frame=self.additional_information_frame,
                                                       path_to_bayesian_register_frame=self.path_to_bayesian_register_frame)
