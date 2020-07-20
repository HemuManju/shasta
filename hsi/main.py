import yaml
from pathlib import Path

from envs.enhance_env import EnhanceEnv
from default_actions.default_actions import blue_team_actions, red_team_actions

from utils import skip_run

config_path = Path(__file__).parents[1] / 'hsi/config/simulation_config.yml'
config = yaml.load(open(str(config_path)), Loader=yaml.SafeLoader)

with skip_run('run', 'Test New Framework') as check, check():

    default_blue_actions = blue_team_actions(config)
    default_red_actions = red_team_actions(config)

    env = EnhanceEnv(config)
    env.step(default_blue_actions, default_red_actions)
