import pygame as pg
import random as r
from pygame.locals import *

from utility import *
from config import *
from entities import *


class Window:
    def __init__(self):
        pg.init()
        self.surface = window_init()
        self.clock = pg.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            state = Menu(self.surface, self.clock).run()
            if state == 'quit':
                self.running = False
            elif state == 'start':
                Game(self.surface, self.clock).run()


class Menu(Scene):
    def __init__(self, *args):
        super().__init__(*args)
        self.btns = pg.sprite.Group()
        pos = WIN_SIZE.w // 2, WIN_SIZE.h // 3
        start = Button('Start', pos=pos, name='start')
        pos = WIN_SIZE.w // 2, WIN_SIZE.h // 3 * 2
        exit = Button('Quit', pos=pos, name='quit')
        self.btns.add(start, exit)

    def render(self):
        self.surface.fill(pg.Color('darkgray'))
        self.btns.draw(self.surface)
        pg.display.update()

    def events(self):
        for e in pg.event.get():
            if e.type == QUIT:
                self.running = False
                self.state = 'quit'
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    self.running = False
                    self.state = 'quit'
            if e.type == MOUSEBUTTONUP:
                if e.button == 1:
                    self.click(e.pos)

    def click(self, pos):
        for btn in self.btns:
            if btn.rect.collidepoint(pos):
                self.state = btn.on_click()
                self.running = False


class Game(Scene):
    def __init__(self, *args):
        super().__init__(*args)
        self.field = Field(self.clock)
        self.field.new()

    def update(self):
        ms = self.clock.tick_busy_loop(FPS) # _busy_loop
        self.field.update(ms)

    def render(self):
        self.surface.fill(pg.Color('black'))
        self.field.draw(self.surface)
        pg.display.update()

    def on_delete(self):
        self.field.kill()


if __name__ == '__main__':
    Window().run()
