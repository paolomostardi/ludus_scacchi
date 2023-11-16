import pygame 

class Button:
    def __init__(self, rectangle, color = (100,100,100), message = None, screen = None):
        
        self.x, self.y, self.width, self.height = rectangle
        self.rectangle = rectangle
        self.color =  color
        
        self.message = message
        self.font =  pygame.font.SysFont('Times new roman', 50)
        self.text_surface = self.font.render(self.message, True, (0,0,0))

        self.on_click = None
        self.outside = None
        self.outside_color = color
        self.screen = screen 

        if self.y + self.height // 2 > 50:
            self.font_height = self.y
        else:
            self.font_height = self.y + self.height // 2


    def set_on_click(self, method):
        self.on_click = method

    def check_click(self, coordinates, args = []):
        click_x, click_y = coordinates
        if self.x <= click_x <= self.x + self.width and self.y <= click_y <= self.y + self.height:
            return True
    
    def set_outside(self, outside, color = (100,100,100)):
        self.outside = outside
        self.outside_color = color

    def update_message(self,message):
        self.message = message
        self.text_surface = self.font.render(message, True, (0,0,0))


    def render(self):
        # pygame.draw.rect(screen,(0,0,0),random_choice_square[1])
        
        pygame.draw.rect(self.screen, self.color, self.rectangle)
        self.screen.blit(self.text_surface, (self.x , self.font_height))

        if self.outside:
            pygame.draw.rect(self.screen, self.outside_color, self.rectangle, 2)
