# file used to start a ipython terminal at lunch 

import pandas as pd
import numpy as np
import keras
import tensorflow as tf

import Backend.pipeline.from_PGN_generate_bitboards as gen
import Backend.evaluation.model_evaluation as eval
import Backend.evaluation.check_dataset_legal as check_legal

from Backend.pipeline import gm_pipeline as pipe
from Backend.pipeline import lichess_month_db as m_pipe
from Backend.models.architectures.resnet50_implementation import ResNet50 as resnet





from importlib import reload as r 

from IPython import start_ipython

try:
    df = pd.read_csv('df.csv')
except :
    print('df file not found')

try:
    x = np.load('chunk_0.npy')
except :
    print('x file not found')

try:
    y = np.load('chunk_0_y.npy')
except :
    print('y file not found')
    
try:
    model = keras.models.load_model(r'Backend/data/models/13-01/lichess_13_01.keras')
except :
    print('model file not found')


# Set up the local context with all the necessary variables
local_vars = dict(globals(), **locals())

# Launch the IPython shell with the local context
start_ipython(argv=[], user_ns=local_vars)
