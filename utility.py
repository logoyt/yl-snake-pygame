import pygame as pg
from pygame.locals import *

from config import *


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def window_init():
    # получаем размеры монитора
    from tkinter import Tk
    temp = Tk()
    MONITOR_SIZE = temp.winfo_screenwidth(), \
                   temp.winfo_screenheight()
    temp.destroy()
    del temp

    # устанавливаем окно в правый верхний угол
    from os import environ
    screen_coords = (MONITOR_SIZE[0] - WIN_SIZE.w - 50, 50)
    environ['SDL_VIDEO_WINDOW_POS'] = f"{screen_coords[0]}, " \
                                      f"{screen_coords[1]}"

    screen = pg.display.set_mode(WIN_SIZE.size)

    return screen


def draw_text(surface, font, text, pos=(0, 0), color=pg.Color('Black')):
    image = font.render(text, True, color)
    rect = image.get_rect()
    rect.center = pos
    surface.blit(image, rect.topleft)


class Scene:
    def __init__(self, surface, clock, *args):
        self.surface = surface
        self.running = True
        self.clock = clock
        self.state = None

    def run(self):
        while self.running:
            self.events()
            self.update()
            self.render()
        self.on_delete()
        return self.state

    def events(self):
        for e in pg.event.get():
            if e.type == QUIT:
                self.running = False
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    self.running = False

    def update(self):
        self.clock.tick(FPS)

    def render(self):
        self.surface.fill(pg.Color('gray'))
        pg.display.update()

    def on_delete(self):
        pass


class Button(pg.sprite.Sprite):
    btn_id = 0
    def __init__(self, text='Button', size=(256+128, 128), \
                       pos=WIN_SIZE.center, font=None, \
                       name=None):
        super().__init__()
        if not font:
            self.font = pg.font.SysFont('comicsansms', 64, True)

        # прозрачный прямоугольник
        self.image = pg.Surface(size, flags=SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = pos

        # текст
        text = self.font.render(text, True, pg.Color('darkgreen'))
        rect = text.get_rect()
        rect.center = self.rect.w // 2, self.rect.h // 2
        self.image.blit(text, rect.topleft)
        self.text = text

        # рамка
        pg.draw.rect(self.image, pg.Color('blue'), ((0, 0), size), 16)
        
        # имя
        Button.btn_id += 1
        if not name:
            self.name = Button.btn_id
        else:
            self.name = name

    def on_click(self):
        # print(f'Button "{self.name}" pressed')
        return self.name


def len_bw_dots(dot1, dot2):
    dx = abs(dot1[0] - dot2[0])
    dy = abs(dot1[1] - dot2[1])
    return int((dx ** 2 + dy ** 2) ** .5)
