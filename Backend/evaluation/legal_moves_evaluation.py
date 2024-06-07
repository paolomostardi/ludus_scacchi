import numpy as np
from keras import Model
import keras


# this file checks how many moves played by the model are legal.


def give_max(board):
    max_switch = max(range(len(board)), key=board.__getitem__)
    return max_switch

def legal_evaluation(model : Model, testing_dataset : np.array):
    predictions = model.predict(testing_dataset)
    for prediction in predictions:
        pass


if __name__ == "__main__":
    model = keras.models.load_model('Backend/data/models/gm_model_white/gm_model_chunk_9.keras')
    dataset = np.load('chunk_0.npy')
    legal_evaluation(model, dataset[:5000])






