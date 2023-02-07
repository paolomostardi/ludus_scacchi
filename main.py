import pygame
import analysis_mode


def main():
    light_green = (148, 238, 140)
    dark_green = (100, 150, 120)
    red_text = (160, 50, 35)
    background_grey = (185, 180, 180)
    pygame.init()

    window_size = (700, 700)
    screen = pygame.display.set_mode(window_size)

    button_width = 300
    button_height = 100

    button_x = (window_size[0] - button_width) // 2
    button_y = (window_size[1] - button_height) // 5

    button_color = light_green
    button_color_hover = dark_green

    font = pygame.font.SysFont('', 48)
    label = font.render("Analysis Mode", True, red_text)

    text_width, text_height = font.size("Analysis Mode")
    text_x = (button_width - text_width) // 2
    text_y = (button_height - text_height) // 2

    button = pygame.Surface((button_width, button_height))
    button.fill(button_color)
    button.blit(label, (0, 0))

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_x <= mouse_pos[0] <= button_x + button_width and \
                        button_y <= mouse_pos[1] <= button_y + button_height:
                    analysis_mode.main()
        mouse_pos = pygame.mouse.get_pos()
        if button_x <= mouse_pos[0] <= button_x + button_width and \
           button_y <= mouse_pos[1] <= button_y + button_height:
            button.fill(button_color_hover)
        else:
            button.fill(button_color)

        screen.fill(background_grey)
        button.blit(label, (text_y, text_x))
        screen.blit(button, (button_x, button_y))

        pygame.display.update()
        clock.tick(16)
    pygame.quit()


main()
