
import numpy as np

from keras.models import Sequential
from keras.layers import Conv2D, Flatten, Dense

# Define the input shape
input_shape = (14, 8, 8)

# Create a Sequential model
model = Sequential()

# Add a convolutional layer with 16 filters, each of size (3, 3) and 'valid' padding
model.add(Conv2D(16, (3, 3), activation='relu', input_shape=input_shape))
model.add(Conv2D(32, (3, 3), activation='relu'))

# Add a flattening layer to transform the 3D output into a 1D vector
model.add(Flatten())

# Add a dense layer with 16 units and 'relu' activation
model.add(Dense(16, activation='relu'))

# Add the output layer with 4 units (flattened to (4,)) and appropriate activation function
model.add(Dense(4, activation='softmax'))

# Compile the model with a suitable loss function and optimizer for your specific task
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Print a summary of the model's architecture
model.summary()

x = np.load(r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\x.npy')
y = np.load(r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\asdad.npy')

model.fit(x, y)
