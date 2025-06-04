import time
import math
import random
import pygame
from pygame.constants import *

pygame.init()
pygame.mixer.init()
""" 模式选项类 """
class OptionMode(pygame.sprite.Sprite):

    def __init__(self, window, x, y, image_path, turn_anglev_angle, flag):
        pygame.sprite.Sprite.__init__(self)
        self.window = window
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.turn_anglev_angle = turn_anglev_angle
        self.v_angle = 0
        self.flag = flag

    def update(self):
        new_image = pygame.transform.rotate(self.image, -self.v_angle)
        self.window.blit(new_image, (self.rect.x + self.rect.width / 2 - new_image.get_width() / 2,self.rect.y + self.rect.height / 2 - new_image.get_height() / 2))
        self.v_angle += self.turn_anglev_angle

""" 背景图片 """
class Background(pygame.sprite.Sprite):

    def __init__(self, window, x, y, image_path):
        pygame.sprite.Sprite.__init__(self)
        self.window = window
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.window.blit(self.image, self.rect)


""" 被抛出的水果类 """
class ThrowFruit(pygame.sprite.Sprite):

    def __init__(self, window, image_path, speed, turn_anglev_angle, flag):
        pygame.sprite.Sprite.__init__(self)

        # 游戏窗口
        self.window = window

        # 导入水果图像并获取其矩形区域
        self.image = pygame.image.load(image_path)
        self.original_image = self.image.copy()  # 保存原始图像用于恢复
        self.rect = self.image.get_rect()

        # 水果抛出时x坐标取随机数
        self.rect.x = random.randint(0, Manager.WIDTH - 10)

        # 水果初始y坐标
        self.rect.y = Manager.HEIGHT

        # 抛出时速度
        self.speed = speed

        # 旋转速度
        self.turn_anglev_angle = turn_anglev_angle

        # 水果抛出时与窗口下水平线的夹角弧度，因为要用到随机函数, 所以取整数， 使用时除以100
        self.throw_anglev_angle = 157

        # 水果抛出后所经历的时间, 初始化为0
        self.fruit_t = 0

        # 旋转的总角度
        self.v_angle = 0

        # 水果抛出时的初速度
        self.v0 = 6

        # 水果标记
        self.flag = flag

        self.slow_down_time=0
        self.original_v0=6
       
       
    def update(self):
        if self.slow_down_time>0:
            # 平滑减速：随时间线性变化
            slowdown_factor = 0.5 + (0.5 * (self.slow_down_time / 300))
            self.v0 = self.original_v0 * slowdown_factor
            self.slow_down_time -= 1
            
            # 减速状态可视化
            if self.slow_down_time % 20 == 0:  # 每20帧闪烁一次
                current_scale = 0.9 + (0.1 * (self.slow_down_time / 300))
                self.image = pygame.transform.scale(
                    self.original_image,
                    (int(self.original_image.get_width() * current_scale),
                     int(self.original_image.get_height() * current_scale))
                )
        else:
            self.v0 = self.original_v0
            # 恢复原始大小
            if hasattr(self, 'original_image'):
                self.image = self.original_image
        # 当角度为90度时,可以计算出对应的弧度为： 90度 × π / 180 = 0.5π = 1.57（约）
        # 如果水果的初始X坐标位于窗口左边区域, 取抛出时弧度在70度至90度之间
        if self.rect.x <= Manager.WIDTH / 2:
            self.throw_anglev_angle = random.randint(140, 157)
        else:
            self.throw_anglev_angle=random.randint(157,175)

        sin_anglev_angle=math.sin(self.throw_anglev_angle/100)
        cos_anglev_angle=math.cos(self.throw_anglev_angle/100)

        # 计算新位置
        self.rect.y -= (self.v0 * self.fruit_t * sin_anglev_angle - (Manager.G * self.fruit_t ** 2 / 10) / 2)
        self.rect.x += self.v0 * self.fruit_t * cos_anglev_angle

        # 旋转图像
        self.v_angle = (self.v_angle + self.turn_anglev_angle) % 360  # 防止角度过大
        new_fruit = pygame.transform.rotate(self.image, -self.v_angle)
        
        # 优化绘制位置计算
        new_rect = new_fruit.get_rect(center=self.rect.center)
        self.window.blit(new_fruit, new_rect)

        # 检查是否超出屏幕
        if self.rect.y >= Manager.HEIGHT + self.rect.height:
            if self.flag != 5:  # 不是炸弹才计算miss
                Manager.classic_miss += 1
            self.kill()

        # 更新时间
        self.fruit_t += 0.1 


""" 水果切片类 """
class HalfFruit(pygame.sprite.Sprite):

    def __init__(self, window, image_path, x, y, turn_anglev_angle, v_angle, v0):
        pygame.sprite.Sprite.__init__(self)
        self.window = window
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.turn_anglev_angle = turn_anglev_angle
        self.v_angle = v_angle
        self.v0 = v0
        self.fruit_t = 0
    def update(self):
 
        # 水果旋转后的新图像
        new_fruit = pygame.transform.rotate(self.image, self.v_angle)

        # 将旋转后的新图像贴入游戏窗口, 注意, 旋转后的图像尺寸以及像素都不一样了(尺寸变大了), 所以坐标需要进行适当处理
        # 在原先图片矩形的中心位置绘制
        self.window.blit(new_fruit, (self.rect.x + self.rect.width / 2 - new_fruit.get_width() / 2,self.rect.y + self.rect.height / 2 - new_fruit.get_height() / 2))

        if self.rect.y >= Manager.HEIGHT:
            self.kill()
        self.rect.y += Manager.G * self.fruit_t ** 2 / 2
        self.rect.x += self.v0 * self.fruit_t

        self.fruit_t += 0.01
        self.v_angle += self.turn_anglev_angle


""" 水果刀光类 """
class Knife(object):

    def __init__(self, window):
        self.window = window
        self.apple_flash = pygame.image.load("./images/apple_flash.png")
        self.banana_flash = pygame.image.load("./images/banana_flash.png")
        self.peach_flash = pygame.image.load("./images/peach_flash.png")
        self.watermelon_flash = pygame.image.load("./images/watermelon_flash.png")
        self.strawberry_flash = pygame.image.load("./images/strawberry_flash.png")

    def show_apple_flash(self, x, y):
        self.window.blit(self.apple_flash, (x, y))

    def show_banana_flash(self, x, y):
        self.window.blit(self.banana_flash, (x, y))

    def show_peach_flash(self, x, y):
        self.window.blit(self.peach_flash, (x, y))

    def show_watermelon_flash(self, x, y):
        self.window.blit(self.watermelon_flash, (x, y))

    def show_strawberry_flash(self, x, y):
        self.window.blit(self.strawberry_flash, (x, y))




""" 游戏音乐类 """
class Bgm(object):

    def __init__(self):
        pygame.mixer.init()

    def play_menu(self):
        pygame.mixer.music.load("./sound/menu.mp3")
        pygame.mixer.music.play(-1, 0)
        #设置播放次数和播放时间，-1表示无限循环播放
    def play_classic(self):
        pygame.mixer.music.load("./sound/start.mp3")
        pygame.mixer.music.play(1, 0)

    def play_throw(self):
        pygame.mixer.music.load("./sound/throw.mp3")
        pygame.mixer.music.play(1, 0)

    def play_splatter(self):
        pygame.mixer.music.load("./sound/splatter.mp3")
        pygame.mixer.music.play(1, 0)

    def play_over(self):
        pygame.mixer.music.load("./sound/over.mp3")
        pygame.mixer.music.play(1, 0)

    def play_boom(self):
        pygame.mixer.music.load("./sound/boom.mp3")
        pygame.mixer.music.play(1, 0)


""" 游戏逻辑类 """
class Manager(object):
    # 窗口尺寸
    WIDTH = 640
    HEIGHT = 480

    # 游戏中的定时器常量
    THROWFRUITTIME = pygame.USEREVENT
    pygame.time.set_timer(THROWFRUITTIME, 2000)

    # 根据窗口大小，选取随机整数重力加速度, 水果下落更有层次感，使用时除以10
    G = random.randint(19, 21)

    # 经典模式miss掉的水果数，用于经典模式中的一个评判标准
    classic_miss = 0

    # 读取最好成绩
    with open('best.txt', 'r') as file:
        for line in file:
            if 'zen_mode' in line:
                zen_best = int(line.split(':')[-1].strip())
            if 'classic_mode' in line:
                classic_best = int(line.split(':')[-1].strip())

    def __init__(self):
        # 生成游戏窗口
        self.window = pygame.display.set_mode((Manager.WIDTH, Manager.HEIGHT))
        self.window_icon = pygame.image.load("./images/score.png")
        pygame.display.set_icon(self.window_icon)
        pygame.display.set_caption("水果忍者")

        # 游戏状态变量
        self.max_combo = 0

        # 创建游戏中用到的的精灵组
        self.background_list = pygame.sprite.Group()
        self.circle_option = pygame.sprite.Group()
        self.option_fruit_list = pygame.sprite.Group()
        self.fruit_half_list = pygame.sprite.Group()
        self.throw_fruit_list = pygame.sprite.Group()

        # 导入背景图像并添加入背景精灵组
        self.background = Background(self.window, 0, 0, "./images/background.jpg")
        self.home_mask = Background(self.window, 0, 0, "./images/home-mask.png")
        self.logo = Background(self.window, 20, 10, "./images/logo.png")
        self.ninja = Background(self.window, Manager.WIDTH - 320, 45, "./images/ninja.png")
        self.home_desc = Background(self.window, 20, 135, "./images/home-desc.png")
        

        self.background_list.add(self.background)
        self.background_list.add(self.home_mask)
        self.background_list.add(self.logo)
        self.background_list.add(self.ninja)
        self.background_list.add(self.home_desc)
        

        # 创建旋转的圈并添加进精灵组
        self.dojo = OptionMode(self.window, Manager.WIDTH - 600, Manager.HEIGHT - 250,"./images/dojo.png", 1, None)
        self.new_game = OptionMode(self.window, Manager.WIDTH - 405, Manager.HEIGHT - 250,"./images/new-game.png", 1, None)
        self.game_quit = OptionMode(self.window, Manager.WIDTH - 160, Manager.HEIGHT - 150,"./images/quit.png", -1, None)
        self.circle_option.add(self.dojo)
        self.circle_option.add(self.new_game)
        self.circle_option.add(self.game_quit)

        # 创建主菜单界面旋转的水果并添加进精灵组
        self.home_peach = OptionMode(self.window, Manager.WIDTH - 600 + self.dojo.rect.width / 2 - 31,Manager.HEIGHT - 250 + self.dojo.rect.height / 2 - 59 / 2,"./images/peach.png", -1, "option_peach")
        self.home_watermelon = OptionMode(self.window, Manager.WIDTH - 405 + self.new_game.rect.width / 2 - 49, Manager.HEIGHT - 250 + self.new_game.rect.height / 2 - 85 / 2,"./images/watermelon.png", -1, "option_watermelon")
        self.home_boom = OptionMode(self.window, Manager.WIDTH - 160 + self.game_quit.rect.width / 2 - 66 / 2, Manager.HEIGHT - 150 + self.game_quit.rect.height / 2 - 68 / 2, "./images/boom.png", 1, "option_boom")
        self.option_fruit_list.add(self.home_peach)
        self.option_fruit_list.add(self.home_watermelon)
        self.option_fruit_list.add(self.home_boom)


        # 设置定时器
        self.clock = pygame.time.Clock()
        self.mode_flag = 0

        # 音效
        self.bgm = Bgm()
        #刀具
        self.knife = Knife(self.window)

        # 游戏分数
        self.classic_score = 0
        self.zen_score = 0

    def create_fruit(self):
    
      """ 创建水果 """
      fruit_image_path = ["./images/apple.png", "./images/banana.png", "./images/peach.png","./images/watermelon.png", "./images/strawberry.png"]
      fruit_weights = [1, 1, 1, 1, 0.2]

      if self.mode_flag == 1:  # 禅宗模式
        # 根据是否狂暴模式决定生成数量
        if hasattr(self, 'frenzy_mode') and self.frenzy_mode:
            fruit_number = random.randint(4, 6)  # 狂暴模式：4-6个
        else:
            fruit_number = random.randint(2, 4)  # 正常模式：2-4个
        
        for _ in range(fruit_number):
            rand_fruit_index = random.choices(range(len(fruit_image_path)), weights=fruit_weights, k=1)[0]
            self.bgm.play_throw()
            fruit = ThrowFruit(self.window, fruit_image_path[rand_fruit_index], None, 5, rand_fruit_index)
            self.throw_fruit_list.add(fruit)
            
      elif self.mode_flag == 2:  # 经典模式保持不变
        boom_prob = random.randint(1, 10)
        if boom_prob == 5:
            self.bgm.play_throw()
            boom = ThrowFruit(self.window, "./images/boom.png", None, 5, 5)
            self.throw_fruit_list.add(boom)
        
        fruit_number = random.randint(1, 3)
        for _ in range(fruit_number):
            rand_fruit_index = random.choices(range(len(fruit_image_path)), weights=fruit_weights, k=1)[0]
            self.bgm.play_throw()
            fruit = ThrowFruit(self.window, fruit_image_path[rand_fruit_index], None, 5, rand_fruit_index)
            self.throw_fruit_list.add(fruit)
            

    def create_fruit_half(self, fruit_flag, fruit_x, fruit_y, turn_anglev_angle, v_angle):
        if fruit_flag == "option_peach":
            """ 禅宗模式的桃子被切开 """
            fruit_left = HalfFruit(self.window, "./images/peach-1.png", fruit_x - 50,fruit_y, turn_anglev_angle, v_angle, -5)
            fruit_right = HalfFruit(self.window, "./images/peach-2.png", fruit_x + 50,fruit_y, -turn_anglev_angle, v_angle, 5)
            self.fruit_half_list.add(fruit_left)
            self.fruit_half_list.add(fruit_right)

        if fruit_flag == "option_watermelon":
            """ 经典模式西瓜被切开 """
            fruit_left = HalfFruit(self.window, "./images/watermelon-1.png", fruit_x - 50,fruit_y, turn_anglev_angle, v_angle, -5)
            fruit_right = HalfFruit(self.window, "./images/watermelon-2.png", fruit_x + 50,fruit_y, -turn_anglev_angle, v_angle, 5)
            self.fruit_half_list.add(fruit_left)
            self.fruit_half_list.add(fruit_right)

        if fruit_flag == 0:
            """ 苹果被切开 """
            fruit_left = HalfFruit(self.window, "./images/apple-1.png", fruit_x - 50,fruit_y, turn_anglev_angle, v_angle, -5)
            fruit_right = HalfFruit(self.window, "./images/apple-2.png", fruit_x + 50,fruit_y, -turn_anglev_angle, v_angle, 5)
            self.fruit_half_list.add(fruit_left)
            self.fruit_half_list.add(fruit_right)

        if fruit_flag == 1:
            """ 香蕉被切开 """
            fruit_left = HalfFruit(self.window, "./images/banana-1.png", fruit_x - 50,fruit_y, turn_anglev_angle, v_angle, -5)
            fruit_right = HalfFruit(self.window, "./images/banana-2.png", fruit_x + 50,fruit_y, -turn_anglev_angle, v_angle, 5)
            self.fruit_half_list.add(fruit_left)
            self.fruit_half_list.add(fruit_right)

        if fruit_flag == 2:
            """ 梨被切开 """
            fruit_left = HalfFruit(self.window, "./images/peach-1.png", fruit_x - 50,fruit_y, turn_anglev_angle, v_angle, -5)
            fruit_right = HalfFruit(self.window, "./images/peach-2.png", fruit_x + 50,fruit_y, -turn_anglev_angle, v_angle, 5)
            self.fruit_half_list.add(fruit_left)
            self.fruit_half_list.add(fruit_right)

        if fruit_flag == 3:
            """ 西瓜被切开 """
            fruit_left = HalfFruit(self.window, "./images/watermelon-1.png", fruit_x - 50,fruit_y, turn_anglev_angle, v_angle, -5)
            fruit_right = HalfFruit(self.window, "./images/watermelon-2.png", fruit_x + 50,fruit_y, -turn_anglev_angle, v_angle, 5)
            self.fruit_half_list.add(fruit_left)
            self.fruit_half_list.add(fruit_right)

        if fruit_flag == 4:
            """ 草莓被切开 """
            fruit_left = HalfFruit(self.window, "./images/strawberry-1.png", fruit_x - 50,fruit_y, turn_anglev_angle, v_angle, -5)
            fruit_right = HalfFruit(self.window, "./images/strawberry-2.png", fruit_x + 50,fruit_y, -turn_anglev_angle, v_angle, 5)
            self.fruit_half_list.add(fruit_left)
            self.fruit_half_list.add(fruit_right)

    def impact_check(self):
        # 只在鼠标左键按下时检测
        if not pygame.mouse.get_pressed()[0]:
            return None
            
        mouse_pos = pygame.mouse.get_pos()
        
        # 使用精灵组的内置碰撞检测
        clicked_options = pygame.sprite.Group([s for s in self.option_fruit_list if s.rect.collidepoint(mouse_pos)])
        clicked_fruits = pygame.sprite.Group([s for s in self.throw_fruit_list if s.rect.collidepoint(mouse_pos)])
        
        # 处理菜单选项点击
        for item in clicked_options:
            self.bgm.play_splatter()
            self.create_fruit_half(item.flag, item.rect.x, item.rect.y, item.turn_anglev_angle, item.v_angle)
            self.option_fruit_list.remove(item)
            
            if item.flag == "option_peach":
                self.mode_flag = 1
                return 1
            elif item.flag == "option_watermelon":
                self.mode_flag = 2
                return 2
            elif item.flag == "option_boom":
                return 0

        # 处理水果点击
        for item in clicked_fruits:
            # 显示刀光效果
            flash_methods = {
                0: self.knife.show_apple_flash,
                1: self.knife.show_banana_flash,
                2: self.knife.show_peach_flash,
                3: self.knife.show_watermelon_flash,
                4: self.knife.show_strawberry_flash
            }
            flash_methods.get(item.flag, lambda x, y: None)(item.rect.x, item.rect.y)

            # 计分和音效
            if item.flag != 5:
                self.bgm.play_splatter()
                # 确保计分持续进行
                base_score = 2 if item.flag == 4 else 1
                if self.mode_flag == 1:
                    self.zen_score += base_score
                elif self.mode_flag == 2:
                    self.classic_score += base_score
            # 创建切开效果
            self.create_fruit_half(item.flag, item.rect.x, item.rect.y, item.turn_anglev_angle, item.v_angle)
            self.throw_fruit_list.remove(item)

            # 特殊效果处理
            if item.flag == 4:  # 草莓减速效果
                # 5秒减速 (60fps * 5 = 300帧)
                for fruit in self.throw_fruit_list:
                    # 保存当前速度状态用于平滑过渡
                    if not hasattr(fruit, 'original_v0'):
                        fruit.original_v0 = fruit.v0
                    fruit.slow_down_time = 300
                    # 初始化减速特效
                    fruit.image = pygame.transform.scale(
                        fruit.original_image,
                        (int(fruit.original_image.get_width()*0.9),
                         int(fruit.original_image.get_height()*0.9))
                    )
            elif item.flag == 5:  # 炸弹效果
                self.bgm.play_boom()
                return 3
            return 1 #返回成功击中水果
        return None

    def check_key(self):
    
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == Manager.THROWFRUITTIME and self.mode_flag in (1, 2):
                self.create_fruit()
    def show_end_screen(self,mode,bomb=False):
        self.window.blit(self.background.image,(0,0)) #清屏

        title_font=pygame.font.Font("./images/simhei.ttf",50)
        score_font=pygame.font.Font("./images/simhei.ttf",40)
        hint_font=pygame.font.Font("./images/simhei.ttf",30)
        combo_font=pygame.font.Font("./images/simhei.ttf",36)
        
        if bomb:
            title=title_font.render("切到炸弹了！",1,(255,0,0))
        elif mode=="zen":
            title=title_font.render("时间耗尽了！",1,(255,255,255))
        else:
            title=title_font.render("游戏结束",1,(255,255,255))

        if mode=="zen":
            score_text=score_font.render(f"最终得分：{self.zen_score}",1,(255,213,156))
            best_text=score_font.render(f"历史最佳：{self.zen_best}",1,(255,179,78))
        else:
            score_text=score_font.render(f"最终得分：{self.classic_score}",1,(255,213,156))
            best_text=score_font.render(f"历史最佳：{self.classic_best}",1,(255,179,78))

        if bomb:
            hint1=hint_font.render("下次小心炸弹哦！",1,(200,200,200))
            hint2=hint_font.render("点击返回主菜单",1,(200,200,200))
        else:
            hint1=hint_font.render("点击返回主菜单",1,(200,200,200))
            hint2=None

        self.window.blit(title,(Manager.WIDTH//2-title.get_width()//2,80))
        self.window.blit(score_text,(Manager.WIDTH//2-score_text.get_width()//2,160))
        self.window.blit(best_text,(Manager.WIDTH//2-best_text.get_width()//2,210))
        self.window.blit(hint1,(Manager.WIDTH//2-hint1.get_width()//2,350))
        if hint2:
            self.window.blit(hint2,(Manager.WIDTH//2-hint2.get_width()//2,390))

        pygame.display.update()
        waiting=True
        while waiting:
            for event in pygame.event.get():
                if event.type==QUIT:
                    pygame.quit()
                    exit()
                elif event.type==MOUSEBUTTONDOWN:
                    waiting=False
                    return
        

    def zen_mode(self):
        """ 禅宗模式 """
        self.bgm.play_classic()
        score_image = Background(self.window, 10, 5, "./images/score.png")
        text = pygame.font.Font("./images/simhei.ttf", 30)  # 设置分数显示的字体
        best = pygame.font.Font("./images/simhei.ttf", 20)  # 设置历史最好分数显示的字体
        combo_font = pygame.font.Font("./images/simhei.ttf", 36)  # 设置连击数显示的字体

        # 游戏状态变量
        record_time = 60*60
        last_time = time.time()
        combo_count = 0
        last_hit_time = time.time()
        max_combo = 0
        frenzy_mode = False
        original_interval = 2000
        last_score = 0  # 用于检测分数变化

        while True:
            current_time = time.time()
            self.clock.tick(60)
            self.check_key()
            
            # 清空屏幕
            self.background_list.sprites()[0].update()
            score_image.update()

            # 更新时间
            if current_time - last_time >= 1.0:
                record_time -= 60
                last_time = current_time
                if record_time <= 10*60 and not frenzy_mode:
                    frenzy_mode = True
                    pygame.time.set_timer(Manager.THROWFRUITTIME, original_interval//2)

            # 连击系统
            if current_time - last_hit_time > 1.0:
                if combo_count > 0:
                    combo_count = 0

            # 显示时间
            if frenzy_mode:
                game_time = text.render("Time:%d"%(record_time/60), 1, (138,43,226))
            else:
                game_time = text.render("Time:%d"%(record_time/60), 1, (178,34,34))
            self.window.blit(game_time, (510, 12))

            # 显示分数
            text_score = text.render("%d" % self.zen_score, 1, (255, 213, 156))
            self.window.blit(text_score, (50, 8))
            best_score = best.render("BEST %d" % self.zen_best, 1, (255, 179, 78))
            self.window.blit(best_score, (10, 40))

            # 显示连击
            if combo_count > 1:
                combo_color = (255, 255, 0)
                if combo_count >= 10:
                    combo_color = (255, 0, 0)
                elif combo_count >= 5:
                    combo_color = (255, 165, 0)

                combo_text = combo_font.render(f"连击 x{combo_count}", 1, combo_color)
                scale = 1.0 + 0.1 * math.sin(current_time * 10)
                scaled_text = pygame.transform.scale(combo_text, 
                    (int(combo_text.get_width() * scale), 
                     int(combo_text.get_height() * scale)))
                self.window.blit(scaled_text, 
                    (Manager.WIDTH//2 - scaled_text.get_width()//2, 50))

                bonus_text = text.render(f"+{combo_count//2}", 1, combo_color)
                self.window.blit(bonus_text, 
                    (Manager.WIDTH//2 - bonus_text.get_width()//2, 100))

            # 检查击中
            temp_flag = self.impact_check()
            if temp_flag == 1:  # 成功击中水果
                combo_count += 1
                if combo_count > max_combo:
                    max_combo = combo_count
                last_hit_time = current_time
                
                # 连击加分
                if combo_count > 1:
                    bonus = combo_count // 2
                    if combo_count >= 10:
                        bonus += 2
                    elif combo_count >= 5:
                        bonus += 1
                    self.zen_score += bonus

            # 检测分数变化
            if self.zen_score != last_score:
                last_score = self.zen_score

            # 游戏结束检查
            if record_time <= 0 or temp_flag == 3:
                pygame.time.set_timer(Manager.THROWFRUITTIME, original_interval)
                if self.zen_score > self.zen_best:
                    self.update_best_score('zen_mode', self.zen_score)
                max_combo_text = text.render(f"最大连击: {max_combo}", 1, (255, 215, 0))
                self.window.blit(max_combo_text, 
                    (Manager.WIDTH//2 - max_combo_text.get_width()//2, 150))
                pygame.display.update()
                time.sleep(1)
                self.show_end_screen("zen", bomb=(temp_flag==3))
                return

            self.throw_fruit_list.update()
            self.fruit_half_list.update()
            pygame.display.update()

    def classic_mode(self):
        """ 经典模式 """
        pygame.font.init()
        self.bgm.play_classic()
        score_image = Background(self.window, 10, 5, "./images/score.png")
        text = pygame.font.Font("./images/simhei.ttf", 30)
        best = pygame.font.Font("./images/simhei.ttf", 20)
        combo_font = pygame.font.Font("./images/simhei.ttf", 36)

        x_nums = pygame.sprite.Group()
        miss_times = pygame.sprite.Group()
        xxx = Background(self.window, Manager.WIDTH - 30, 5, "./images/xxx.png")
        xx = Background(self.window, Manager.WIDTH - 60, 5, "./images/xx.png")
        x = Background(self.window, Manager.WIDTH - 90, 5, "./images/x.png")
        x_nums.add(xxx)
        x_nums.add(xx)
        x_nums.add(x)

        combo_count = 0
        last_hit_time = time.time()
        max_combo = 0
        last_score = 0  # 用于检测分数变化

        while True:
            current_time = time.time()
            self.clock.tick(60)
            self.check_key()
            
            # 清空屏幕
            self.background_list.sprites()[0].update()
            score_image.update()

            # 连击系统
            if current_time - last_hit_time > 1.0:
                if combo_count > 0:
                    combo_count = 0

            # 显示分数
            text_score = text.render("%d" % self.classic_score, 1, (255, 213, 156))
            self.window.blit(text_score, (50, 8))
            best_score = best.render("BEST %d" % self.classic_best, 1, (255, 179, 78))
            self.window.blit(best_score, (10, 40))

            # 显示连击
            if combo_count > 1:
                combo_color = (255, 255, 0)
                if combo_count >= 10:
                    combo_color = (255, 0, 0)
                elif combo_count >= 5:
                    combo_color = (255, 165, 0)

                combo_text = combo_font.render(f"连击 x{combo_count}", 1, combo_color)
                scale = 1.0 + 0.1 * math.sin(current_time * 10)
                scaled_text = pygame.transform.scale(combo_text, 
                    (int(combo_text.get_width() * scale), 
                     int(combo_text.get_height() * scale)))
                self.window.blit(scaled_text, 
                    (Manager.WIDTH//2 - scaled_text.get_width()//2, 50))

                bonus_text = text.render(f"+{combo_count//2}", 1, combo_color)
                self.window.blit(bonus_text, 
                    (Manager.WIDTH//2 - bonus_text.get_width()//2, 100))

            x_nums.update()
            miss_times.update()

            # 检查击中
            temp_flag = self.impact_check()
            if temp_flag == 1:  # 成功击中水果
                combo_count += 1
                if combo_count > max_combo:
                    max_combo = combo_count
                last_hit_time = current_time
                
                # 连击加分
                if combo_count > 1:
                    bonus = combo_count // 2
                    if combo_count >= 10:
                        bonus += 2
                    elif combo_count >= 5:
                        bonus += 1
                    self.classic_score += bonus

            # 检测分数变化
            if self.classic_score != last_score:
                last_score = self.classic_score

            # 游戏结束检查
            if temp_flag == 3 or Manager.classic_miss >= 3:
                if self.classic_score > self.classic_best:
                    self.update_best_score('classic_mode', self.classic_score)
                max_combo_text = text.render(f"最大连击: {max_combo}", 1, (255, 215, 0))
                self.window.blit(max_combo_text, 
                    (Manager.WIDTH//2 - max_combo_text.get_width()//2, 150))
                pygame.display.update()
                time.sleep(1)

                if temp_flag == 3:
                    self.bgm.play_boom()
                else:
                    self.bgm.play_over()
                time.sleep(0.4)
                self.show_end_screen("classic", bomb=(temp_flag == 3))
                Manager.classic_miss = 0
                return

            self.throw_fruit_list.update()
            self.fruit_half_list.update()

            # 处理Miss的显示
            if Manager.classic_miss == 1:
                xf = Background(self.window, Manager.WIDTH - 90, 5, "./images/xf.png")
                miss_times.add(xf)
            elif Manager.classic_miss == 2:
                xf = Background(self.window, Manager.WIDTH - 90, 5, "./images/xf.png")
                miss_times.add(xf)
                xxf = Background(self.window, Manager.WIDTH - 60, 5, "./images/xxf.png")
                miss_times.add(xxf)
            elif Manager.classic_miss >= 3:
                if self.classic_score > self.classic_best:
                    self.update_best_score('classic_mode', self.classic_score)
                max_combo_text = text.render(f"最大连击: {max_combo}", 1, (255, 215, 0))
                self.window.blit(max_combo_text, 
                    (Manager.WIDTH//2 - max_combo_text.get_width()//2, 150))
                pygame.display.update()
                time.sleep(1)
                self.bgm.play_over()
                time.sleep(0.4)
                self.show_end_screen("classic", bomb=False)
                Manager.classic_miss = 0
                return

            pygame.display.update()
            
    def update_best_score(self, mode, new_score):
        """更新最高分数"""
        file_path = './best.txt'
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        with open(file_path, 'w') as file:
            for line in lines:
                if mode in line:
                    file.write(f"{mode}:{new_score}\n")
                else:
                    file.write(line)
    def main(self):
        """ 主页 """
        self.bgm.play_menu()
        while True:
            # 设置游戏帧率
            self.clock.tick(60)
            self.background_list.update()
            self.circle_option.update()
            self.option_fruit_list.update()
            self.fruit_half_list.update()
            temp_flag = self.impact_check()
            pygame.display.update()

            if temp_flag == 1:
                self.zen_mode()
                self.__init__()
                self.bgm.play_over()
                self.bgm.play_menu()

            if temp_flag == 2:
                self.classic_mode()
                self.__init__()
                self.bgm.play_over()
                self.bgm.play_menu()

            elif temp_flag == 0:
                self.bgm.play_over()
                time.sleep(0.3)
                pygame.quit()
                exit()
            elif temp_flag == 3:
                self.__init__()
                self.bgm.play_menu()
            self.check_key()

if __name__ == '__main__':
    manager = Manager()
    manager.main()
