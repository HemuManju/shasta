import yaml
from pathlib import Path
import collections

from numpy import genfromtxt


def initial_nodes_setup(config):
    """Performs initial nodes setup
    """
    # Nodes setup
    nodes = []
    path = config['urdf_data_path'] + 'nodes.csv'
    position_data = genfromtxt(path, delimiter=',')
    for i in range(config['simulation']['n_nodes']):
        info = {}
        info['position'] = [
            position_data[i][1] * 1.125, position_data[i][0] / 1.125
        ]
        info['importance'] = 0
        nodes.append(info)
    return nodes


def blue_team_actions(config):
    # Variables
    default_actions = collections.defaultdict(dict)
    # Read fields for all the platoons
    read_path = Path(
        __file__).parents[1] / 'config/blue_team_config_baseline.yml'
    attr = yaml.load(open(str(read_path)), Loader=yaml.SafeLoader)

    # Setup the uav platoons
    ids = 0
    for i in range(len(attr['uav_platoon']['n_vehicles'])):
        actions_uav = attr['uav'].copy()
        key = 'uav_p_' + str(i + 1)
        actions_uav['platoon_id'] = i + 1
        actions_uav['n_vehicles'] = attr['uav_platoon']['n_vehicles'][i]

        # Assign the ids
        n_vehicles = actions_uav['n_vehicles']
        vehicles_id = list(range(ids, ids + n_vehicles))
        ids = ids + n_vehicles
        actions_uav['vehicles_id'] = vehicles_id

        # Update the uav action
        default_actions['uav'][key] = actions_uav

    # Setup the uav platoons
    ids = 0
    for i in range(len(attr['ugv_platoon']['n_vehicles'])):
        actions_ugv = attr['ugv'].copy()
        key = 'ugv_p_' + str(i + 1)
        actions_ugv['platoon_id'] = i + 1
        actions_ugv['n_vehicles'] = attr['ugv_platoon']['n_vehicles'][i]

        # Assign the ids
        n_vehicles = actions_ugv['n_vehicles']
        vehicles_id = list(range(ids, ids + n_vehicles))
        ids = ids + n_vehicles
        actions_ugv['vehicles_id'] = vehicles_id

        # Update the ugv action
        default_actions['ugv'][key] = actions_ugv
    return default_actions


def red_team_actions(config, team_type=None):
    # Variables
    default_actions = collections.defaultdict(dict)

    # Read fields for all the platoons
    if team_type == 'dynamic':
        read_path = Path(
            __file__).parents[1] / 'config/red_team_config_dynamic.yml'
    elif team_type == 'static':
        read_path = Path(
            __file__).parents[1] / 'config/red_team_config_static.yml'
    else:
        read_path = Path(
            __file__).parents[1] / 'config/red_team_config_baseline.yml'

    attr = yaml.load(open(str(read_path)), Loader=yaml.SafeLoader)

    # Setup the uav platoons
    ids = 0
    for i in range(len(attr['uav_platoon']['n_vehicles'])):
        actions_uav = attr['uav'].copy()
        key = 'uav_p_' + str(i + 1)
        actions_uav['platoon_id'] = i + 1
        actions_uav['n_vehicles'] = attr['uav_platoon']['n_vehicles'][i]

        # Assign the ids
        n_vehicles = actions_uav['n_vehicles']
        vehicles_id = list(range(ids, ids + n_vehicles))
        ids = ids + n_vehicles
        actions_uav['vehicles_id'] = vehicles_id

        # Update the uav action
        default_actions['uav'][key] = actions_uav

    # Setup the uav platoons
    ids = 0
    for i in range(len(attr['ugv_platoon']['n_vehicles'])):
        actions_ugv = attr['ugv'].copy()
        key = 'ugv_p_' + str(i + 1)
        actions_ugv['platoon_id'] = i + 1
        actions_ugv['n_vehicles'] = attr['ugv_platoon']['n_vehicles'][i]

        # Assign the ids
        n_vehicles = actions_ugv['n_vehicles']
        vehicles_id = list(range(ids, ids + n_vehicles))
        ids = ids + n_vehicles
        actions_ugv['vehicles_id'] = vehicles_id

        # Update the ugv action
        default_actions['ugv'][key] = actions_ugv
    return default_actions
