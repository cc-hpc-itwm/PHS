import os


def find_current_folder(swap_path):
    folder_list = next(os.walk(swap_path))[1]
    folder_list.sort()
    current_folder = swap_path + '/' + folder_list[-1]
    return current_folder
