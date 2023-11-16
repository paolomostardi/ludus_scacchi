import pygame
import requests
from Backend.pipeline.lichess_user import LichessUser
from FrontEnd.button import Button
from Backend.pipeline import get_games_in_pgn_from_lichess_api as get_games
from Backend.pipeline import from_PGN_generate_bitboards as generate_bitboards
from Backend.pipeline import create_second_dataset
import numpy as np
from keras.models import load_model
from keras import Model

def choose_model():

    WIDTH = 1200
    HEIGHT = 800

    running = True
    pygame.font.init() 
    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    analysis_rect = (100,50,1000,150)
    question_button = Button(analysis_rect, color= (30,123,45), message = '  Choose the model you would like to train' , screen=screen )

    analysis_rect = (100,350,500,150)
    vgg_button = Button(analysis_rect, color= (123,123,45), message = ' VGG ' , screen=screen )
    
    analysis_rect = (600,350,500,150)
    resnet_button = Button(analysis_rect, color= (30,123,123), message = ' RESNET ' , screen=screen )
    
    while running:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('CLICK EVENT COORDINATE ')
                print(event.pos)
                if vgg_button.check_click(event.pos):
                    return
                if resnet_button.check_click(event.pos):
                    return 

            if event.type == pygame.QUIT:
                    running = False

        screen.fill((150, 150, 150))
        
        question_button.render()
        vgg_button.render()
        resnet_button.render()

        pygame.display.update()
        clock.tick(framerate)

def choose_user():

    WIDTH = 1200
    HEIGHT = 800

    running = True
    pygame.font.init() 
    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    user_text = ''
    text_box_clicked = False

    analysis_rect = (100,50,1000,150)
    question_button = Button(analysis_rect, color= (30,123,45), message = '  Choose the user you would like to train ' , screen=screen )
    
    analysis_rect = (100,300,1000,150)
    user_input = Button(analysis_rect, color= (30,123,45), message = user_text , screen=screen )
    
    analysis_rect = (150,550,300,200)
    enter_button = Button(analysis_rect, color= (200,45,45), message = ' Confirm user ' , screen=screen )

    while running:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('CLICK EVENT COORDINATE ')
                print(event.pos)

                if user_input.check_click(event.pos):
                    text_box_clicked = True
                else:
                    text_box_clicked = False
                if enter_button.check_click(event.pos):
                    user = get_user_info(user_text)
                    if user:
                        return user

            if event.type == pygame.QUIT:
                    running = False

            if event.type == pygame.KEYDOWN:
                if text_box_clicked:
                    if event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                        user_input.update_message(user_text)

                    else:
                        user_text += event.unicode
                        user_input.update_message(user_text)

                print(user_input.message)

        screen.fill((150, 150, 150))
        
        question_button.render()
        user_input.render()
        enter_button.render()

        pygame.display.update()
        clock.tick(framerate)

def get_user_info(username):
    url = "https://lichess.org/api/user/" + username
    response = requests.get(url)
    response = response.json()
    if 'error' in response:
        print('error')
        return None
    user = LichessUser(response)
    return user


def show_user_infos(user : LichessUser):

    WIDTH = 1200
    HEIGHT = 800

    running = True
    pygame.font.init() 
    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    user_text = ''
    text_box_clicked = False

    analysis_rect = (100,50,1000,100)
    question_button = Button(analysis_rect, color= (30,123,45), message = '  USER FOUND: ' + user.username , screen=screen )
    
    analysis_rect = (100,700,300,10)
    enter_button = Button(analysis_rect, color= (200,45,45), message = ' Confirm user ', screen=screen )

    analysis_rect = (100,300,300,10)
    bullet_button = Button(analysis_rect, color= (30,123,45), message = '  Total bullet games ' + str(user.bullet_amount_of_games) , screen=screen )

    analysis_rect = (100,400,300,10)
    blitz_button = Button(analysis_rect, color= (30,123,45), message = '  Total blitz games ' + str(user.blitz_amount_of_games) , screen=screen )

    analysis_rect = (100,500,300,10)
    rapid_button = Button(analysis_rect, color= (30,123,45), message = '  Total rapid games ' + str(user.rapid_amount_of_games) , screen=screen )
    
    analysis_rect = (100,600,300,10)
    classical_button = Button(analysis_rect, color= (30,123,45), message = '  Total classical_amount_of_games ' + str(user.classical_amount_of_games) , screen=screen )



    while running:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('CLICK EVENT COORDINATE ')
                print(event.pos)

            if event.type == pygame.QUIT:
                    running = False

        screen.fill((150, 150, 150))
        
        question_button.render()
        enter_button.render()
        bullet_button.render()
        blitz_button.render()
        rapid_button.render()
        classical_button.render()

        pygame.display.update()
        clock.tick(framerate)


def train_on_user(username, model_path):
    print('doing some stuff')
    saving_path =r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\pgn_games\_'
    games_path = r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\pgn_games\pgn_games_pollofritto.csv'
    generate_bitboards.generate_from_filename(username,0,games_path,0,saving_path)

    x = np.load(saving_path + 'pollofritto_0_bitboard.npy')
    y = np.load(saving_path + 'pollofritto_0_Y_bitboard.npy')

   
    create_second_dataset.transform_from_first_dataset_to_second(x,y,True,r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\pgn_games\_pollofritto_0_x2_bitboard.npy')

    x2 = np.load(saving_path + 'pollofritto_0_x2_bitboard.npy')

    model1 = load_model(model_path[0])
    model2 = load_model(model_path[1])

    print(model1.summary())
    print(model2.summary())
    
    model1.fit(x,y)








def main():
    model_path1 = r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\saved_model\first_mode_engine\resnet.h5'
    model_path2 = r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\saved_model\second_part_engine\VGG19_piece_Predictor.h5'
    train_on_user('pollofritto',[model_path1,model_path2])







