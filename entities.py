import pygame as pg
from config import *
from utility import *
from random import choice, randint
from pygame.locals import *

DIR = {
    'up': [0, -1],
    'down': [0, 1],
    'right': [1, 0],
    'left': [-1, 0],
}

RID = {tuple(value): key for key, value in DIR.items()}

OPPOSITE = [{'up', 'down'}, {'right', 'left'}]


class Cell(pg.sprite.Sprite):
    COLOR = pg.Color('red')
    groups = {}
    def __init__(self, x, y):
        super().__init__()
        self.pos = [x, y]
        self.rect = pg.Rect(0, 0, TILE, TILE)
        self.rect.center = x * TILE, y * TILE
        self.image = pg.Surface(self.rect.size)
        self.image.fill(self.COLOR)
        self.add(self.groups['all'])

    def move(self):
        pass

    def update(self, ms):
        pass


class Apple(Cell, metaclass=Singleton):
    COLOR = pg.Color('darkgreen')
    def __init__(self):
        super().__init__(0, 0)
        self.respawn()

    def respawn(self):
        # while True:
        x, y = randint(1, FIELD[0]), randint(1, FIELD[1])
        self.pos = [x, y]
        self.rect.center = x * TILE, y * TILE
        if pg.sprite.spritecollide(self, self.groups['snake'], False):
            self.respawn()


class Head(Cell, metaclass=Singleton):
    DELAY = 250
    DELAY_INC = 25
    DELAY_MIN = 1000 // FPS

    def __init__(self):
        x, y = randint(1, FIELD[0]), randint(1, FIELD[1])
        super().__init__(x, y)
        self.groups['snake'].add(self)
        self.new()

    def new(self):
        self.alive = True
        self.dir_next = self.dir = choice(list(DIR.keys()))
        self.delay = 0
        self.score = 1
        self.tail = [self]

    def update(self, ms):
        keys = pg.key.get_pressed()
        hor = keys[K_d] - keys[K_a]
        vert = keys[K_s] - keys[K_w]

        if hor != vert and 0 in (hor, vert):
            dir_new = RID[hor, vert]
            if {self.dir, dir_new} not in OPPOSITE:
                self.dir_next = dir_new

        if self.delay <= 0:
            self.move()
        else:
            self.delay -= ms

    def move(self):
        for i in range(len(self.tail) - 1, 0, -1):
            self.tail[i].move(self.tail[i - 1])
        
        self.dir = self.dir_next

        self.pos = [(self.pos[i] + DIR[self.dir][i]) % FIELD[i] for i in range(2)]
        self.rect.center = [coord * TILE + TILE for coord in self.pos]
        self.delay += self.DELAY

        for i in range(1, len(self.tail)):
            if pg.sprite.collide_rect(self, self.tail[i]):
                self.alive = False

    def inc(self):
        self.score += 1
        self.tail.append(Tail(*[coord // TILE for coord in self.tail[-1].rect.center]))

        if self.score - 1 and (self.score - 1) % 4 == 0:
            self.DELAY = max(self.DELAY - self.DELAY_INC, self.DELAY_MIN)

        return FIELD[0] * FIELD[1] == len(self.tail)

    def is_dead(self):
        return not self.alive


class Tail(Cell):
    COLOR = pg.Color('darkred')
    def __init__(self, x, y):
        super().__init__(x, y)
        self.groups['snake'].add(self)

    def move(self, obj):
        self.rect.center = obj.rect.center


class Field(pg.sprite.Sprite, metaclass=Singleton):
    COLOR_BG = pg.Color('darkgray'), pg.Color('gray')
    COLOR_LINE = pg.Color('lightgray')
    def __init__(self, clock):
        super().__init__()
        self.rect = WIN_SIZE
        self.bg = self.field()
        self.image = pg.Surface(self.rect.size)
        self.entities = pg.sprite.Group()
        self.snake = pg.sprite.Group()
        Cell.groups['all'] = self.entities
        Cell.groups['snake'] = self.snake
        Head(), Apple()
        self.font = pg.font.SysFont('comicsansms', 64, True)
        self.font_debug = pg.font.SysFont('comicsansms', 32, True)
        self.clock = clock
        self.debug = True
        self.new()

    def new(self):
        self.state = 'running'
        for sprite in self.snake:
            if sprite.__class__ == Tail:
                sprite.kill()
        Head().new()
        Apple().respawn()


    def field(self):
        # фон
        bg = pg.Surface(self.rect.size)
        bg.fill(self.COLOR_BG[0])
        # клеточки
        for x in range(FIELD[0]):
            for y in range(FIELD[1]):
                rect = pg.Rect(0, 0, TILE, TILE).move(x * TILE + TILE // 2, y * TILE + TILE // 2)
                pg.draw.rect(bg, self.COLOR_BG[(x + y) % 2], rect)
        return bg

    def border(self):
        # рамка
        rect = pg.Rect((0, 0), (FIELD[0] * TILE, FIELD[1] * TILE)).move(TILE // 2, TILE // 2)
        pg.draw.rect(self.image, self.COLOR_LINE, rect, 8)

    def draw(self, surface):
        self.image.blit(self.bg, (0, 0))
        self.entities.draw(self.image)
        self.border()
        draw_text(self.image, self.font, f'Score: {Head().score}', (200, 100))
        if self.debug:
            draw_text(self.image, self.font_debug, f'FPS: {self.clock.get_fps():.0f}', (WIN_SIZE.w - 100, 100))
        if self.state != 'running':
            draw_text(self.image, self.font, self.state, WIN_SIZE.center)
        self.image.blit(Head().image, Head().rect.topleft)
        surface.blit(self.image, (0, 0))

    def update(self, ms):
        if self.state == 'running':
            self.entities.update(ms)
            if Head().is_dead():
                self.state = 'You lose'
                self.the_end()
            if pg.sprite.spritecollide(Apple(), self.snake, False):
                if Head().inc():
                    self.state = 'You win'
                    self.the_end()
                    return
                Apple().respawn()

    def the_end(self):
        self.won = True
