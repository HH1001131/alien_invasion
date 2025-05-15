import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """管理游戏资源和行为的类"""
    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.clock=pygame.time.Clock()
        self.settings=Settings()
        
        #使用特定值屏幕大小
        #self.screen=pygame.display.set_mode((self.settings.screen_width,self.settings.screen_height))
        #使用全屏
        self.screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        self.settings.screen_width=self.screen.get_rect().width
        self.settings.screen_height=self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        #创建一个用于存储游戏统计信息的实例
        self.stats=GameStats(self)
                
        self.ship=Ship(self)
        self.bullets=pygame.sprite.Group()
        self.aliens=pygame.sprite.Group()

        self._creat_fleet()

        #设置背景颜色
        self.bg_color=(self.settings.bg_color)

        #游戏一开始处于非活动状态
        self.game_active=False

        #创建Play按钮
        self.play_button=Button(self,"Play")
    
    def _creat_fleet(self):
        """创建一个外星人舰队"""
        #创建一个外星人,在不断添加，直到没有空间为止
        alien=Alien(self)
        alien_width,alien_height=alien.rect.size

        current_x,current_y=alien_width,alien_height
        while current_y<(self.settings.screen_height-3*alien_height):
            while current_x<(self.settings.screen_width-2*alien_width):
                self._creat_alien(current_x,current_y)
                current_x+=2*alien_width
            #一行加完后，重置x，递增y
            current_x=alien_width
            current_y+=2*alien_height

    def _creat_alien(self,x_position,y_position):
        """创建一个外星人,将其加入舰队"""
        new_alien=Alien(self)
        new_alien.x=x_position
        new_alien.rect.x=x_position
        new_alien.rect.y=y_position
        self.aliens.add(new_alien)


    def run_game(self):
        """开始游戏的主循环"""
        while True:
            self._check_events() 
            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            
            self._update_screen()
            #控制帧率
            self.clock.tick(60)
    
    def _check_fleet_edges(self):
        """在有外星人到达边缘时采取相应措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
        
    def _change_fleet_direction(self):
        """将整个外星舰队向下移动并改变方向"""
        for alien in self.aliens.sprites():
            alien.rect.y+=self.settings.fleet_drop_speed
        self.settings.fleet_direction*=-1
    

    def _update_aliens(self):
        """检查是否有外星人位于屏幕边缘,更新所有外星人位置"""
        self._check_fleet_edges()
        self.aliens.update()

        #检测外星人和飞船之间的碰撞
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            self._ship_hit()
        
        self._check_aliens_bottom()
    
    def _check_aliens_bottom(self):
        """检查是否有外星人到达屏幕下边缘"""
        for alien in self.aliens.sprites():
            if alien.rect.bottom>=self.settings.screen_height:
                self._ship_hit()
                break


    def _ship_hit(self):
        """响应飞船和外星人的碰撞"""
        if self.stats.ships_left>0:
            #将余下飞船数-1
            self.stats.ships_left-=1

            self.bullets.empty()
            self.aliens.empty()

            #创建一个新的舰队，放置飞船
            self._creat_fleet()
            self.ship.center_ship()

            #暂停
            sleep(0.5)
        else:
            self.game_active=False
            pygame.mouse.set_visible(True)


    def _update_bullets(self):
        #更新子弹位置
        self.bullets.update()
         #删除消失的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom<=0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()
    
    def _check_bullet_alien_collisions(self): 
        """响应子弹和外星人碰撞"""         
        #检查是否有子弹击中外星人，有就删除相应子弹和外星人
        collisions=pygame.sprite.groupcollide(self.bullets,self.aliens,True,True)
        if not self.aliens:
            #删除现有子弹并创建一个新外星舰队
            self.bullets.empty()
            self._creat_fleet()
            self.settings.increase_speed()

     #侦听键盘和鼠标事件
    def _check_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                sys.exit()
            elif event.type==pygame.KEYDOWN:
                self._check_keydown_events(event)              
            elif event.type==pygame.KEYUP:
                self._check_keyup_events(event)   
            elif event.type==pygame.MOUSEBUTTONDOWN:
                mouse_pos=pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self,mouse_pos):
        """单机Play时开始游戏""" 
        button_clicked=self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            #还原游戏设置
            self.settings.initialize_dynamic_settings()
            
            #重置游戏统计信息
            self.stats.reset_stats()
            self.game_active=True

            #清空外星人和子弹列表
            self.bullets.empty()
            self.aliens.empty()

            #创建一个新舰队并将飞船放置在底部中央
            self._creat_fleet()
            self.ship.center_ship()

            #隐藏光标
            pygame.mouse.set_visible(False)


    def _check_keydown_events(self,event):
        """响应按下"""
        if event.key==pygame.K_RIGHT:
            self.ship.moving_right=True
        elif event.key==pygame.K_LEFT:
            self.ship.moving_left=True
        elif event.key==pygame.K_ESCAPE:
            sys.exit()
        elif event.key==pygame.K_SPACE:
            self._fire_bullet_()

    def _check_keyup_events(self,event):
        """响应释放"""    
        if event.key==pygame.K_RIGHT:
            self.ship.moving_right=False
        elif event.key==pygame.K_LEFT:
            self.ship.moving_left=False
            
    def _fire_bullet_(self):
        """创建一颗子弹 将其加入编组bullets"""
        if len(self.bullets)<self.settings.bullets_allowed:
            new_bullet=Bullet(self)
            self.bullets.add(new_bullet)


    #每次循环都重绘屏幕
    def _update_screen(self):
        self.screen.fill(self.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)

        #若游戏处于非活动状态，就绘制Play按钮
        if not self.game_active:
            self.play_button.draw_button()

        #让最近绘制的屏幕可见
        pygame.display.flip()

if __name__=='__main__':
    #创建游戏实例并运行游戏
    ai=AlienInvasion()
    ai.run_game()



