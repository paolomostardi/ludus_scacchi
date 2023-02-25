import pygame
from scripts import analysis_mode


class Button:
    def __init__(self,color_tuple, screen, button_size, button_y_dividend, text_property):

        window_size = screen.get_size()
        self.button_width, self.button_height = button_size

        self.screen = screen
        self.background_color, self.hover_color = color_tuple
        self.button_x = (window_size[0] - self.button_width) // 2
        self.button_y = (window_size[1] - self.button_height) // button_y_dividend
        self.coordinate = (self.button_x, self.button_y)

        self.pygame_button = pygame.Surface((self.button_width, self.button_height))

        font = pygame.font.SysFont('', 48)
        text_content, color_text = text_property
        self.label = font.render(text_content, True, color_text)

        text_width, text_height = font.size("Analysis Mode")
        self.text_x = (self.button_width - text_width) // 2
        self.text_y = (self.button_height - text_height) // 2

    def render(self):
        self.screen.blit(self.pygame_button, self.coordinate)

    def manage_hover(self, mouse_pos):

        is_mouse_on_the_x = self.button_x <= mouse_pos[0] <= self.button_x + self.button_width
        is_mouse_on_the_y = self.button_y <= mouse_pos[1] <= self.button_y + self.button_height

        if is_mouse_on_the_x and is_mouse_on_the_y:
            self.pygame_button.fill(self.hover_color)
        else:
            self.pygame_button.fill(self.background_color)


def main():
    light_green = (148, 238, 140)
    dark_green = (100, 150, 120)
    red_text = (160, 50, 35)
    background_grey = (185, 180, 180)
    pygame.init()

    window_size = (700, 700)
    screen = pygame.display.set_mode(window_size)
    screen.fill(background_grey)

    button_width = 300
    button_height = 100

    button_x = (window_size[0] - button_width) // 2
    button_y = (window_size[1] - button_height) // 10

    button_color = light_green
    button_color_hover = dark_green

    font = pygame.font.SysFont('', 48)
    label = font.render('text_content', True, red_text)

    text_width, text_height = font.size("Analysis Mode")
    text_x = (button_width - text_width) // 2
    text_y = (button_height - text_height) // 2

    button = pygame.Surface((button_width, button_height))

    # trying stuff
    button_size = (button_width, button_height)
    text_property = ('play stockfish', red_text)
    color_tuple = (light_green, dark_green)
    play_stockfish_button = Button(color_tuple, screen, button_size, 3, text_property)

    running = True
    clock = pygame.time.Clock()

    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_x <= mouse_pos[0] <= button_x + button_width and \
                        button_y <= mouse_pos[1] <= button_y + button_height:
                    analysis_mode.main()

        play_stockfish_button.manage_hover(mouse_pos)
        if button_x <= mouse_pos[0] <= button_x + button_width and \
           button_y <= mouse_pos[1] <= button_y + button_height:
            button.fill(button_color_hover)
        else:
            button.fill(button_color)

        button.blit(label, (text_y, text_x))
        screen.blit(button, (button_x, button_y))
        play_stockfish_button.render()

        pygame.display.update()
        clock.tick(16)
    pygame.quit()


main()
