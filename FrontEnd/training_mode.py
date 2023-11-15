import pygame
import requests
from Backend.pipeline.lichess_user import LichessUser
from FrontEnd.button import Button


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


def train_on_user(user : LichessUser):

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








def main():


    model = choose_model()
    user = choose_user()
    train_on_user(user)
