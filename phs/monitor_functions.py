import numpy as np
import pandas as pd
import os
import pickle
import time
import imageio
import matplotlib.pyplot as plt
from matplotlib import cm, colors, gridspec
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.patches import ConnectionPatch


def result_evolution(name,
                     path_out,
                     result_frame,
                     path_to_bayesian_register_frame,
                     **not_used_kwargs):

    start_time = time.time()
    save_dir = path_out + '/' + name

    current_result_frame = result_frame
    bayesian_register_frame = pd.read_pickle(path_to_bayesian_register_frame + '.pkl')

    x = current_result_frame.index.values
    y = current_result_frame['result'].values

    plt.switch_backend('agg')
    plt.ioff()
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)

    for i in current_result_frame.index.values:
        x = i
        y = current_result_frame.at[i, 'result']
        if any(bayesian_register_frame.loc[i]):
            marker = '+'
            color = 'r'
        else:
            marker = 'o'
            color = 'b'
        ax.scatter(x, y, color=color, marker=marker)
    ax.set_xlabel('parameter set')
    ax.set_ylabel('result')
    plt.xlim(left=0)
    plt.grid(True)
    fig.savefig(save_dir + '.png', bbox_inches='tight')
    fig.savefig(save_dir + '.pdf', bbox_inches='tight')
    plt.close()

    return 1


def plot_3d(name,
            path_out,
            first,
            second,
            third,
            result_frame,
            path_to_bayesian_register_frame,
            contour=False,
            animated=False,
            **not_used_kwargs):
    start_time = time.time()
    save_dir = path_out + '/' + name

    current_log_frame = result_frame
    bayesian_register_frame = pd.read_pickle(path_to_bayesian_register_frame + '.pkl')

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

        fig_2d = plt.figure(figsize=(10.08, 10.08))
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
        if not animated:
            fig_2d.savefig(save_dir + '.png', dpi=100)
            # fig_2d.savesfig(save_dir + '.pdf', dpi=100)
        else:
            fig_2d.canvas.draw()
            # Get the RGBA buffer from the figure
            w, h = fig_2d.canvas.get_width_height()
            buf_plain = np.fromstring(fig_2d.canvas.tostring_argb(), dtype=np.uint8)
            buf_plain.shape = (w, h, 4)
            # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
            buf_plain = np.roll(buf_plain, 3, axis=2)
            frame_array_dict_return = {}
            frame_array_dict_return['plain'] = buf_plain

        if contour and len(data_1_list) >= 3:
            tricontour_levels = np.linspace(min(data_3_list), max(data_3_list), num=10)
            tricontour_levels = tricontour_levels[1:-1]
            ax_2d.tricontour(data_1_list, data_2_list, data_3_list,
                             levels=tricontour_levels, linewidths=1, cmap=colormap)
            if not animated:
                fig_2d.savefig(save_dir + '_contour' + '.png', dpi=100)
                # fig_2d.savefig(save_dir+'_contour' + '.pdf', dpi=100)
                # with open(save_dir + '_contour' + '.pkl', 'wb') as f:
                #     pickle.dump(fig_2d, f)
            else:
                fig_2d.canvas.draw()
                # Get the RGBA buffer from the figure
                w, h = fig_2d.canvas.get_width_height()
                buf_contour = np.fromstring(fig_2d.canvas.tostring_argb(), dtype=np.uint8)
                buf_contour.shape = (w, h, 4)
                # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
                buf_contour = np.roll(buf_contour, 3, axis=2)
                frame_array_dict_return['contour'] = buf_contour

        plt.close(fig_2d)
        # print('plot_3d:\t%.3f' % (time.time()-start_time), end='\n')

    if not animated:
        return 1
    else:
        return frame_array_dict_return

    '''if not string_in_data:
            fig_3d = plt.figure(figsize=(10,10))
            ax_3d = fig_3d.add_subplot(1,1,1,projection='3d')
            ax_3d.scatter(data_1_list_no_bayes,data_2_list_no_bayes,data_3_list_no_bayes,
                          c=data_3_list_no_bayes,marker='o', cmap=colormap,vmin=data_3_list_min, vmax=data_3_list_max)
            ax_3d_scatter = ax_3d.scatter(data_1_list_bayes,data_2_list_bayes,data_3_list_bayes,
                                          c=data_3_list_bayes,marker='+', cmap=colormap,vmin=data_3_list_min, vmax=data_3_list_max)
            for a,b,c,d in zip(data_1_list,data_2_list,data_3_list,i_list):
                ax_3d.text(a,b,c,d)
            cbar_3d = fig_3d.colorbar(ax_3d_scatter)
            cbar_3d.set_label(third)
            ax_3d.set_xlabel(first)
            ax_3d.set_ylabel(second)
            fig_3d.savefig(save_dir+'_3d' + '.png', bbox_inches='tight')
            fig_3d.savefig(save_dir+'_3d' + '.pdf', bbox_inches='tight')
            plt.close(fig_3d)'''


def create_worker_timeline(name,
                           path_out,
                           additional_information_frame,
                           **not_used_kwargs):
    start_time = time.time()
    save_dir = path_out + '/' + name

    plt.switch_backend('agg')
    plt.ioff()
    fig = plt.figure(figsize=(10, 2))
    ax = fig.add_subplot(1, 1, 1)

    index = additional_information_frame.index.values
    worker = additional_information_frame['worker'].values
    started = pd.to_datetime(additional_information_frame['started'].values)
    ended = pd.to_datetime(additional_information_frame['ended'].values)
    ax.hlines(y=worker, xmin=started, xmax=ended, color='b')
    index_string_list = [",".join(item) for item in index.astype(str)]
    for i in index:
        ax.text(started[i], worker[i], str(i), verticalalignment='bottom')
    ax.scatter(started, worker, marker='^', c='g')
    ax.scatter(ended, worker, marker='v', c='r')
    ax.set_xlabel('time')
    # ax.set_ylabel('')
    fig.savefig(save_dir + '.png', bbox_inches='tight')
    fig.savefig(save_dir + '.pdf', bbox_inches='tight')
    plt.close()
    # print('create_worker_timeline:\t%.3f' % (time.time()-start_time), end='\n')
    return 1


def create_parameter_combination(name,
                                 path_out,
                                 result_frame,
                                 additional_information_frame,
                                 path_to_bayesian_register_frame,
                                 **not_used_kwargs):
    start_time = time.time()
    save_dir = path_out + '/' + name

    bayesian_register_frame = pd.read_pickle(path_to_bayesian_register_frame + '.pkl')

    index_string = 'index'
    col_names = []
    col_names.append(index_string)
    col_names.extend(bayesian_register_frame.columns.values.tolist())

    parameter_values = []
    marker = []
    parameter_index_list = result_frame.index.values.tolist()
    for i, index in enumerate(parameter_index_list):
        for name_j in col_names:
            parameter_values.append([])
            marker.append([])
            if name_j == index_string:
                parameter_values[i].append(index)
                marker[i].append('d')
            else:
                parameter_values[i].append(result_frame.loc[index, name_j])
                if bayesian_register_frame.loc[i, name_j] == 0:
                    marker[i].append('o')
                else:
                    marker[i].append('+')

    result = result_frame['result'].values

    rgba_color = []
    norm = colors.Normalize(vmin=min(result), vmax=max(result))
    index_best = np.argmin(np.array(result))
    for i in result:
        rgba_color.append(cm.jet(norm(i)))

    plt.switch_backend('agg')
    plt.ioff()
    fig = plt.figure(figsize=(10, 2*len(col_names)))
    gs = gridspec.GridSpec(len(col_names), 1)
    gs.update(wspace=0.025, hspace=4.5)
    ax = []
    for i, name_j in enumerate(col_names):
        ax.append(plt.subplot(gs[i]))
        ax[i].set_ylabel(col_names[i])
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
    # print('create_parameter_combination:\t%.3f' % (time.time()-start_time), end='\n')
    return 1
