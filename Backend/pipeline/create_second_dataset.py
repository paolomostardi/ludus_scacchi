# creating the second dataset for the second part of the engine 
import numpy as np

def transform_from_first_dataset_to_second(x, y, saving = False, saving_path = None):
    array = []
    for index, element in enumerate(x):
        s = np.expand_dims(y[index][0], axis=0)
        array.append(np.concatenate((element, s), axis=0))
    if saving:
        np.save(saving_path, array)
    return np.array(array)
    