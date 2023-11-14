import pygame
from FrontEnd.button import Button


def traning_mode():

    WIDTH = 1200
    HEIGHT = 800

    running = True
    pygame.font.init() 
    clock = pygame.time.Clock()
    framerate = 15
    screen = pygame.display.set_mode((WIDTH, HEIGHT))    
    analysis_rect = (100,50,1000,150)
    analysis_button = Button(analysis_rect, color= (30,123,45), message = ' Choose the model you would like to train' , screen=screen )


    while running:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('CLICK EVENT COORDINATE ')
                print(event.pos)
                if analysis_button.check_click(event.pos):
                        print('hello')
                        pygame.quit()

            if event.type == pygame.QUIT:
                    running = False


        screen.fill((150, 150, 150))
        analysis_button.render()
        pygame.display.update()
        clock.tick(framerate)
