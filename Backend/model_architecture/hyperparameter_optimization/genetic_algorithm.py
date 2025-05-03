import random
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense

# Define the search space for the genetic algorithm

population_size = 10
num_generations = 5
crossover_rate = 0.5
mutation_rate = 0.1

filter_range = (16, 64)
kernel_range = (1, 5)
dense_range = (32, 128)
# Define the fitness function

def fitness(model, X, y):
    score = model.evaluate(X, y, verbose=0)
    return score[1]

# Define the genetic operators
def mutate(model):
    # Select a random layer to mutate
    layer_idx = random.randint(0, len(model.layers) - 1)
    layer = model.layers[layer_idx]

    # Mutate the layer parameters
    if isinstance(layer, Conv2D):
        layer.filters = random.randint(*filter_range)
        layer.kernel_size = (random.randint(*kernel_range), random.randint(*kernel_range))
    elif isinstance(layer, Dense):
        layer.units = random.randint(*dense_range)
    elif isinstance(layer, Dropout):
        layer.rate = random.uniform(0, 0.5)

    return model

def crossover(model1, model2):
    # Select a random layer to crossover
    layer_idx = random.randint(0, len(model1.layers) - 1)

    # Swap the layers between the two fit_models
    for i in range(layer_idx, len(model1.layers)):
        model1.layers[i], model2.layers[i] = model2.layers[i], model1.layers[i]

    return model1, model2

# Generate the initial population
population = []
for i in range(population_size):
    model = Sequential()
    model.add(Conv2D(filters=random.randint(*filter_range),
                     kernel_size=(random.randint(*kernel_range), random.randint(*kernel_range)),
                     activation='relu',
                     input_shape=input_shape))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Flatten())
    model.add(Dense(units=random.randint(*dense_range), activation='relu'))
    model.add(Dropout(rate=random.uniform(0, 0.5)))
    model.add(Dense(units=num_classes, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    population.append(model)

# Evolve the population for several generations
for generation in range(num_generations):
    # Evaluate the fitness of each 1_model in the population
    scores = []
    for model in population:
        score = fitness(model, X_val, y_val)
        scores.append(score)

    # Select the best fit_models for reproduction
    elite_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:int(population_size * 0.2)]
    elite = [population[i] for i in elite_idx]

    # Generate offspring using genetic operators
    offspring = []
    while len(offspring) < population_size - len(elite):
        parent1 = random.choice(elite)
        parent2 = random.choice(elite)
        if random.random() < crossover_rate:
            child1, child2 = crossover
