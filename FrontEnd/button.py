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
        self.screen = screen 

    def set_on_click(self, method):
        self.on_click = method

    def check_click(self, coordinates, args = []):
        click_x, click_y = coordinates
        if self.x <= click_x <= self.x + self.width and self.y <= click_y <= self.y + self.height:
            return True

    def render(self):
        # pygame.draw.rect(screen,(0,0,0),random_choice_square[1])
        
        pygame.draw.rect(self.screen, self.color, self.rectangle)
        self.screen.blit(self.text_surface, (self.x , self.y + self.height // 2 ))
