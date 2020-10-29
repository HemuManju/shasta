from pathlib import Path
import yaml
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import deepdish as dd

config_path = Path(__file__).parents[1] / 'hsi/config/simulation_config.yml'
config = yaml.load(open(str(config_path)), Loader=yaml.SafeLoader)


def plot_cpu_memory_profile(config):

    df = pd.DataFrame(columns=[
        'World size', 'No. UAV + UGV', 'Headless', 'CPU Usage (%)',
        'Memory Usage (MB)', 'Memory Usage (%)', 'Speedup'
    ])

    values = []
    df_temp = pd.DataFrame(columns=[
        'world_size', 'uav + ugv', 'headless', 'cpu', 'memory',
        'memory_percent', 'speed_up'
    ])
    temp = None
    for i in range(5):
        read_path = config['log_path'] + 'cpu_memory_profile_exp_' + str(
            i + 1) + '.csv'
        temp = pd.read_csv(read_path)
        df_temp = pd.concat((df_temp, temp), ignore_index=True)
        values.append(temp[['cpu', 'memory', 'memory_percent',
                            'speed_up']].values)

    # Rename columns
    df_temp = df_temp.rename(
        columns={
            'world_size': 'World size',
            'uav + ugv': 'No. UAV + UGV',
            'headless': 'Headless',
            'cpu': 'CPU Usage (%)',
            'memory': 'Memory Usage (MB)',
            'memory_percent': 'Memory Usage (%)',
            'speed_up': 'Speedup'
        })

    # Stack them
    values = np.dstack(values)
    # Main dataframe
    df[['World size', 'No. UAV + UGV',
        'Headless']] = temp[['world_size', 'uav + ugv', 'headless']]
    df[['CPU Usage (%)', 'Memory Usage (MB)', 'Memory Usage (%)',
        'Speedup']] = np.mean(values, axis=-1)
    df[[
        'CPU Usage (%) std', 'Memory Usage (MB) std', 'Memory Usage (%) std',
        'Speedup std'
    ]] = np.std(values, axis=-1)

    # Save them
    df.to_csv('cpu_memory_profiles.csv', index=False)

    plt.style.use('clean_box')
    names = {
        'cpu': 'CPU Usage (%)',
        'memory': 'Memory Usage (MB)',
        'speed_up': 'Speedup'
    }
    for key in names.keys():
        ax = sns.catplot(x='No. UAV + UGV',
                         y=names[key],
                         ci='sd',
                         hue='World size',
                         col='Headless',
                         data=df_temp,
                         kind="bar",
                         height=4.0,
                         aspect=1.25,
                         legend_out=False,
                         edgecolor=".2",
                         capsize=0.1,
                         errwidth=1.5,
                         palette='Greys',
                         legend=False,
                         facet_kws={'despine': False})
        for item in ax.axes:
            item[0].grid()
        plt.grid()
        plt.legend(title='World size', loc='upper right', prop={'size': 14})
        plt.tight_layout()
        file_name = 'reports/images/' + key + '.pdf'
        save_path = Path(__file__).parents[1] / file_name
        plt.savefig(save_path)
    plt.show()


plot_cpu_memory_profile(config)


def describe_helper(series):
    splits = str(series.describe()[['mean', 'std', 'max']]).split()
    keys, values = "", ""
    for i in range(0, len(splits) - 2, 2):
        keys += "{:8}\n".format(splits[i] + ':')
        values += "{:>8}\n".format(splits[i + 1])
    return keys, values


def plot_time_delays(config):
    # Read the data
    data = dd.io.load('data/interim/time_offset_exp_0_dataset.h5')

    plt.style.use('clean_box')
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(10, 3))
    streams = ['eeg', 'eye', 'game']
    offset = {'eeg': [], 'eye': [], 'game': []}
    subjects = [
        '2002', '2003', '2004', '2005', '2007', '2008', '2009', '2011', '2012',
        '2013', '2014', '2015', '2017', '2018', '2020'
    ]
    sessions = ['S002']
    for subject in subjects:
        for session in sessions:
            temp = data['sub-OFS_' + subject][session]
            for i, stream in enumerate(streams):
                offset[stream].append(temp[stream]['time_offsets'] -
                                      np.mean(temp[stream]['time_offsets']))

    # place_x = [0.075, 0.4, 0.71]
    title = {'eeg': 'EEG Data', 'eye': 'Eye Data', 'game': 'Game Data'}
    for i, stream in enumerate(streams):
        data = np.concatenate(offset[stream], axis=0)
        ax[i].set_title(title[stream])
        ax[i].hist(data, edgecolor='black')
        ax[i].grid()
        ax[i].ticklabel_format(axis="x", style="sci", scilimits=(0, 0))
        ax[i].set_xlabel('Time offsets (s)')
    plt.autoscale(enable=True, axis='x')
    plt.tight_layout(pad=0)

    file_name = 'reports/images/' + 'time_offsets.pdf'
    save_path = Path(__file__).parents[1] / file_name
    plt.savefig(save_path)
    plt.show()


plot_time_delays(config)
