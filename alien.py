import pygame
import pygame.imageext
from pygame.sprite import Sprite

class Alien(Sprite):
    """表示单个外星人的类"""

    def __init__(self,ai_game):
        super().__init__()
        self.screen=ai_game.screen
        self.settings=ai_game.settings

        #加载外星人图像并设置rect属性
        self.image=pygame.image.load('images/alien.bmp')
        self.rect=self.image.get_rect()

        #最初在左上角
        self.rect.x=self.rect.width
        self.rect.y=self.rect.height

        #存储外星人精确水平位置
        self.x=float(self.rect.x)

    def check_edges(self):
        """如果外星人位于屏幕边缘则返回True"""
        screen_rect=self.screen.get_rect()
        return (self.rect.right>=screen_rect.right) or (self.rect.left<=0)
    

    def update(self):
        """向左或右移动外星人"""
        self.x+=self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x=self.x
