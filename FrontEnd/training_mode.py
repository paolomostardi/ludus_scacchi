import pygame
import requests
from Backend.data_pipeline.lichess_user import LichessUser
from FrontEnd.button import Button
from FrontEnd import play_mode

from Backend.data_pipeline import get_games_in_pgn_from_lichess_api as get_games
from Backend.data_pipeline import from_PGN_generate_bitboards as generate_bitboards
from Backend.data_pipeline import create_second_dataset
import numpy as np
from keras.models import load_model
import pandas as pd
import os
from FrontEnd import helper
import threading
import queue

# training mode trains models on users games
# it uses elements of the backend pipeline to prep the data for the models
# it then trains the models on a separate thread to not block the UI 
# finally it saves the models in the trainind_data/model folder

def choose_user():
    # region  button declaration

    WIDTH = 1200
    HEIGHT = 800

    running = True
    pygame.font.init()  
    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    black_bishop_icon = pygame.image.load(r'FrontEnd/Pieces/black/b.png')
    pygame.display.set_icon(black_bishop_icon)
    pygame.display.set_caption('Ludus Scacchi')

    background_color = (33,41,46)
    black = (50,50,50)
    padding_size = 2
    button_gray = (185,185,185)
    light_blue = (106,131,146)
    orange = (218,145,37)

    user_text = ''
    text_box_clicked = False    
    total_game_clicked = False


    background_div_rect = (0,0,1200,550)
    background_div = Button(background_div_rect, color = light_blue, screen=screen )    
    
    select_model_rect = (20,50,500,50)
    select_model_message = Button(select_model_rect, color= orange, message = ' Select model ' ,font_size = 32, font_padding=(10,10), screen=screen, border_radius=10, padding=True, padding_color=black,padding_size=padding_size )

    engine_button_list = []
    try: 
        path = 'training_data\model'
        for index, engine_name in enumerate(os.listdir(path)):
            engine_rect = (40,120 + (50 * index), 350, 35) 
            engine_button_list.append( Button(engine_rect,orange,screen,message=engine_name,font_size= 27, font_padding=(20,3),padding=True,padding_size=padding_size,padding_color=(50,50,50) ) )    
    except Exception:
        print('ops')

    select_user_rect = (600,50,550,50)
    select_user_message = Button(select_user_rect, color = orange, message = ' Insert name of the user ' ,font_size = 32, font_padding=(10,10), screen=screen, border_radius=10, padding=True, padding_color=black,padding_size=padding_size )
   
    user_input_rect = (610,120,400,45)
    user_input = Button(user_input_rect, color= orange, message = user_text , screen=screen , padding=True, padding_color=black, padding_size=padding_size, font_size = 25 , font_padding=(10,10))
    
    user_search_rect = (920,120,200,45)
    user_search_button = Button(user_search_rect, color= button_gray, message = 'Search user' , screen=screen , padding=True, padding_color=black, padding_size=padding_size, font_size = 25 , font_padding=(45,10))

    train_model_rect = (20,470,250,70)
    train_model_button = Button(train_model_rect, color= orange, message = 'TRAIN MODEL' , screen=screen, font_size= 25 ,padding=True, padding_color=black, padding_size= padding_size, border_radius=10, font_padding=(10,10))

    new_model_rect = (300,470,250,70)
    new_model_button = Button(new_model_rect, color= orange, message = 'NEW MODEL' , screen=screen, font_size= 25 ,padding=True, padding_color=black, padding_size= padding_size, border_radius=10, font_padding=(10,10))
 
    play_rect = (570,470,250,70)
    play_button = Button(play_rect, color= orange, message = 'PLAY WITH MODEL' , screen=screen, font_size= 25 ,padding=True, padding_color=black, padding_size= padding_size, border_radius=10, font_padding=(10,10))
 
    display_user = False    
   
    display_user_rect = (610,180,550,200)
    display_user_background = Button(display_user_rect,color=orange,screen=screen, padding=True, padding_color=black, padding_size=padding_size, font_padding=(175,10))

    analysis_rect = (810,375,200,50)
    user_input_total_games = Button(analysis_rect, color = button_gray, screen=screen, font_size=25, padding=True, padding_color=black, padding_size = 1, font_padding=(10,20),message='')
    
    analysis_rect = (1010,375,150,50)
    games_to_use_message = Button(analysis_rect, color= button_gray, screen=screen,message='Games to use', font_size=25 ,padding=True, padding_color=black,padding_size=padding_size , font_padding=(5,10)    )

    flag_image = pygame.image.load(r'FrontEnd/Pieces/search_icon.png')
    
    flag_image = helper.resize_image(flag_image, 200, 0.18)

    current_model = ''

    # endregion

    to_render_progress = []

    progress_queue = queue.Queue()

    while running:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('CLICK EVENT COORDINATE ')
                print(event.pos)
                text_box_clicked = False
                total_game_clicked = False

                if user_input.check_click(event.pos):
                    text_box_clicked = True
                
                elif user_input_total_games.check_click(event.pos):
                    total_game_clicked = True
                    
                elif train_model_button.check_click(event.pos):
                    pass

                elif user_search_button.check_click(event.pos):
                    display_user_rect = (610,230,500,200)


                    user = get_user_info(user_input.message)
                    analysis_rect = (620,250,300,10)
                    bullet_button = Button(analysis_rect, color= orange, message = 'Bullet games:      ' + str(user.bullet_amount_of_games)  + '  Rating:  ' + str(user.bullet_rating), screen=screen, font_size=25 )

                    analysis_rect = (620,280,300,10)
                    blitz_button = Button(analysis_rect, color= orange, message = 'Blitz games:        ' + str(user.blitz_amount_of_games)  + '  Rating:  ' + str(user.blitz_rating), screen=screen, font_size=25 )

                    analysis_rect = (620,310,300,10)
                    rapid_button = Button(analysis_rect, color= orange, message = 'Rapid games:      ' + str(user.rapid_amount_of_games) + '  Rating:  ' + str(user.rapid_rating) , screen=screen, font_size=25 )
                    
                    analysis_rect = (620,340,300,10)
                    classical_button = Button(analysis_rect, color= orange, message = 'Classical games: ' + str(user.classical_amount_of_games) + '  Rating:  ' + str(user.classical_rating) , screen=screen, font_size=25     )                    
                    
                    analysis_rect = (610,375,200,50)
                    total_games_message = Button(analysis_rect, color= orange, message = 'Total games: ' + str(user.total_amount_of_games), screen=screen, font_size=25 ,padding=True, padding_color=black,padding_size=padding_size , font_padding=(10,20)   )
                    

                    display_user_background.update_message(user.username)
                    
                    display_user = True

                elif train_model_button.check_click(event.pos):
                    train_model_given_user_and_model(user.username, r'training_data\model\\' + current_model)

                elif new_model_button.check_click(event.pos):
                    print(current_model,' the current model is ')
                    print(display_user_background.message)
                    path_to_current_model = r'training_data\model\\' + current_model
                    path_to_save=r'training_data\model\\' + display_user_background.message

                    task_thread = threading.Thread(target=train_model_given_user_and_model, args=(user.username, path_to_current_model, path_to_save ,progress_queue))
                    task_thread.start()

                    to_render_progress = []

                elif play_button.check_click(event.pos):
                    pygame.quit()
                    play_mode.main()

                else:
                    for engine in engine_button_list:
                        if engine.check_click(event.pos):
                            current_model = engine.message 
                            print(engine.message)

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

                elif total_game_clicked:
                    if event.key == pygame.K_BACKSPACE:
                        msg = user_input_total_games.message[:-1]
                        user_input.update_message(msg)
                    else:
                        msg = user_input_total_games.message
                        user_input_total_games.update_message(msg + event.unicode)

                print(user_input.message)

        # region render
        screen.fill(background_color)
        background_div.render()
        select_model_message.render()
        select_user_message.render()

        user_input.render()
        user_search_button.render()
        train_model_button.render()
        new_model_button.render()
        play_button.render()

        if display_user:
            display_user_background.render()
            bullet_button.render()
            blitz_button.render()
            rapid_button.render()
            classical_button.render()
            total_games_message.render()
            user_input_total_games.render()
            games_to_use_message.render()


        screen.blit(flag_image, (user_search_button.x + 5, user_search_button.y + 5))
        



        for i in engine_button_list:
            i.render()

      
        while True:
            try:
                progress_message = progress_queue.get_nowait()  

                current_lenght = len(to_render_progress)
                progress_square = (10, 575 + (current_lenght * 50), 0, 0)
                progress = Button(progress_square, background_color,screen,message=progress_message,font_color=(255,255,255),font_size = (30))
                to_render_progress.append(progress)
            except queue.Empty:
                break
        
        
        for i in to_render_progress:
            i.render()


        pygame.display.update()
        clock.tick(framerate)
        # endregion 


def get_user_info(username):
    print('looking for the user :', username)
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
    bullet_button = Button(analysis_rect, color= (30,123,45), message = 'Bullet games ' + str(user.bullet_amount_of_games) , screen=screen )

    analysis_rect = (100,400,300,10)
    blitz_button = Button(analysis_rect, color= (30,123,45), message = 'Blitz games ' + str(user.blitz_amount_of_games) , screen=screen )

    analysis_rect = (100,500,300,10)
    rapid_button = Button(analysis_rect, color= (30,123,45), message = 'Rapid games ' + str(user.rapid_amount_of_games) , screen=screen )
    
    analysis_rect = (100,600,300,10)
    classical_button = Button(analysis_rect, color= (30,123,45), message = 'Classical games ' + str(user.classical_amount_of_games) , screen=screen )



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

    x = np.load(saving_path + 'pollofritto_0_bitboard.npy')
    y = np.load(saving_path + 'pollofritto_0_Y_bitboard.npy')   

    x2 = np.load(saving_path + 'pollofritto_0_x2_bitboard.npy')

    model1 = load_model(model_path[0])
    model2 = load_model(model_path[1])

    print(model1.summary())
    print(model2.summary())
    
    y1,y2 = create_second_dataset.transform_y(y)

    model1.fit(x,np.array(y1))
    model2.fit(x2,np.array(y2))


def check_model_fit_on_username(username,path_to_model):
    df = pd.read_csv(path_to_model + '\list_of_users.csv')
    if username in df['trained_users'].values:
        return True
    return False


def check_data_available_on_username(username):
    path = 'training_data\data'
    if username in os.listdir(path):
        return True
    return False


def fit_model_on_user_data(username,path_to_model,saving_path = None):
    path_to_model1 = path_to_model + r'\first_part\model.h5'
    path_to_model2 = path_to_model + r'\second_part\model.h5'
    
    if saving_path is None:
        saving_path = path_to_model

    saving_to_model1 = saving_path + r'\first_part\model.h5'
    saving_to_model2 = saving_path + r'\second_part\model.h5'

    model1 = load_model(path_to_model1)
    model2 = load_model(path_to_model2)
    
    data_path = r'training_data\data\\' + username+ r'\bitboard'

    print(path_to_model)
    print(path_to_model1)
    
    x1 = np.load(data_path + r'\x.npy')
    x2 = np.load(data_path + r'\x2.npy')
    y1 = np.load(data_path + r'\y.npy') 
    y2 = np.load(data_path + r'\y2.npy')

    model1.fit(x1,y1)
    model2.fit(x2,y2)

    df = pd.read_csv(path_to_model + '\list_of_users.csv')
    df = df.append({'trained_users': username}, ignore_index=True)

    print('saving at : ')
    print(saving_path)
    print(saving_to_model1)
    print(saving_to_model2)

    model1.save(saving_to_model1)
    model2.save(saving_to_model2)

    print(df)
    df.to_csv(path_to_model + '\list_of_users.csv')


    

    return model1, model2 


def download_and_process_data_of_user(username):
    folder_path = r'training_data\data\\' + username + r'\pgn'
    file_path = r'training_data\data\\' + username + r'\pgn\pgn_games_' + username + '.csv'

    saving_path = r'training_data\data\\' + username + r'\bitboard'

    os.makedirs(saving_path)


    print('generating the bitboards')
    print('---------------- CURRENT PATH BEING USED --------------')
    
    print(folder_path)    
    get_games.get_pgn_games_from_username(username,folder_path,number_of_games=100)    
    generate_bitboards.generate_from_filename('',0,file_path,0,saving_path)
    return 


def train_model_given_user_and_model(username, path_to_model, path_to_save = None, progress_queue = None):
    if path_to_save is None:
        path_to_save = path_to_model


    if progress_queue:
        progress_queue.put('checking if the model has already been trained')    
    

    if check_model_fit_on_username(username,path_to_model):
        if progress_queue:
            progress_queue.put('model already trained')
    else:
        if check_data_available_on_username(username):
            if progress_queue:
                progress_queue.put('Data already process for this User')
            fit_model_on_user_data(username,path_to_model,path_to_save)

        else:
            if progress_queue:
                progress_queue.put('Processing data for user')
            download_and_process_data_of_user(username)
            if progress_queue:
                progress_queue.put('Training model on user')
            fit_model_on_user_data(username, path_to_model,path_to_save)


def main():

    choose_user()







