import yaml
from pathlib import Path

from envs.benning_env import BenningEnv
from default_actions.default_actions import blue_team_actions, red_team_actions

from utils import skip_run

config_path = Path(__file__).parents[1] / 'hsi/config/simulation_config.yml'
config = yaml.load(open(str(config_path)), Loader=yaml.SafeLoader)

with skip_run('run', 'Test New Framework') as check, check():

    blue_actions = blue_team_actions(config)
    red_actions = red_team_actions(config)

    env = BenningEnv(config)
    env.step(blue_actions, red_actions)
