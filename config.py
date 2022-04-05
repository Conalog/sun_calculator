import os

from dotenv import load_dotenv


basedir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(basedir, '.env')
load_dotenv(dotenv_path=env_path)

# VAR_EXAMPLE = os.environ["VAR_EXAMPLE"]

DATA_PATH = os.path.join(basedir, 'data/')
