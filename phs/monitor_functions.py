import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from matplotlib import cm, colors, gridspec
from matplotlib.mlab import griddata
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.patches import ConnectionPatch

import utils


def plot_3d(first, second, third, name, monitor_path, swap_path, contour=False):
    save_dir = monitor_path + '/' + name
    current_folder = utils.find_current_folder(swap_path)
    current_log_frame = pd.read_pickle(current_folder + '/log_frame.pkl')
    bayesian_register_frame = pd.read_pickle(swap_path + '/bayesian_register_frame.pkl')

    plt.switch_backend('agg')
    plt.ioff()
    data_1_list = []
    data_2_list = []
    data_3_list = []
    i_list = []
    marker_flag = []
    marker_no_bayes = 'o'
    marker_bayes = '+'
    parameter_index_list = current_log_frame.index.values.tolist()
    for i in parameter_index_list:
        if current_log_frame.loc[i, 'result'] != None:
            data_1 = current_log_frame.loc[i, first]
            data_1_list.append(data_1)
            data_2 = current_log_frame.loc[i, second]
            data_2_list.append(data_2)
            data_3 = current_log_frame.loc[i, third]
            data_3_list.append(data_3)
            i_list.append(i)
            if (first != 'result' and bayesian_register_frame.loc[i, first] == 1) or\
                (second != 'result' and bayesian_register_frame.loc[i, second] == 1) or\
                    (third != 'result' and bayesian_register_frame.loc[i, third] == 1):
                marker_flag.append('bayes')
            else:
                marker_flag.append('no bayes')
    if data_1_list:
        indices_bayes = [i for i, x in enumerate(marker_flag) if x == 'bayes']
        indices_no_bayes = [i for i, x in enumerate(marker_flag) if x == 'no bayes']
        data_1_list = np.array(data_1_list)
        data_2_list = np.array(data_2_list)
        data_3_list = np.array(data_3_list)
        data_1_list_no_bayes = data_1_list[indices_no_bayes]
        data_2_list_no_bayes = data_2_list[indices_no_bayes]
        data_3_list_no_bayes = data_3_list[indices_no_bayes]
        data_1_list_bayes = data_1_list[indices_bayes]
        data_2_list_bayes = data_2_list[indices_bayes]
        data_3_list_bayes = data_3_list[indices_bayes]
        index_best = np.argmin(data_3_list)
        data_1_best = data_1_list[index_best]
        data_2_best = data_2_list[index_best]
        data_3_best = data_3_list[index_best]
        if index_best in indices_bayes:
            marker_best = marker_bayes
        else:
            marker_best = marker_no_bayes

        data_3_list_min = min(data_3_list)
        data_3_list_max = max(data_3_list)
        colormap = cm.jet

        fig_2d = plt.figure(figsize=(10, 10))
        ax_2d = fig_2d.add_subplot(1, 1, 1)
        ax_2d.scatter(data_1_best, data_2_best, s=250,
                      edgecolors="k", facecolors='none', marker='o')
        ax_2d.scatter(data_1_list_no_bayes, data_2_list_no_bayes, c=data_3_list_no_bayes,
                      marker=marker_no_bayes, cmap=colormap, vmin=data_3_list_min, vmax=data_3_list_max)
        img_2d = ax_2d.scatter(data_1_list_bayes, data_2_list_bayes, c=data_3_list_bayes,
                               marker=marker_bayes, cmap=colormap, vmin=data_3_list_min, vmax=data_3_list_max)
        for a, b, d in zip(data_1_list, data_2_list, i_list):
            ax_2d.text(a, b, d)
        divider = make_axes_locatable(ax_2d)
        cax1 = divider.append_axes("right", size="5%", pad=0.05)
        cbar_2d = fig_2d.colorbar(img_2d, cax=cax1)
        cbar_2d.set_label(third)
        ax_2d.set_xlabel(first)
        ax_2d.set_ylabel(second)
        fig_2d.savefig(save_dir + '.png', bbox_inches='tight')
        fig_2d.savefig(save_dir + '.pdf', bbox_inches='tight')

        string_in_data = False
        for val in data_1_list:
            if isinstance(val, str):
                string_in_data = True
                break
        if not string_in_data:
            for val in data_2_list:
                if isinstance(val, str):
                    string_in_data = True
                    break
        if not string_in_data:
            for val in data_3_list:
                if isinstance(val, str):
                    string_in_data = True
                    break

        if contour and not string_in_data:
            tricontour_levels = np.linspace(min(data_3_list), max(data_3_list), num=10)
            tricontour_levels = tricontour_levels[1:-1]
            ax_2d.tricontour(data_1_list, data_2_list, data_3_list,
                             levels=tricontour_levels, linewidths=1, cmap=colormap)
            fig_2d.savefig(save_dir+'_contour' + '.png', bbox_inches='tight')
            fig_2d.savefig(save_dir+'_contour' + '.pdf', bbox_inches='tight')
        plt.close(fig_2d)
    return 1

    '''if not string_in_data:
            fig_3d = plt.figure(figsize=(10,10))
            ax_3d = fig_3d.add_subplot(1,1,1,projection='3d')
            ax_3d.scatter(data_1_list_no_bayes,data_2_list_no_bayes,data_3_list_no_bayes,c=data_3_list_no_bayes,marker='o', cmap=colormap,vmin=data_3_list_min, vmax=data_3_list_max)
            ax_3d_scatter = ax_3d.scatter(data_1_list_bayes,data_2_list_bayes,data_3_list_bayes,c=data_3_list_bayes,marker='+', cmap=colormap,vmin=data_3_list_min, vmax=data_3_list_max)
            for a,b,c,d in zip(data_1_list,data_2_list,data_3_list,i_list):
                ax_3d.text(a,b,c,d)
            cbar_3d = fig_3d.colorbar(ax_3d_scatter)
            cbar_3d.set_label(third)
            ax_3d.set_xlabel(first)
            ax_3d.set_ylabel(second)
            fig_3d.savefig(save_dir+'_3d' + '.png', bbox_inches='tight')
            fig_3d.savefig(save_dir+'_3d' + '.pdf', bbox_inches='tight')
            plt.close(fig_3d)'''


def create_worker_timeline(name, monitor_path, swap_path):
    save_dir = monitor_path + '/' + name
    current_folder = utils.find_current_folder(swap_path)
    current_log_frame = pd.read_pickle(current_folder + '/log_frame.pkl')

    plt.switch_backend('agg')
    plt.ioff()
    fig = plt.figure(figsize=(10, 2))
    ax = fig.add_subplot(1, 1, 1)
    parameter_index_list = current_log_frame.index.values.tolist()
    empty = True
    for i in parameter_index_list:
        if not math.isnan(current_log_frame.loc[i, 'result']):
            empty = False
            worker = str(current_log_frame.loc[i, 'worker'])
            started = current_log_frame.loc[i, 'started']
            ended = current_log_frame.loc[i, 'ended']
            ax.hlines(y=worker, xmin=started, xmax=ended, color='b')
            ax.scatter(started, worker, marker='^', c='g')
            ax.scatter(ended, worker, marker='v', c='r')
    if not empty:
        ax.set_xlabel('time')
        # ax.set_ylabel('')
        fig.savefig(save_dir + '.png', bbox_inches='tight')
        fig.savefig(save_dir + '.pdf', bbox_inches='tight')
    plt.close()
    return 1


def create_parameter_combination(name, monitor_path, swap_path):
    save_dir = monitor_path + '/' + name
    current_folder = utils.find_current_folder(swap_path)
    current_log_frame = pd.read_pickle(current_folder + '/log_frame.pkl')
    parameter_frame = pd.read_pickle(swap_path + '/parameter_frame.pkl')
    bayesian_register_frame = pd.read_pickle(swap_path + '/bayesian_register_frame.pkl')

    index_string = 'index'
    parameter_names = []
    parameter_names.append(index_string)
    for n in parameter_frame.columns.values.tolist():
        parameter_names.append(n)

    parameter_values = []
    parameter_result = []
    marker = []
    parameter_index_list = current_log_frame.index.values.tolist()
    for i in parameter_index_list:
        if not math.isnan(current_log_frame.loc[i, 'result']):
            parameter_result.append(current_log_frame.loc[i, 'result'])
        else:
            parameter_result.append('no_result_yet')
        for name_j in parameter_names:
            parameter_values.append([])
            marker.append([])
            if name_j == index_string:
                parameter_values[i].append(i)
                marker[i].append('d')
            else:
                parameter_values[i].append(current_log_frame.loc[i, name_j])
                if bayesian_register_frame.loc[i, name_j] == 0:
                    marker[i].append('o')
                else:
                    marker[i].append('+')
    to_delete = []
    for i in parameter_index_list:
        if parameter_result[i] == 'no_result_yet':
            to_delete.append(i)
    for index in sorted(to_delete, reverse=True):
        del parameter_result[index]
        del parameter_values[index]
        del marker[index]

    rgba_color = []
    norm = colors.Normalize(vmin=min(parameter_result), vmax=max(parameter_result))
    index_best = np.argmin(np.array(parameter_result))
    for i in parameter_result:
        rgba_color.append(cm.jet(norm(i)))

    plt.switch_backend('agg')
    plt.ioff()
    fig = plt.figure(figsize=(10, 2*len(parameter_names)))
    gs = gridspec.GridSpec(len(parameter_names), 1)
    gs.update(wspace=0.025, hspace=4.5)
    ax = []
    for i, name_j in enumerate(parameter_names):
        ax.append(plt.subplot(gs[i]))
        ax[i].set_ylabel(parameter_names[i])
        ax[i].set_yticks([])

    for i, set_i in enumerate(parameter_values):
        if i == index_best:
            for j, par_j in enumerate(set_i):
                ax[j].plot(par_j, 0, marker='o', markersize=15, markeredgecolor="k",
                           markerfacecolor='None', markeredgewidth=2)
        for j, par_j in enumerate(set_i):
            ax[j].plot(par_j, 0, marker=marker[i][j], color=rgba_color[i])
        for j, par_j in enumerate(set_i[0:-1]):
            xyA = (set_i[j], 0)
            xyB = (set_i[j+1], 0)
            con = ConnectionPatch(xyB, xyA, coordsA="data", coordsB="data",
                                  axesA=ax[j+1], axesB=ax[j], color=rgba_color[i])
            ax[j+1].add_artist(con)
    fig.savefig(save_dir + '.png', bbox_inches='tight')
    fig.savefig(save_dir + '.pdf', bbox_inches='tight')
    plt.close()
    return 1
