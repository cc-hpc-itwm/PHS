import os

def find_current_folder(swap_path):
    i=1
    current_folder = None
    while True:
        current_folder = swap_path + '/' + str(i).zfill(5)
        if os.path.exists(current_folder) and os.path.isdir(current_folder):
            i = i + 1
        else:
            break
    current_folder = swap_path + '/' + str(i-1).zfill(5)
    return current_folder