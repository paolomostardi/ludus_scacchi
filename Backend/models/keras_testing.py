import numpy as np
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from keras.utils import to_categorical

# Generate random data and labels for demonstration
# You should replace this with your actual data
num_samples = 1000
image_size = (32, 32, 3)  # Adjust the size based on your actual data

# Generate random images with values between 0 and 1
data = np.random.rand(num_samples, *image_size)

# Generate random labels as integers (e.g., for a binary classification task)
labels = np.random.randint(2, size=num_samples)

# Convert labels to one-hot encoding
labels = to_categorical(labels, num_classes=2)

# Create a simple CNN model
model = Sequential()
model.add(Conv2D(32, (3, 3), activation='relu', input_shape=image_size))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(Flatten())
model.add(Dense(64, activation='relu'))
model.add(Dense(2, activation='softmax'))  # 2 classes in this example

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(data, labels, epochs=10, batch_size=32)

# You can save the model for future use if needed
# model.save('my_cnn_model.h5')
