import os
import ray
import psutil
import math
import time
import numpy as np
import pandas as pd

import yaml
from pathlib import Path

import collections

from envs.enhance_env import EnhanceEnv
from default_actions.default_actions import (blue_team_actions,
                                             red_team_actions)

config_path = Path(__file__).parents[1] / 'hsi/config/simulation_config.yml'
config = yaml.load(open(str(config_path)), Loader=yaml.SafeLoader)


def nested_dict():
    return collections.defaultdict(nested_dict)


def change_target_position(actions, target_position):
    for i in range(3):
        key = 'uav_p_' + str(i + 1)
        actions['uav'][key]['target_pos'] = target_position
        actions['uav'][key]['initial_formation'] = True

        key = 'ugv_p_' + str(i + 1)
        actions['ugv'][key]['target_pos'] = target_position
        actions['ugv'][key]['initial_formation'] = True
    return actions


def convert_memory_size(nbytes):
    metric = ("B", "kB", "MB", "GB", "TB")
    if nbytes == 0:
        return "%s %s" % ("0", "B")

    # nunit = int(math.floor(math.log(nbytes, 1024)))
    nsize = round(nbytes / (math.pow(1024, 2)), 2)
    return nsize, '%s %s' % (format(nsize, ".2f"), metric[2])


@ray.remote
class State():
    def __init__(self):
        self.task_done = False

    def task_complete(self):
        self.task_done = True

    def task_status(self):
        return self.task_done


@ray.remote
class Actor(object):
    def __init__(self, state):
        self.state = state
        self.done = False

    def get_pid(self):
        print(os.getpid())
        return os.getpid()

    def is_done(self):
        return self.done

    def run(self, config):
        default_blue_actions = blue_team_actions(config)
        default_red_actions = red_team_actions(config)

        env = EnhanceEnv(config)
        # Action 1
        # Change the end position
        blue_actions = change_target_position(
            default_blue_actions, target_position=[42.888361, -78.880011, 1])
        speed_up = env.step(blue_actions, default_red_actions)

        # Action 2
        # Change the end position
        blue_actions = change_target_position(
            default_blue_actions, target_position=[42.887369, -78.878633, 1])
        speed_up = env.step(blue_actions, default_red_actions)

        # Action 3
        # Change the end position
        blue_actions = change_target_position(
            default_blue_actions, target_position=[42.889052, -78.875661, 1])
        speed_up = env.step(blue_actions, default_red_actions)

        # Action 4
        # Change the end position
        blue_actions = change_target_position(
            default_blue_actions, target_position=[42.887040, -78.881616, 1])
        speed_up = env.step(blue_actions, default_red_actions)

        self.state.task_complete.remote()
        return speed_up


@ray.remote
class Profiler(object):
    def __init__(self, state):
        self.state = state
        return None

    def profile(self, actor_pid):
        cpu, memory, memory_percent = [], [], []
        start_time = time.time()
        current_time = 0
        currentProcess = psutil.Process(actor_pid)
        while current_time <= 20:
            current_time = time.time() - start_time
            cpu.append(
                currentProcess.cpu_percent(interval=0.5) /
                psutil.cpu_count(logical=False))
            memory_bytes = currentProcess.memory_info()[0]
            memory.append(convert_memory_size(memory_bytes)[0])
            memory_percent.append(currentProcess.memory_percent())
            if ray.get(self.state.task_status.remote()):
                break
        return cpu, memory, memory_percent


def cpu_memory_profile(config):
    # Initiate ray
    if not ray.is_initialized():
        ray.init(num_cpus=10)

    state = State.remote()
    actor = Actor.remote(state)
    profiler = Profiler.remote(state)

    # Get the actor PID
    actor_pid = ray.get(actor.get_pid.remote())

    # Run all the clients in parallel
    out = ray.get(
        [profiler.profile.remote(actor_pid),
         actor.run.remote(config)])
    cpu, memory, memory_percent, speed_up = out[0][0], out[0][1], out[0][
        2], out[1]

    # Shutdown ray
    ray.shutdown()

    return np.max(cpu), np.max(memory), np.max(memory_percent), speed_up


# Main loop
results = pd.DataFrame(columns=[
    'world_size', 'uav + ugv', 'headless', 'cpu', 'memory', 'memory_percent',
    'speed_up'
])
model_sizes = ['small', 'medium', 'large']
platoon_sizes = [60, 90, 120, 150, 180, 210]
headless = [False, True]
run = 0
for model_size in model_sizes:
    config['simulation']['map_to_use'] = 'buffalo-' + model_size
    for platoon_size in platoon_sizes:
        config['experiment']['platoon_size'] = int(platoon_size / 6)
        for item in headless:
            config['simulation']['headless'] = item
            # Run the profiling
            cpu, memory, memory_percent, speed_up = cpu_memory_profile(config)
            results.loc[run] = [
                model_size, platoon_size, item, cpu, memory, memory_percent,
                speed_up
            ]
            run += 1
            print(results)

# Save the dataframe to csv
results.to_csv('cpu_memory_profile_exp_5.csv', index=False)
