# file used to start a ipython terminal at lunch 

import pandas as pd
import numpy as np
import keras
import tensorflow as tf

import Backend.pipeline.from_PGN_generate_bitboards as gen
import Backend.evaluation.model_evaluation as eval
from Backend.pipeline import new_pipeline as pipe
from Backend.pipeline import db_pipe as db_pipe



from importlib import reload as r 

from IPython import start_ipython

# Set up the local context with all the necessary variables
local_vars = dict(globals(), **locals())

# Launch the IPython shell with the local context
start_ipython(argv=[], user_ns=local_vars)
