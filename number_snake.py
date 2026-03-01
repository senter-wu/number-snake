# -*- coding: utf-8 -*-
"""
数字贪吃蛇 - 教育类数学游戏
帮助小朋友学习10以内加减法
"""

import pygame
import random
import sys
import math
import time
import array

# 初始化pygame
pygame.init()
pygame.mixer.init()


class SoundManager:
    """音效管理器"""
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        self._generate_sounds()

    def _generate_sounds(self):
        """生成简单的音效"""
        try:
            # 正确音效 - 上升音调
            self.sounds['correct'] = self._create_multi_tone([(800, 0.1), (1000, 0.1)])

            # 错误音效 - 下降音调
            self.sounds['wrong'] = self._create_multi_tone([(400, 0.15), (300, 0.15)])

            # 吃泡泡音效 - 短促的pop声
            self.sounds['eat'] = self._create_tone(600, 0.08)

            # 撞墙音效 - 低沉的碰撞声
            self.sounds['wall'] = self._create_tone(150, 0.15)

            # 提示音效 - 叮咚声
            self.sounds['hint'] = self._create_multi_tone([(900, 0.1), (1100, 0.1)])

            # 游戏开始音效
            self.sounds['start'] = self._create_multi_tone([(500, 0.15), (700, 0.15)])

            # 游戏结束音效
            self.sounds['end'] = self._create_multi_tone([(400, 0.2), (300, 0.2), (200, 0.3)])

            print("音效生成成功！")

        except Exception as e:
            print(f"音效生成失败: {e}")
            self.enabled = False

    def _create_multi_tone(self, tones):
        """创建多音调音效"""
        sample_rate = 44100
        total_duration = sum(d for _, d in tones)
        n_samples = int(sample_rate * total_duration)

        # 生成多音调正弦波
        samples = [0] * n_samples
        current_pos = 0

        for frequency, duration in tones:
            tone_samples = int(sample_rate * duration)
            for i in range(tone_samples):
                if current_pos + i < n_samples:
                    t = float(i) / sample_rate
                    # 添加淡入淡出
                    fade_len = min(1000, tone_samples)
                    if i < fade_len:
                        envelope = i / fade_len
                    elif tone_samples - i < fade_len:
                        envelope = (tone_samples - i) / fade_len
                    else:
                        envelope = 1.0
                    value = int(32767 * envelope * math.sin(2 * math.pi * frequency * t))
                    samples[current_pos + i] = value

            current_pos += tone_samples

        # 转换为立体声
        stereo_samples = [(s, s) for s in samples]
        sound = pygame.mixer.Sound(buffer=array.array('h', [s[0] for s in stereo_samples]).tobytes())
        return sound

    def _create_tone(self, frequency, duration):
        """创建单音调"""
        sample_rate = 44100
        n_samples = int(sample_rate * duration)

        # 生成正弦波
        samples = []
        for i in range(n_samples):
            t = float(i) / sample_rate
            # 添加淡入淡出
            fade_len = min(1000, n_samples)
            if i < fade_len:
                envelope = i / fade_len
            elif n_samples - i < fade_len:
                envelope = (n_samples - i) / fade_len
            else:
                envelope = 1.0
            value = int(32767 * envelope * math.sin(2 * math.pi * frequency * t))
            samples.append((value, value))

        sound = pygame.mixer.Sound(buffer=array.array('h', [s[0] for s in samples]).tobytes())
        return sound

    def play(self, sound_name):
        """播放音效"""
        if self.enabled and sound_name in self.sounds:
            self.sounds[sound_name].play()


# 创建全局音效管理器
sound_manager = SoundManager()

# 颜色定义 (R, G, B)
COLORS = {
    'GREEN': (46, 204, 113),      # 1-5 绿色
    'YELLOW': (241, 196, 15),     # 6-10 黄色
    'ORANGE': (230, 126, 34),     # 11-15 橙色
    'RED': (231, 76, 60),         # 16-20 红色
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'GRAY': (128, 128, 128),
    'LIGHT_GRAY': (200, 200, 200),
    'SNAKE': (138, 43, 226),      # 蛇的颜色 - 蓝紫色
    'BG_COLOR': (245, 250, 255),  # 浅蓝白渐变底色
    'GAME_BG_COLOR': (255, 255, 255),  # 游戏区域白色背景
    'HEADER_BG': (135, 206, 250),  # 顶部信息栏天蓝色
    'TEXT_COLOR': (52, 73, 94),    # 深灰蓝色文字
}

# 获取屏幕信息
SCREEN_INFO = pygame.display.Info()
SCREEN_WIDTH = min(1200, SCREEN_INFO.current_w - 100)
SCREEN_HEIGHT = min(800, SCREEN_INFO.current_h - 100)

# 游戏区域设置 - 优化布局，增大游戏区域占比
GAME_MARGIN = 55  # 顶部信息栏高度（减小）
GAME_AREA_TOP = GAME_MARGIN + 5

# 泡泡设置 - 增大尺寸
BUBBLE_RADIUS_MIN = 30
BUBBLE_RADIUS_MAX = 42
BUBBLE_COUNT_MIN = 5
BUBBLE_COUNT_MAX = 10

# 蛇的设置 - 增大尺寸
SNAKE_SIZE = 22
SNAKE_SPEED = 3  # 减慢速度

# 游戏常量
HINT_TIME = 20  # 提示时间（秒）
MESSAGE_TIMER_BASE = 60  # 消息计时器基准值（帧）
MESSAGE_TIMER_LONG = 120  # 长消息计时器
NEW_ROUND_DELAY = 90  # 成功后开始新轮延迟（3秒 at 30fps）
SHOW_EQUATION_DELAY = 90  # 等式显示时间（3秒 at 30fps）
RESET_BUBBLES_DELAY = 60  # 失败后恢复泡泡延迟（帧）约2秒
WALL_HINT_DELAY = 30  # 撞墙提示显示时间（帧）
TRANSPARENT_DURATION = 30  # 咬到自己透明持续时间（帧）
GROW_LENGTH = 5  # 成功后蛇变长的格数
SHRINK_LENGTH = 1  # 失败后蛇变短的格数

# 字体 - 优化大小，提高可读性
try:
    FONT_PATH = pygame.font.match_font('microsoftyahei')
    if FONT_PATH is None:
        FONT_PATH = pygame.font.match_font('simhei')
    TITLE_FONT = pygame.font.Font(FONT_PATH, 38)
    INFO_FONT = pygame.font.Font(FONT_PATH, 26)
    SCORE_FONT = pygame.font.Font(FONT_PATH, 30)
    BUBBLE_FONT = pygame.font.Font(FONT_PATH, 32)  # 增大泡泡内数字字体
except:
    TITLE_FONT = pygame.font.SysFont('microsoftyahei', 38)
    INFO_FONT = pygame.font.SysFont('microsoftyahei', 26)
    SCORE_FONT = pygame.font.SysFont('microsoftyahei', 30)
    BUBBLE_FONT = pygame.font.SysFont('microsoftyahei', 32)


def draw_flag_icon(screen, x, y, size=20):
    """绘制小旗子图标 - 代表目标"""
    # 旗杆
    pygame.draw.line(screen, (139, 90, 43), (x, y - size//2), (x, y + size//2), 2)
    # 旗帜
    pygame.draw.polygon(screen, (255, 100, 100), [
        (x, y - size//2),
        (x + size//2, y - size//3),
        (x, y)
    ])
    pygame.draw.polygon(screen, (200, 50, 50), [
        (x, y - size//2),
        (x + size//2, y - size//3),
        (x, y)
    ], 1)


def draw_star_icon(screen, x, y, size=18):
    """绘制星星图标 - 代表得分"""
    # 外圈圆
    pygame.draw.circle(screen, (255, 215, 0), (x, y), size//2, 2)
    # 内部星星
    pygame.draw.circle(screen, (255, 215, 0), (x, y), size//4)


def draw_refresh_icon(screen, x, y, size=18):
    """绘制循环图标 - 代表轮次"""
    pygame.draw.arc(screen, (100, 150, 200), (x-size//2, y-size//2, size, size), 0, 1.5, 2)


def draw_bubble_icon(screen, x, y, size=16, color=(100, 200, 255)):
    """绘制泡泡图标"""
    pygame.draw.circle(screen, color, (x, y), size//2, 2)
    # 高光
    pygame.draw.circle(screen, (255, 255, 255), (x - 2, y - 2), 2)


def draw_clock_icon(screen, x, y, size=18):
    """绘制时钟图标 - 代表时间"""
    pygame.draw.circle(screen, (80, 80, 80), (x, y), size//2, 2)
    # 指针
    pygame.draw.line(screen, (80, 80, 80), (x, y), (x, y - 4), 2)
    pygame.draw.line(screen, (80, 80, 80), (x, y), (x + 3, y), 2)


def draw_keyboard_icon(screen, x, y, size=20):
    """绘制键盘图标 - 代表操作"""
    # 外框
    pygame.draw.rect(screen, (150, 150, 150), (x - size//2, y - size//4, size, size//2), 1)
    # 方向键指示
    pygame.draw.polygon(screen, (100, 100, 100), [
        (x, y - size//3),
        (x - size//4, y + size//6),
        (x + size//4, y + size//6)
    ])


def draw_hand_icon(screen, x, y, size=16):
    """绘制手型图标 - 代表暂停"""
    # 简化的手型
    pygame.draw.circle(screen, (200, 150, 100), (x, y), size//2, 2)


def get_bubble_color(number):
    """根据数字返回泡泡颜色"""
    if 1 <= number <= 5:
        return COLORS['GREEN']
    elif 6 <= number <= 10:
        return COLORS['YELLOW']
    elif 11 <= number <= 15:
        return COLORS['ORANGE']
    else:
        return COLORS['RED']


class Bubble:
    """数字泡泡类"""
    def __init__(self, number, x, y, radius=None):
        self.number = number
        self.x = x
        self.y = y
        self.radius = radius if radius else random.randint(BUBBLE_RADIUS_MIN, BUBBLE_RADIUS_MAX)
        self.color = get_bubble_color(number)
        self.float_offset = random.random() * 2 * 3.14159
        self.float_speed = 0.02 + random.random() * 0.01
        self.collected = False
        self.glow = False
        self.target_glow = False

    def update(self):
        """更新泡泡浮动动画"""
        self.float_offset += self.float_speed
        self.y = self.y + math.sin(self.float_offset) * 0.3

        # 发光效果平滑过渡
        if self.target_glow and not self.glow:
            self.glow = True
        elif not self.target_glow and self.glow:
            self.glow = False

    def draw(self, screen):
        """绘制泡泡"""
        # 发光效果 - 更平滑的渐变
        if self.glow:
            for i in range(5, 0, -1):
                alpha = 40 * i
                glow_radius = self.radius + i * 4
                s = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                color_with_alpha = (*self.color, alpha)
                pygame.draw.circle(s, color_with_alpha, (glow_radius, glow_radius), glow_radius)
                screen.blit(s, (self.x - glow_radius, self.y - glow_radius))

        # 泡泡主体
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        # 高光 - 更可爱的位置，减小尺寸
        highlight_x = self.x - self.radius * 0.25
        highlight_y = self.y - self.radius * 0.25
        pygame.draw.circle(screen, (255, 255, 255), (int(highlight_x), int(highlight_y)), int(self.radius * 0.15))

        # 边框 - 细边框
        pygame.draw.circle(screen, (255, 255, 255, 180), (int(self.x), int(self.y)), self.radius, 2)

        # 数字 - 深色文字+阴影，提高对比度
        text_shadow = BUBBLE_FONT.render(str(self.number), True, (0, 0, 0))
        text = BUBBLE_FONT.render(str(self.number), True, COLORS['TEXT_COLOR'])
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        shadow_rect = text_shadow.get_rect(center=(int(self.x)+2, int(self.y)+2))
        screen.blit(text_shadow, shadow_rect)
        screen.blit(text, text_rect)

    def is_clicked(self, pos):
        """检查是否点击了泡泡"""
        distance = ((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2) ** 0.5
        return distance <= self.radius

    def collides_with(self, other):
        """检查是否与其他泡泡重叠"""
        distance = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        return distance < self.radius + other.radius + 5


class Snake:
    """贪吃蛇类"""
    def __init__(self):
        self.reset()

    def reset(self):
        """重置蛇"""
        # 初始化5个连续位置，蛇头在右边
        start_x = SCREEN_WIDTH // 2
        start_y = (SCREEN_HEIGHT + GAME_AREA_TOP) // 2
        self.positions = [
            (start_x - 14 * SNAKE_SIZE, start_y),
            (start_x - 13 * SNAKE_SIZE, start_y),
            (start_x - 12 * SNAKE_SIZE, start_y),
            (start_x - 11 * SNAKE_SIZE, start_y),
            (start_x - 10 * SNAKE_SIZE, start_y),
            (start_x - 9 * SNAKE_SIZE, start_y),
            (start_x - 8 * SNAKE_SIZE, start_y),
            (start_x - 7 * SNAKE_SIZE, start_y),
            (start_x - 6 * SNAKE_SIZE, start_y),
            (start_x - 5 * SNAKE_SIZE, start_y),
            (start_x - 4 * SNAKE_SIZE, start_y),
            (start_x - 3 * SNAKE_SIZE, start_y),
            (start_x - 2 * SNAKE_SIZE, start_y),
            (start_x - SNAKE_SIZE, start_y),
            (start_x, start_y)
        ]
        self.direction = (SNAKE_SPEED, 0)
        self.length = 15  # 初始长度增加2倍（5*3=15）
        self.growing = False
        self.shrinking = False
        self.transparent = False
        self.transparent_timer = 0
        self.wall_hit = False  # 撞墙标志

    def set_direction(self, dx, dy):
        """设置移动方向"""
        if self.direction[0] == 0 and dx != 0:
            self.direction = (dx * SNAKE_SPEED, 0)
        elif self.direction[1] == 0 and dy != 0:
            self.direction = (0, dy * SNAKE_SPEED)

    def update(self):
        """更新蛇的位置"""
        self.wall_hit = False  # 重置撞墙标志
        head_x, head_y = self.positions[0]

        # 计算新头部位置
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        # 边界检测 - 撞墙转向
        if new_head[0] < 0:
            new_head = (0, new_head[1])
            self.direction = (0, SNAKE_SPEED)  # 向下
            self.wall_hit = True
        elif new_head[0] > SCREEN_WIDTH:
            new_head = (SCREEN_WIDTH, new_head[1])
            self.direction = (0, -SNAKE_SPEED)  # 向上
            self.wall_hit = True
        elif new_head[1] < GAME_AREA_TOP:
            new_head = (new_head[0], GAME_AREA_TOP)
            self.direction = (SNAKE_SPEED, 0)  # 向右
            self.wall_hit = True
        elif new_head[1] > SCREEN_HEIGHT:
            new_head = (new_head[0], SCREEN_HEIGHT)
            self.direction = (-SNAKE_SPEED, 0)  # 向左
            self.wall_hit = True

        # 咬到自己 - 变透明
        if new_head in self.positions[1:]:
            self.transparent = True
            self.transparent_timer = TRANSPARENT_DURATION
            return

        # 更新位置
        self.positions.insert(0, new_head)

        # 处理变长/变短
        if self.growing:
            self.growing = False
            self.length += GROW_LENGTH  # 成功变长3格
        elif self.shrinking:
            self.shrinking = False
            if self.length > SHRINK_LENGTH:
                self.length -= SHRINK_LENGTH  # 失败变短1格
        else:
            if len(self.positions) > self.length:
                self.positions.pop()

        # 更新透明状态
        if self.transparent:
            self.transparent_timer -= 1
            if self.transparent_timer <= 0:
                self.transparent = False

    def draw(self, screen):
        """绘制蛇 - 可爱版本带眼睛微笑"""
        # 先绘制身体
        for i, pos in enumerate(self.positions[1:], 1):
            color = COLORS['SNAKE']
            body_color = tuple(min(255, c + 15) for c in color)
            pygame.draw.circle(screen, body_color, pos, SNAKE_SIZE - 2)
            # 高光
            pygame.draw.circle(screen, (200, 180, 255), (pos[0] - 6, pos[1] - 6), 6)

        # 单独绘制头部
        if self.positions:
            pos = self.positions[0]
            color = COLORS['SNAKE']
            # 头部身体
            pygame.draw.circle(screen, color, pos, SNAKE_SIZE - 2)
            pygame.draw.circle(screen, (200, 180, 255), (pos[0] - 6, pos[1] - 6), 6)

            # 眼睛位置
            eye_offset = 6
            if self.direction[0] > 0:  # 向右
                eye1 = (pos[0] + eye_offset, pos[1] - 5)
                eye2 = (pos[0] + eye_offset, pos[1] + 5)
            elif self.direction[0] < 0:  # 向左
                eye1 = (pos[0] - eye_offset, pos[1] - 5)
                eye2 = (pos[0] - eye_offset, pos[1] + 5)
            elif self.direction[1] > 0:  # 向下
                eye1 = (pos[0] - 5, pos[1] + eye_offset)
                eye2 = (pos[0] + 5, pos[1] + eye_offset)
            else:  # 向上
                eye1 = (pos[0] - 5, pos[1] - eye_offset)
                eye2 = (pos[0] + 5, pos[1] - eye_offset)

            # 绘制眼睛（白色底+黑色眼珠+白色眼神光）
            pygame.draw.circle(screen, (255, 255, 255), eye1, 7)
            pygame.draw.circle(screen, (255, 255, 255), eye2, 7)
            pygame.draw.circle(screen, (20, 20, 20), eye1, 4)
            pygame.draw.circle(screen, (20, 20, 20), eye2, 4)
            # 眼神光
            pygame.draw.circle(screen, (255, 255, 255), (eye1[0]-1, eye1[1]-1), 2)
            pygame.draw.circle(screen, (255, 255, 255), (eye2[0]-1, eye2[1]-1), 2)

            # 绘制微笑
            if self.direction[0] > 0:  # 向右
                smile_center = (pos[0] + 8, pos[1])
            elif self.direction[0] < 0:  # 向左
                smile_center = (pos[0] - 8, pos[1])
            elif self.direction[1] > 0:  # 向下
                smile_center = (pos[0], pos[1] + 8)
            else:  # 向上
                smile_center = (pos[0], pos[1] - 8)

            # 用小圆点画微笑
            for dx in range(-3, 4):
                for dy in range(-2, 3):
                    if dx*dx + dy*dy <= 9:
                        pygame.draw.circle(screen, (200, 100, 100), (smile_center[0] + dx, smile_center[1] + dy), 1)

            # 脸颊红晕
            cheek_dist = 10
            if self.direction[0] > 0:  # 向右
                cheek1 = (pos[0] + cheek_dist, pos[1] + 2)
                cheek2 = (pos[0] - cheek_dist, pos[1] + 2)
            elif self.direction[0] < 0:  # 向左
                cheek1 = (pos[0] + cheek_dist, pos[1] + 2)
                cheek2 = (pos[0] - cheek_dist, pos[1] + 2)
            elif self.direction[1] > 0:  # 向下
                cheek1 = (pos[0] + 2, pos[1] + cheek_dist)
                cheek2 = (pos[0] - 2, pos[1] + cheek_dist)
            else:  # 向上
                cheek1 = (pos[0] + 2, pos[1] - cheek_dist)
                cheek2 = (pos[0] - 2, pos[1] - cheek_dist)
            pygame.draw.circle(screen, (255, 180, 180), cheek1, 4)
            pygame.draw.circle(screen, (255, 180, 180), cheek2, 4)

    def get_head(self):
        """获取蛇头位置"""
        return self.positions[0]


class Game:
    """游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("数字贪吃蛇 - 学数学")
        self.clock = pygame.time.Clock()

        # 音效开关必须在reset_game之前初始化
        self.sound_enabled = True  # 音效开关

        self.reset_game()
        self.running = True
        self.paused = False
        self.game_over = False
        self.start_time = 0
        self.total_time = 180  # 默认3分钟
        self.last_think_time = 0
        self.hint_shown = False
        self.target_pulse_timer = 0  # 目标数字脉冲动画

        # 消息显示
        self.message = ""
        self.message_timer = 0
        self.wall_collision_shown = False  # 撞墙提示标志
        self.pending_new_round = False  # 待开始新的一轮
        self.new_round_delay = 0  # 新一轮延迟计数器
        self.pending_reset_bubbles = False  # 待恢复泡泡
        self.reset_bubbles_delay = 0  # 恢复泡泡延迟计数器
        self.showing_equation = False  # 显示等式状态
        self.equation_timer = 0  # 等式显示计时器
        self.pending_grow = False  # 等待蛇变长
        self.pending_shrink = False  # 等待蛇变短

        # 背景浮动泡泡 - 增加动感
        self.bg_bubbles = []
        for _ in range(6):
            self.bg_bubbles.append({
                'x': random.randint(50, SCREEN_WIDTH - 50),
                'y': random.randint(50, SCREEN_HEIGHT - 50),
                'size': random.randint(8, 16),
                'speed': random.uniform(0.3, 0.8),
                'offset': random.random() * math.pi * 2,
                'color': random.choice([
                    (255, 182, 193),  # 粉色
                    (173, 216, 230),  # 浅蓝
                    (255, 218, 185),  # 浅橙
                    (221, 160, 221),  # 浅紫
                    (144, 238, 144),  # 浅绿
                ])
            })

    def reset_game(self):
        """重置游戏"""
        self.snake = Snake()
        self.bubbles = []
        self.score = 0
        self.current_round = 1
        self.target_number = 0
        self.operation = ""  # "add" or "subtract"
        self.collected_numbers = []  # 当前收集的数字
        self.hint_shown = False
        self.wall_collision_shown = False
        self.generate_new_round()
        if self.sound_enabled:
            sound_manager.play('start')  # 播放开始音效

    def generate_new_round(self):
        """生成新的一轮"""
        # 增加轮次计数
        self.current_round += 1

        # 重置收集的数字
        self.collected_numbers = []
        self.hint_shown = False
        self.last_think_time = time.time()
        self.first_eat_time = 0  # 重置第一次吃泡泡的时间

        # 生成目标数字 (1-20)
        self.target_number = random.randint(1, 20)

        # 随机选择运算方式
        self.operation = random.choice(["add", "subtract"])

        # 生成泡泡数量
        bubble_count = random.randint(BUBBLE_COUNT_MIN, BUBBLE_COUNT_MAX)

        # 生成数字泡泡，确保有解
        self.bubbles = self.generate_bubbles(bubble_count, self.target_number, self.operation)

    def generate_bubbles(self, count, target, operation):
        """生成数字泡泡，确保有解 - 强制生成保证有解的组合"""
        max_attempts = 50

        for _ in range(max_attempts):
            # 首先确保有一个正确的解
            if operation == "add":
                # 随机生成两个数字，使它们的和等于目标（都在1-20范围内）
                num1 = random.randint(1, min(target - 1, 20)) if target > 1 else random.randint(1, 10)
                num2 = target - num1
                # 确保 num2 在 1-20 范围内，如果不在则重新生成
                while num2 < 1 or num2 > 20:
                    num1 = random.randint(1, min(target - 1, 20)) if target > 1 else random.randint(1, 10)
                    num2 = target - num1
            else:  # subtract
                # 随机生成两个数字，使它们的差等于目标
                # 确保大数-小数=目标，且两个数都在1-20范围内
                num2 = random.randint(1, 20 - target)  # 小数，最大为 20 - target
                num1 = num2 + target  # 大数 = 小数 + 目标

            solution_nums = [num1, num2]

            # 生成剩余的数字
            numbers = solution_nums.copy()

            while len(numbers) < count:
                num = random.randint(1, 20)
                if num not in numbers:
                    numbers.append(num)

            # 生成泡泡位置
            new_bubbles = []
            snake_safe_distance = 80  # 蛇周围的安全距离
            # UI区域安全距离（避开顶部目标显示和中间等式显示）
            # 扩大安全区域避免与文字重叠
            ui_safe_top = 120  # 顶部安全线（避开目标显示）
            ui_safe_bottom = SCREEN_HEIGHT - 100  # 底部安全线（避开消息显示）
            ui_center_x = SCREEN_WIDTH // 2
            ui_center_width = 250  # 中间区域宽度

            for num in numbers:
                attempts = 0
                while attempts < 100:  # 增加尝试次数
                    x = random.randint(BUBBLE_RADIUS_MAX + 10, SCREEN_WIDTH - BUBBLE_RADIUS_MAX - 10)
                    y = random.randint(ui_safe_top + 30, ui_safe_bottom - 30)

                    # 检查是否与现有泡泡重叠
                    valid = True
                    for b in new_bubbles:
                        if b.collides_with(Bubble(num, x, y)):
                            valid = False
                            break

                    # 检查是否与贪吃蛇位置重叠（确保蛇附近不生成泡泡）
                    if valid and hasattr(self, 'snake'):
                        for seg in self.snake.positions:
                            dist = ((x - seg[0]) ** 2 + (y - seg[1]) ** 2) ** 0.5
                            if dist < snake_safe_distance:
                                valid = False
                                break

                    # 检查是否在UI安全区域内（避开目标显示和等式显示）
                    if valid:
                        # 避开顶部区域
                        if y < ui_safe_top:
                            valid = False
                        # 避开底部区域
                        elif y > ui_safe_bottom:
                            valid = False
                        # 避开中间等式显示区域（整个中间带都不生成泡泡）
                        elif abs(x - ui_center_x) < ui_center_width // 2:
                            valid = False

                    if valid:
                        new_bubbles.append(Bubble(num, x, y))
                        break
                    attempts += 1
                else:
                    break  # 如果尝试太多次，重新生成位置

            if len(new_bubbles) == count:
                # 再次验证有解
                if self._verify_solution(new_bubbles, target, operation):
                    return new_bubbles

        # 如果无法生成无重叠的泡泡，降低要求（允许重叠）
        numbers = solution_nums.copy()
        while len(numbers) < count:
            num = random.randint(1, 20)
            if num not in numbers:
                numbers.append(num)

        new_bubbles = []
        # UI区域安全距离 - 与前面保持一致
        ui_safe_top = 120
        ui_safe_bottom = SCREEN_HEIGHT - 100
        ui_center_x = SCREEN_WIDTH // 2
        ui_center_width = 250

        for num in numbers:
            # 尝试生成不与UI重叠的泡泡
            valid = False
            for _ in range(100):
                x = random.randint(BUBBLE_RADIUS_MAX + 10, SCREEN_WIDTH - BUBBLE_RADIUS_MAX - 10)
                y = random.randint(ui_safe_top + 30, ui_safe_bottom - 30)
                # 避开中间区域
                if abs(x - ui_center_x) < ui_center_width // 2:
                    continue
                valid = True
                break
            if not valid:
                x = random.randint(BUBBLE_RADIUS_MAX + 10, SCREEN_WIDTH - BUBBLE_RADIUS_MAX - 10)
                y = random.randint(ui_safe_top + 30, ui_safe_bottom - 30)
            new_bubbles.append(Bubble(num, x, y))
        return new_bubbles

    def _verify_solution(self, bubbles, target, operation):
        """验证泡泡是否有解"""
        numbers = [b.number for b in bubbles]
        if operation == "add":
            for i in range(len(numbers)):
                for j in range(i + 1, len(numbers)):
                    if numbers[i] + numbers[j] == target:
                        return True
        else:
            for i in range(len(numbers)):
                for j in range(len(numbers)):
                    if i != j and abs(numbers[i] - numbers[j]) == target:
                        return True
        return False

    def handle_input(self):
        """处理输入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reset_game()
                    self.game_over = False
                    self.start_time = time.time()
                elif event.key == pygame.K_m:
                    self.sound_enabled = not self.sound_enabled

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over:
                    self.reset_game()
                    self.game_over = False
                    self.start_time = time.time()
                    return

        # 键盘控制蛇的方向
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.snake.set_direction(-1, 0)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.snake.set_direction(1, 0)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.snake.set_direction(0, -1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.snake.set_direction(0, 1)

    def collect_number(self, bubble):
        """收集数字"""
        if bubble.collected:
            return

        bubble.collected = True
        self.collected_numbers.append(bubble.number)
        if self.sound_enabled:
            sound_manager.play('eat')  # 播放吃泡泡音效

        # 记录第一次吃泡泡的时间（用于提示计时）
        if len(self.collected_numbers) == 1:
            self.first_eat_time = time.time()

        # 检查是否收集了足够的数字
        if len(self.collected_numbers) == 2:
            # 判断是否正确
            num1, num2 = self.collected_numbers
            result = 0

            if self.operation == "add":
                result = num1 + num2
            else:
                result = abs(num1 - num2)

            # 暂停游戏并显示等式（让小朋友学习）
            self.showing_equation = True
            self.equation_timer = SHOW_EQUATION_DELAY
            self.pending_grow = False  # 重置等待生长标志
            self.pending_shrink = False  # 重置等待缩短标志

            if result == self.target_number:
                # 正确！等式显示结束后再变长
                self.pending_grow = True
                self.score += 1
                self.message = "真棒！"
                self.message_timer = MESSAGE_TIMER_BASE
                if self.sound_enabled:
                    sound_manager.play('correct')  # 播放正确音效
                # 等式显示完后开始新的一轮
                self.pending_new_round = True
                self.new_round_delay = NEW_ROUND_DELAY
            else:
                # 错误！等式显示结束后再变短
                self.pending_shrink = True
                if self.score > 0:
                    self.score -= 1
                self.message = "再想想哦~"
                self.message_timer = MESSAGE_TIMER_BASE
                if self.sound_enabled:
                    sound_manager.play('wrong')  # 播放错误音效
                # 等式显示完后恢复泡泡
                self.pending_reset_bubbles = True
                self.reset_bubbles_delay = RESET_BUBBLES_DELAY

        elif len(self.collected_numbers) > 2:
            # 重新开始这轮
            self.collected_numbers = [bubble.number]
            self.reset_bubbles()

    def reset_bubbles(self):
        """恢复所有泡泡"""
        for bubble in self.bubbles:
            bubble.collected = False
        # 清空收集的数字列表
        self.collected_numbers = []

    def check_hint(self):
        """检查是否需要显示提示"""
        if self.hint_shown:
            return

        # 只有在第一次吃泡泡后20秒才显示提示
        if not hasattr(self, 'first_eat_time') or self.first_eat_time == 0:
            return

        elapsed = time.time() - self.first_eat_time
        if elapsed > HINT_TIME:
            self.hint_shown = True
            # 找到正确的数字组合
            correct_nums = self.find_solution()
            if correct_nums:
                for bubble in self.bubbles:
                    if bubble.number in correct_nums:
                        bubble.target_glow = True
                # 显示提示消息
                self.message = f"{self.target_number}可以分成{correct_nums[0]}和{correct_nums[1]}哦，找找看~"
                self.message_timer = MESSAGE_TIMER_LONG
                if self.sound_enabled:
                    sound_manager.play('hint')  # 播放提示音效

    def find_solution(self):
        """找到正确的数字组合"""
        available = [b.number for b in self.bubbles if not b.collected]

        if self.operation == "add":
            for i in range(len(available)):
                for j in range(i + 1, len(available)):
                    if available[i] + available[j] == self.target_number:
                        return [available[i], available[j]]
        else:
            for i in range(len(available)):
                for j in range(len(available)):
                    if i != j and abs(available[i] - available[j]) == self.target_number:
                        return [available[i], available[j]]
        return None

    def update(self):
        """更新游戏状态"""
        if self.paused or self.game_over:
            return

        # 检查时间
        if self.start_time == 0:
            self.start_time = time.time()

        elapsed = time.time() - self.start_time
        remaining = self.total_time - elapsed

        if remaining <= 0:
            self.game_over = True
            if self.sound_enabled:
                sound_manager.play('end')  # 播放结束音效
            return

        # 显示等式时暂停游戏（让小朋友学习）
        if self.showing_equation:
            self.equation_timer -= 1
            # 继续更新脉冲动画
            self.target_pulse_timer += 0.1
            # 等式显示时间结束后继续游戏并开始下一轮
            if self.equation_timer <= 0:
                self.showing_equation = False
                # 等式结束后让蛇变长/变短
                if self.pending_grow:
                    self.snake.growing = True
                    self.pending_grow = False
                if self.pending_shrink:
                    self.snake.shrinking = True
                    self.pending_shrink = False
                # 清除消息
                self.message = ""
                # 清除发光效果
                for bubble in self.bubbles:
                    bubble.target_glow = False
                # 立即开始下一轮
                if self.pending_new_round:
                    self.generate_new_round()
                    self.pending_new_round = False
            return

        # 更新蛇
        self.snake.update()

        # 更新目标数字脉冲动画
        self.target_pulse_timer += 0.1

        # 检测蛇与泡泡的碰撞（自动收集）
        snake_head = self.snake.get_head()
        for bubble in self.bubbles:
            if not bubble.collected:
                distance = ((snake_head[0] - bubble.x) ** 2 + (snake_head[1] - bubble.y) ** 2) ** 0.5
                if distance < SNAKE_SIZE + bubble.radius:
                    self.collect_number(bubble)
                    break

        # 检测撞墙并显示提示
        if self.snake.wall_hit and not self.wall_collision_shown:
            self.message = "哎呀，转个弯~"
            self.message_timer = WALL_HINT_DELAY
            if self.sound_enabled:
                sound_manager.play('wall')  # 播放撞墙音效
            self.wall_collision_shown = True
        elif not self.snake.wall_hit:
            self.wall_collision_shown = False

        # 更新泡泡
        for bubble in self.bubbles:
            bubble.update()

        # 检查提示
        self.check_hint()

        # 处理恢复泡泡延迟
        if self.pending_reset_bubbles:
            self.reset_bubbles_delay -= 1
            if self.reset_bubbles_delay <= 0:
                self.pending_reset_bubbles = False
                self.reset_bubbles()

        # 更新消息计时器
        if self.message_timer > 0 and not self.showing_equation:
            self.message_timer -= 1
            if self.message_timer == 0:
                # 清除发光效果
                for bubble in self.bubbles:
                    bubble.target_glow = False

    def draw(self):
        """绘制游戏画面"""
        # 背景 - 渐变效果
        self.screen.fill(COLORS['BG_COLOR'])

        # 绘制浮动背景泡泡 - 动感效果
        current_time = time.time()
        for bubble in self.bg_bubbles:
            # 浮动动画
            float_y = bubble['y'] + math.sin(current_time * bubble['speed'] + bubble['offset']) * 15
            # 半透明效果
            s = pygame.Surface((bubble['size'] * 2, bubble['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*bubble['color'], 100), (bubble['size'], bubble['size']), bubble['size'])
            self.screen.blit(s, (bubble['x'] - bubble['size'], float_y - bubble['size']))

        # 绘制可爱云朵装饰（在游戏区域之上）
        cloud_positions = [
            (80, 120), (SCREEN_WIDTH - 100, 150), (SCREEN_WIDTH // 2 - 50, 100)
        ]
        for cx, cy in cloud_positions:
            cloud_offset = math.sin(current_time * 0.5) * 5
            # 绘制三朵云
            pygame.draw.circle(self.screen, (255, 255, 255), (int(cx + cloud_offset), int(cy)), 25)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(cx + 20 + cloud_offset), int(cy - 5)), 20)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(cx - 15 + cloud_offset), int(cy + 5)), 18)

        # 绘制小星星装饰（在游戏区域之上）
        star_positions = [
            (150, 200), (SCREEN_WIDTH - 150, 250), (300, 350), (SCREEN_WIDTH - 250, 400)
        ]
        for sx, sy in star_positions:
            star_alpha = int(150 + 100 * math.sin(current_time * 2 + sx))
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            # 简单星星形状
            pygame.draw.circle(s, (255, 215, 0, star_alpha), (8, 8), 8)
            self.screen.blit(s, (sx - 8, sy - 8))

        # 绘制游戏区域背景 - 白色带圆角
        game_bg_rect = pygame.Rect(5, GAME_AREA_TOP - 5, SCREEN_WIDTH - 10, SCREEN_HEIGHT - GAME_AREA_TOP)
        pygame.draw.rect(self.screen, COLORS['GAME_BG_COLOR'], game_bg_rect, border_radius=15)
        pygame.draw.rect(self.screen, (200, 220, 240), game_bg_rect, 2, border_radius=15)

        # 绘制可爱云朵装饰（在游戏区域之上）
        for cx, cy in cloud_positions:
            cloud_offset = math.sin(current_time * 0.5) * 5
            # 绘制三朵云
            pygame.draw.circle(self.screen, (255, 255, 255), (int(cx + cloud_offset), int(cy)), 25)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(cx + 20 + cloud_offset), int(cy - 5)), 20)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(cx - 15 + cloud_offset), int(cy + 5)), 18)

        # 绘制小星星装饰（在游戏区域之上）
        for sx, sy in star_positions:
            star_alpha = int(150 + 100 * math.sin(current_time * 2 + sx))
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            # 简单星星形状
            pygame.draw.circle(s, (255, 215, 0, star_alpha), (8, 8), 8)
            self.screen.blit(s, (sx - 8, sy - 8))

        # 绘制顶部信息栏背景 - 卡通彩虹风格
        header_rect = pygame.Rect(10, 10, SCREEN_WIDTH - 20, GAME_MARGIN - 10)

        # 绘制彩虹渐变背景
        rainbow_colors = [
            (255, 182, 193),  # 粉色
            (255, 218, 185),  # 浅橙
            (255, 255, 224),  # 浅黄
            (173, 216, 230),  # 浅蓝
            (221, 160, 221),  # 浅紫
        ]
        header_height = GAME_MARGIN - 10
        color_band_height = header_height // len(rainbow_colors)
        for i, color in enumerate(rainbow_colors):
            y = 10 + i * color_band_height
            h = color_band_height if i < len(rainbow_colors) - 1 else header_height - i * color_band_height
            pygame.draw.rect(self.screen, color, (10, y, SCREEN_WIDTH - 20, h))

        # 白色半透明遮罩让文字更清晰
        pygame.draw.rect(self.screen, (255, 255, 255, 180), header_rect, border_radius=12)
        # 彩色边框 - 天蓝色
        pygame.draw.rect(self.screen, (135, 206, 250), header_rect, 3, border_radius=12)

        # 绘制信息栏底部分隔线 - 改为虚线效果
        pygame.draw.line(self.screen, (220, 220, 220), (20, GAME_MARGIN - 5), (SCREEN_WIDTH - 20, GAME_MARGIN - 5), 2)

        # 绘制信息 - 紧凑布局 带图形图标（图标与文字垂直居中对齐）
        info_y = 16
        icon_x = 20
        icon_size = 26  # 图标大小
        # 文字高度30，图标高度26，垂直居中对齐需要偏移 (30-26)/2 = 2
        icon_y_offset = 2

        # 目标 - 小旗子图标
        draw_flag_icon(self.screen, icon_x, info_y + icon_y_offset + 11, icon_size)
        target_text = SCORE_FONT.render(f"目标 {self.target_number}", True, COLORS['TEXT_COLOR'])
        self.screen.blit(target_text, (icon_x + 30, info_y))

        # 本轮计算方式 - 用颜色区分
        icon_x2 = 165
        op_text = "当前轮+" if self.operation == "add" else "当前轮-"
        op_color = COLORS['GREEN'] if self.operation == "add" else COLORS['ORANGE']
        op_render = SCORE_FONT.render(op_text, True, op_color)
        self.screen.blit(op_render, (icon_x2, info_y))

        # 分数 - 星星图标
        icon_x3 = 315
        draw_star_icon(self.screen, icon_x3, info_y + icon_y_offset + 11, icon_size - 2)
        score_text = SCORE_FONT.render(f"得分 {self.score}", True, COLORS['TEXT_COLOR'])
        self.screen.blit(score_text, (icon_x3 + 26, info_y))

        # 轮次 - 刷新图标
        icon_x4 = 465
        draw_refresh_icon(self.screen, icon_x4, info_y + icon_y_offset + 11, icon_size - 2)
        round_text = INFO_FONT.render(f"第{self.current_round}轮", True, COLORS['TEXT_COLOR'])
        self.screen.blit(round_text, (icon_x4 + 26, info_y + 2))

        # 时间 - 时钟图标 靠右显示
        draw_clock_icon(self.screen, SCREEN_WIDTH - 155, info_y + icon_y_offset + 11, icon_size - 2)
        elapsed = time.time() - self.start_time if self.start_time > 0 else 0
        remaining = max(0, self.total_time - elapsed)
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        time_text = SCORE_FONT.render(f"{minutes:02d}:{seconds:02d}", True, COLORS['TEXT_COLOR'])
        self.screen.blit(time_text, (SCREEN_WIDTH - 125, info_y))

        # 提示操作说明 - 底部
        sound_status = "ON" if self.sound_enabled else "OFF"
        hint_text = INFO_FONT.render(f"方向键移动  |  碰到泡泡自动收集  |  空格暂停  |  R重新开始  |  M音效:{sound_status}", True, COLORS['GRAY'])
        self.screen.blit(hint_text, (20, SCREEN_HEIGHT - 28))

        # 绘制超大目标数字（带脉冲动画）- 在游戏区域顶部居中
        # 计算脉冲效果（放大缩小）
        pulse_scale = 1.0 + 0.1 * math.sin(self.target_pulse_timer)
        target_font_size = int(48 * pulse_scale)

        # 创建大字体目标 - 使用系统字体
        # 尝试使用系统自带的中文字体
        try:
            # Windows 系统字体
            target_big_font = pygame.font.SysFont("microsoftyahei", target_font_size)
        except:
            try:
                target_big_font = pygame.font.SysFont("simhei", target_font_size)
            except:
                target_big_font = pygame.font.Font(None, target_font_size)

        # 目标数字带阴影和边框 - 使用中文
        if self.operation == "add":
            target_label = f"找到相加等于{self.target_number}"
        else:
            target_label = f"找到相减等于{self.target_number}"
        target_shadow = target_big_font.render(target_label, True, (200, 200, 200))
        target_surface = target_big_font.render(target_label, True, COLORS['ORANGE'])

        # 绘制目标文字（带阴影效果，不加框）
        shadow_rect = target_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, GAME_AREA_TOP + 38 + 2))
        text_rect = target_surface.get_rect(center=(SCREEN_WIDTH // 2, GAME_AREA_TOP + 38))
        self.screen.blit(target_shadow, shadow_rect)
        self.screen.blit(target_surface, text_rect)

        # 绘制泡泡
        for bubble in self.bubbles:
            if not bubble.collected:
                bubble.draw(self.screen)

        # 绘制蛇
        self.snake.draw(self.screen)

        # 绘制已收集的数字和等式 - 大字显示在屏幕中央
        if self.collected_numbers:
            if len(self.collected_numbers) == 1:
                # 收集了一个数字 - 大字显示
                num = self.collected_numbers[0]
                collect_text = SCORE_FONT.render(f"找到了 {num}!", True, COLORS['TEXT_COLOR'])

                # 背景框
                bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, GAME_AREA_TOP + 80, 200, 50)
                pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, border_radius=12)
                pygame.draw.rect(self.screen, COLORS['GREEN'], bg_rect, 2, border_radius=12)

                # 显示文字
                text_rect = collect_text.get_rect(center=(SCREEN_WIDTH // 2, GAME_AREA_TOP + 105))
                self.screen.blit(collect_text, text_rect)

            elif len(self.collected_numbers) == 2:
                # 收集了两个数字，显示等式 - 超大显示
                n1, n2 = self.collected_numbers
                if self.operation == "add":
                    result = n1 + n2
                    equation = f"{n1} + {n2} = {result}"
                else:
                    bigger = max(n1, n2)
                    smaller = min(n1, n2)
                    result = bigger - smaller
                    equation = f"{bigger} - {smaller} = {result}"

                # 正确是绿色，错误是红色
                if result == self.target_number:
                    equation_color = COLORS['GREEN']
                    status_text = "正确!"
                else:
                    equation_color = COLORS['RED']
                    status_text = f"不对哦~ 目标是 {self.target_number}"

                # 创建超大字体等式 - 使用系统字体
                try:
                    eq_big_font = pygame.font.SysFont("microsoftyahei", 56)
                except:
                    try:
                        eq_big_font = pygame.font.SysFont("simhei", 56)
                    except:
                        eq_big_font = pygame.font.Font(None, 56)

                # 等式文字（带阴影，无框）
                eq_shadow = eq_big_font.render(equation, True, (200, 200, 200))
                eq_render = eq_big_font.render(equation, True, equation_color)
                shadow_rect = eq_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, GAME_AREA_TOP + 95 + 2))
                text_rect = eq_render.get_rect(center=(SCREEN_WIDTH // 2, GAME_AREA_TOP + 95))
                self.screen.blit(eq_shadow, shadow_rect)
                self.screen.blit(eq_render, text_rect)

                # 状态文字 - 使用系统字体
                try:
                    status_font = pygame.font.SysFont("microsoftyahei", 24)
                except:
                    try:
                        status_font = pygame.font.SysFont("simhei", 24)
                    except:
                        status_font = pygame.font.Font(None, 24)
                status_render = status_font.render(status_text, True, equation_color)
                status_rect = status_render.get_rect(center=(SCREEN_WIDTH // 2, GAME_AREA_TOP + 125))
                self.screen.blit(status_render, status_rect)

        # 绘制消息 - 移到底部避免遮挡游戏
        if self.message and self.message_timer > 0:
            # 直接显示消息文字，无框
            msg_surface = TITLE_FONT.render(self.message, True, COLORS['WHITE'])
            msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
            self.screen.blit(msg_surface, msg_rect)

        # 暂停画面 - 可爱风格
        if self.paused:
            # 半透明遮罩
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 150))
            self.screen.blit(overlay, (0, 0))

            pause_text = TITLE_FONT.render("[ 游戏暂停 - 按空格继续 ]", True, COLORS['TEXT_COLOR'])
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            pygame.draw.rect(self.screen, COLORS['WHITE'], pause_rect.inflate(50, 25), border_radius=15)
            pygame.draw.rect(self.screen, (173, 216, 230), pause_rect.inflate(50, 25), 3, border_radius=15)  # 蓝色边框
            self.screen.blit(pause_text, pause_rect)

        # 游戏结束画面 - 可爱风格
        if self.game_over:
            # 半透明遮罩
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 180))
            self.screen.blit(overlay, (0, 0))

            over_text = TITLE_FONT.render("=== 游戏结束 ===", True, COLORS['TEXT_COLOR'])
            final_score = SCORE_FONT.render(f"[ 最终得分: {self.score} ]", True, COLORS['GREEN'])
            restart_text = INFO_FONT.render("点击任意位置或按 R 重新开始", True, COLORS['GRAY'])

            over_rect = over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            score_rect = final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))

            # 背景框 - 圆角可爱风格
            bg_rect = over_rect.union(score_rect).union(restart_rect)
            bg_rect = bg_rect.inflate(60, 50)
            pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, border_radius=20)
            pygame.draw.rect(self.screen, (255, 182, 193), bg_rect, 4, border_radius=20)  # 粉色边框

            self.screen.blit(over_text, over_rect)
            self.screen.blit(final_score, score_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        """运行游戏"""
        # 事件处理
        self.handle_input()

        # 先更新游戏状态（包括处理蛇变长）
        self.update()

        # 绘制
        self.draw()

        # 控制帧率
        self.clock.tick(30)


def select_difficulty():
    """选择难度/时间 - 使用与游戏相同的窗口尺寸"""
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("数字贪吃蛇 - 选择游戏时长")

    clock = pygame.time.Clock()
    running = True

    # 预设时间选项
    times = [
        (1, "1分钟"),
        (3, "3分钟"),
        (5, "5分钟"),
        (10, "10分钟"),
    ]

    # 自定义时间输入相关
    custom_input_active = False
    custom_time_str = ""

    # 布局参数 - 左右两栏布局
    left_section_x = SCREEN_WIDTH // 4 - 100  # 左侧预设按钮区域
    right_section_x = SCREEN_WIDTH * 3 // 4 - 100  # 右侧自定义输入区域
    start_y = SCREEN_HEIGHT // 2 + 30  # 起始Y位置
    btn_width = 200
    btn_height = 50
    btn_spacing = 70

    while running:
        screen.fill(COLORS['BG_COLOR'])

        # 绘制可爱装饰 - 顶部彩虹色带
        rainbow_colors = [(255, 182, 193), (255, 218, 185), (255, 255, 224), (173, 216, 230), (221, 160, 221)]
        for i, color in enumerate(rainbow_colors):
            y = 5 + i * 3
            pygame.draw.rect(screen, color, (0, y, SCREEN_WIDTH, 3))

        # 绘制彩色装饰 - 飘动的云朵
        cloud_colors = [(255, 255, 255), (240, 248, 255), (245, 245, 245)]
        for i, cx in enumerate([100, SCREEN_WIDTH - 150, 300, SCREEN_WIDTH - 80]):
            cy = 200 + i * 30
            color = cloud_colors[i % len(cloud_colors)]
            pygame.draw.circle(screen, color, (cx, cy), 30)
            pygame.draw.circle(screen, color, (cx + 25, cy - 5), 25)
            pygame.draw.circle(screen, color, (cx - 20, cy + 5), 20)

        # 绘制彩色星星装饰
        star_colors = [(255, 215, 0), (255, 165, 0), (255, 105, 180)]
        for i, (sx, sy) in enumerate([(50, 150), (SCREEN_WIDTH - 50, 180), (80, 300), (SCREEN_WIDTH - 80, 320)]):
            color = star_colors[i % len(star_colors)]
            pygame.draw.circle(screen, color, (sx, sy), 8)
            pygame.draw.circle(screen, (255, 255, 200), (sx - 2, sy - 2), 3)

        # 绘制底部彩色圆点装饰
        bottom_colors = [(255, 182, 193), (173, 216, 230), (144, 238, 144), (255, 218, 185)]
        for i in range(10):
            x = 30 + i * (SCREEN_WIDTH - 60) // 9
            y = SCREEN_HEIGHT - 80
            color = bottom_colors[i % len(bottom_colors)]
            pygame.draw.circle(screen, color, (x, y), 5)

        # 绘制标题
        title = TITLE_FONT.render("=== 数字贪吃蛇 ===", True, COLORS['TEXT_COLOR'])
        subtitle = INFO_FONT.render("选择游戏时长", True, COLORS['GRAY'])

        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 80))

        # 游戏规则说明 - 增大间距避免重叠
        rules = [
            "游戏规则：",
            "1. 每轮设置目标数字，找到两个数字相加/相减等于目标",
            "2. 控制小蛇移动，碰到数字泡泡自动收集",
            "3. 收集正确蛇变长得分，错误蛇变短扣分",
            "4. 撞墙不会死亡，会害羞地转弯",
        ]
        rule_line_height = 20  # 行间距
        rule_title_y = 125  # 标题位置
        for i, rule in enumerate(rules):
            if i == 0:
                # 标题使用更大字体和颜色
                rule_color = COLORS['TEXT_COLOR']
                rule_font = SCORE_FONT
                rule_text = rule_font.render(rule, True, rule_color)
                screen.blit(rule_text, (30, rule_title_y))
            else:
                # 内容使用较小字体和灰色，增大与标题的间距
                rule_color = (80, 80, 80)
                try:
                    rule_font = pygame.font.SysFont("microsoftyahei", 16)
                except:
                    try:
                        rule_font = pygame.font.SysFont("simhei", 16)
                    except:
                        rule_font = pygame.font.Font(None, 16)
                rule_text = rule_font.render(rule, True, rule_color)
                screen.blit(rule_text, (30, rule_title_y + 40 + (i - 1) * rule_line_height))

        mouse_pos = pygame.mouse.get_pos()

        # 左侧 - 预设时间按钮
        left_title = SCORE_FONT.render("快速选择", True, COLORS['TEXT_COLOR'])
        screen.blit(left_title, (left_section_x + btn_width // 2 - left_title.get_width() // 2, start_y - 40))

        for i, (minutes, label) in enumerate(times):
            btn_x = left_section_x
            btn_y = start_y + i * btn_spacing
            btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)

            # 悬停时渐变色
            if btn_rect.collidepoint(mouse_pos):
                color = COLORS['GREEN']
                # 添加发光效果
                glow_rect = btn_rect.inflate(10, 10)
                pygame.draw.rect(screen, (200, 255, 200), glow_rect, border_radius=15)
            else:
                color = COLORS['LIGHT_GRAY']

            pygame.draw.rect(screen, color, btn_rect, border_radius=12)
            pygame.draw.rect(screen, (100, 200, 100), btn_rect, 3, border_radius=12)

            # 按钮文字
            btn_text = SCORE_FONT.render(f"[ {label} ]", True, COLORS['TEXT_COLOR'])
            screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width() // 2, btn_rect.centery - btn_text.get_height() // 2))

        # 右侧 - 自定义时间输入
        right_title = SCORE_FONT.render("自定义时间", True, COLORS['TEXT_COLOR'])
        screen.blit(right_title, (right_section_x + btn_width // 2 - right_title.get_width() // 2, start_y - 40))

        # 输入框标签
        input_label = INFO_FONT.render("输入分钟数 (1-60):", True, COLORS['TEXT_COLOR'])
        screen.blit(input_label, (right_section_x, start_y))

        # 绘制输入框
        input_rect = pygame.Rect(right_section_x, start_y + 35, btn_width, btn_height)
        if custom_input_active:
            pygame.draw.rect(screen, COLORS['GREEN'], input_rect, 3, border_radius=12)
        else:
            pygame.draw.rect(screen, COLORS['LIGHT_GRAY'], input_rect, 3, border_radius=12)

        # 显示输入的内容
        if custom_time_str:
            input_text = SCORE_FONT.render(custom_time_str + " 分钟", True, COLORS['TEXT_COLOR'])
        else:
            input_text = INFO_FONT.render("点击输入...", True, COLORS['GRAY'])
        screen.blit(input_text, (input_rect.x + 10, input_rect.y + 15))

        # 确认按钮
        confirm_rect = pygame.Rect(right_section_x + btn_width + 20, start_y + 35, 80, btn_height)
        if confirm_rect.collidepoint(mouse_pos):
            confirm_color = COLORS['GREEN']
        else:
            confirm_color = COLORS['LIGHT_GRAY']
        pygame.draw.rect(screen, confirm_color, confirm_rect, border_radius=12)
        confirm_text = SCORE_FONT.render("开始", True, COLORS['TEXT_COLOR'])
        # 居中显示
        text_x = confirm_rect.x + (confirm_rect.width - confirm_text.get_width()) // 2
        text_y = confirm_rect.y + (confirm_rect.height - confirm_text.get_height()) // 2
        screen.blit(confirm_text, (text_x, text_y))

        # 底部提示
        hint_text = INFO_FONT.render("从左侧选择快速选项，或在右侧输入自定义时长", True, COLORS['GRAY'])
        screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT - 50))

        # 右下角公众号提示
        try:
            wechat_font = pygame.font.SysFont("microsoftyahei", 20)
        except:
            try:
                wechat_font = pygame.font.SysFont("simhei", 20)
            except:
                wechat_font = pygame.font.Font(None, 20)
        # 使用更明显的颜色（深紫色）
        wechat_text = wechat_font.render("欢迎关注公众号@零虎冲呀", True, (128, 0, 128))
        screen.blit(wechat_text, (SCREEN_WIDTH - wechat_text.get_width() - 20, SCREEN_HEIGHT - 25))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # 检查左侧预设按钮
                for i, (minutes, label) in enumerate(times):
                    btn_x = left_section_x
                    btn_y = start_y + i * btn_spacing
                    btn_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
                    if btn_rect.collidepoint(event.pos):
                        return minutes * 60

                # 检查输入框
                if input_rect.collidepoint(event.pos):
                    custom_input_active = True
                    custom_time_str = ""
                else:
                    custom_input_active = False

                # 检查确认按钮
                if confirm_rect.collidepoint(event.pos) and custom_time_str:
                    try:
                        custom_minutes = int(custom_time_str)
                        if 1 <= custom_minutes <= 60:
                            return custom_minutes * 60
                    except:
                        pass

            if event.type == pygame.KEYDOWN and custom_input_active:
                if event.key == pygame.K_BACKSPACE:
                    custom_time_str = custom_time_str[:-1]
                elif event.key == pygame.K_RETURN:
                    # 按回车确认
                    try:
                        custom_minutes = int(custom_time_str)
                        if 1 <= custom_minutes <= 60:
                            return custom_minutes * 60
                    except:
                        pass
                elif event.unicode.isdigit() and len(custom_time_str) < 2:
                    custom_time_str += event.unicode

        clock.tick(30)


if __name__ == "__main__":
    import math

    # 选择难度
    total_time = select_difficulty()

    # 继续使用已有窗口（已在select_difficulty中设置）
    pygame.display.set_caption("数字贪吃蛇 - 学数学")

    # 创建游戏实例
    game = Game()
    game.total_time = total_time

    # 游戏主循环
    while game.running:
        game.run()

    pygame.quit()
