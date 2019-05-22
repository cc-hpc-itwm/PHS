import os
import time
import numpy as np

RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"

def progress_bar(
    progress,
    total,
    start_time = None,
    bar_width = 20,
    prog_sign = '=',
    left_border='[',
    right_border=']',
    sep='|',
    prog_color=YELLOW,
    total_color=GREEN,
    time_color=BLUE):

    if progress != total:
        end = '\r'
    else:
        end = ''

    if start_time is not None:
        elapsed_time =time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    else:
        elapsed_time = ''
    finished_portion = progress/total
    percent = int(finished_portion * 100)
    prog = int(round(bar_width * finished_portion)) * prog_sign
    print('{total_color}{left_border}{prog_color}{prog:<{bar_width}}{total_color}{right_border}{reset} {sep} {prog_color}{percent:>3}%{reset} {sep} {prog_color}{progress:>5}{reset} of {total_color}{total:>6}{reset} {sep} {time_color}{elapsed_time:>10}{reset}'
                                                                        .format(
                                                                            total_color=total_color,
                                                                            left_border=left_border,
                                                                            prog_color = prog_color,
                                                                            prog=prog,
                                                                            bar_width=bar_width,
                                                                            reset=RESET,
                                                                            right_border=right_border,
                                                                            sep=sep,
                                                                            percent=percent,
                                                                            progress=progress,
                                                                            total=total,
                                                                            time_color=time_color,
                                                                            elapsed_time=elapsed_time),
                                                                        end=end)




if __name__ == '__main__':
    total=100
    for count in range(1, total+1):
        time.sleep(0.05)
        progress_bar(progress=count, total=total)