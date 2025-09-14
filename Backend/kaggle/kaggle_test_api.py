from kaggle.api.kaggle_api_extended import KaggleApi
import time

# Authenticate
api = KaggleApi()
api.authenticate()

# Define your Kaggle notebook (username/notebook-name)
NOTEBOOK_PATH = "/home/paolo/Desktop/projects/Ludus/ludus_scacchi/Backend/kaggle/"  # Update with your real notebook path

api.kernels_push("Backend\kaggle")


