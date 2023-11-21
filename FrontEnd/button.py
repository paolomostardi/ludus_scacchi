import pygame 

class Button:
    def __init__(self, rectangle, color = (100,100,100), screen = None, padding_color = None,
                  message = None, border_radius = 0, font_size = 50, font_padding = (0,0), padding = False, padding_size = 5):
        
        self.x, self.y, self.width, self.height = rectangle
        self.rectangle = rectangle
        self.color =  color
        
        self.message = message
        self.font =  pygame.font.SysFont('Times new roman', font_size)
        self.text_surface = self.font.render(self.message, True, (0,0,0))

        self.on_click = None

        self.padding = padding
        self.padding_size = padding_size

        if padding_color is None:
            self.padding_color = color
        else:
            self.padding_color = padding_color

        self.screen = screen 

        if self.y + self.height // 2 > 50:
            self.font_height = self.y
        else:
            self.font_height = self.y + self.height // 2

        self.font_padding = font_padding
        self.border_radius = border_radius

    def set_on_click(self, method):
        self.on_click = method

    def check_click(self, coordinates, args = []):
        click_x, click_y = coordinates
        if self.x <= click_x <= self.x + self.width and self.y <= click_y <= self.y + self.height:
            return True
    
    def set_outside(self, outside, color = (100,100,100)):
        self.outside = outside
        self.padding_color = color

    def update_message(self,message):
        self.message = message
        self.text_surface = self.font.render(message, True, (0,0,0))


    def render(self):
        # pygame.draw.rect(screen,(0,0,0),random_choice_square[1])
        
        pygame.draw.rect(self.screen, self.color, self.rectangle, border_radius=self.border_radius)
        self.screen.blit(self.text_surface, (self.x + self.font_padding[0] , self.font_height + self.font_padding[1]))

        if self.padding:
            pygame.draw.rect(self.screen, self.padding_color, self.rectangle, self.padding_size,border_radius=self.border_radius)
