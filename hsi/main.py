import yaml
from pathlib import Path

from envs.enhance_env import EnhanceEnv
from default_actions.default_actions import blue_team_actions

from gui.gui_main import MainGUI

from utils import skip_run
from visualize import plot_nodes

config_path = Path(__file__).parents[1] / 'hsi/config/simulation_config.yml'
config = yaml.load(open(str(config_path)), Loader=yaml.SafeLoader)

with skip_run('run', 'Test New Framework') as check, check():

    default_blue_actions = blue_team_actions(config)

    # config['simulation']['map_to_use'] = 'buffalo-medium'
    if config['simulation']['show_nodes']:
        plot_nodes(config)
    else:
        env = EnhanceEnv(config)
        env.step(default_blue_actions)

with skip_run('skip', 'Test New GUI') as check, check():
    gui = MainGUI(1200, 800, config)
    gui.run()
