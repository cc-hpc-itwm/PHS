import os
import time
import numpy as np
import pandas as pd

def append_result(index, parameter_dict, result_col_name, result, file_path, lock_result_path):
        """

        Parameters
        ----------
        index :


        Returns
        -------

        """
        single_result_dict = parameter_dict # dicts are ordered in python 3.7+. The order was set in parameter_definition.py
        single_result_dict[result_col_name] = result
        single_result_df = pd.DataFrame(single_result_dict, index=[index]) # column order is taken over from dict key order

        '''self.result_frame = self.result_frame.append(
            current_result_df, ignore_index=False, verify_integrity=False)

        # self.result_frame = self.result_frame.applymap(
        #     lambda x: round(x, 4) if isinstance(x, (int, float)) else x)'''
        while True:
            try:
                os.mkdir(lock_result_path)
                break
            except OSError:
                # print('write locked')
                time.sleep(0.1)
                continue

        with open(file_path, 'a') as f:
            single_result_df.to_csv(f, header=False, index=True)

        if os.path.exists(lock_result_path) and os.path.isdir(lock_result_path):
            os.rmdir(lock_result_path)

        return 1
