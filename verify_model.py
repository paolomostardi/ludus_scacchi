import sys
import os
sys.path.append(os.getcwd())

from Backend.model_architecture.implementation.experimental_architecture1 import experimental_architecture1

def verify():
    print("Building model...")
    model = experimental_architecture1()
    model.summary()
    print("Model built successfully.")

if __name__ == "__main__":
    verify()
