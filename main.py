from FrontEnd import play_mode
from FrontEnd import training_mode

import pygame
from FrontEnd.button import Button
import os

def color_choice():    

    WIDTH = 1200
    HEIGHT = 800
    board_size = 700


    background_color = (33,41,46)
    button_gray = (200,200,200)
    light_blue = (106,131,146)

    orange = (218,145,37,100)



    icon = pygame.image.load(r'C:\Users\paolo\OneDrive\Desktop\Final_project\Ludus_scacchi\FrontEnd\Pieces\black\b.png')

    running = True
    pygame.font.init() 
    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font =  pygame.font.SysFont('Times new roman', 50)

    pygame.display.set_icon(icon)
    pygame.display.set_caption('Ludus Scacchi')

    # x, y, width, height

    black_rectangle = (120,120,240,160 )
    black_button = Button(black_rectangle,button_gray,screen=screen)

    white_rectangle = (840 ,120,240,160 )
    white_button = Button(white_rectangle,button_gray,screen=screen)

    random_rectangle = (480 ,120,240,160 )
    random_button = Button(random_rectangle,button_gray,screen=screen)

    container_rectangle = (60,60,1080, 260)
    container_button = Button(container_rectangle,light_blue,screen=screen)


    engine_button_list = []

    path = 'training_data\model'
    for index, engine_name in enumerate(os.listdir(path)):
        engine_rect = (60,500 + (100 * index), 500, 80) 
        engine_button_list.append( Button(engine_rect,orange,engine_name,screen) )

    while running:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass
            if event.type == pygame.QUIT:
                    running = False


        screen.fill(background_color)
        
        container_button.render()
        black_button.render()
        white_button.render()
        random_button.render()

        [engine.render() for engine in engine_button_list]

        pygame.display.update()

        clock.tick(framerate)

color_choice()

