# Ludus_scacchi

This chess app uses keras to train CNN models on lichess games of different users.
You can then play with those engines.
There are 3 major functionalities:
 - you can fine tune base-line keras models on lichess users
 - you can analyse with your models 
 - you can play with your models

future versions might allow you to create unique traning programs based on a model and generate positions where a lichess user is more likely to make mistakes. 

## Why ludus 
While many chess engines concentrate on identifying the optimal move, they often lack the ability to emulate a human player effectively. This can hinder their role as an effective training partner since the opponent consistently makes perfect moves, which is unrealistic.

Ludus aims to rectify this by simulating real human behavior, predicting moves that align more closely with what a human player might choose in a game, thereby creating an ideal sparring partner for training purposes.

## Installation

to install simply run the follwing command :

        git clone https://github.com/paolomostardi/ludus_scacchi.git

and then run the program with 

        python main.py

to run you need the follwing modules: 

- tensorflow 
- keras
- pygame
- pychess
- pandas
- numpy

## Training on users 

To train on lichess users you can simply use the application 


![plot](./img/training_mode.png)

just write the name of the user then click search user after that either click train model to finetune a model or new model to make a new model.
click then play with model to start a game.

### training on non lichess users

if you wish to train on non-lichess users you can create a folder in training_data/data/NAMEOFPLAYER/bitboard
if you have a file that cointains many pgns files you can simply run the follwing script: 

        pyhton
        from Backend/pipeline import from_PGN_generate_bitboards as gen 
        gen.generate_from_filename(NAMEOFPLAYER,0,FILEPATH,0,SAVINGPATH)

your saving path will most likely be the one above. 


## Pipeline

![plot](./img/chess_pipeline.png)

Above is a diagram of the current pipeline. <br>
Here we can see that the initial model is trained with data from the lichess database to be a generic chess player of elo 1700.
Cloud computional resources have been used to train the model. 
The model is then deployed to the desktop application. 
The user can then download automatically games of a lichess user form their API and fine tune different models on it. 

## Model architecture 

The final model is made by 2 keras models and it splits the output in 2. <br>
One model determines which piece should move while another model determine where the piece will move. <br>
The first model uses a Resnet like architecture while the second uses a VGG like architecture. The input is a 8x8x14 for the first model and 8x8x15 for the second model.  The output of the model is a softmax function applied to a 64 array in both models. 





