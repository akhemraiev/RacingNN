import pygame
import math
import os
from pygame.locals import *

pygame.init()
clock = pygame.time.Clock()

MIN_WIDTH = 1024
MIN_HEIGHT = 768

WIN = pygame.display.set_mode((MIN_WIDTH, MIN_HEIGHT))
pygame.display.set_caption("Racing")

bg_img = pygame.image.load("images/bg.jpg").convert()


class CarSprite(pygame.sprite.Sprite):
    MAX_FORWARD_SPEED = 10
    MAX_REVERSE_SPEED = 10
    ACCELERATION = 2
    TURN_SPEED = 10

    def __init__(self, image, position):
        pygame.sprite.Sprite.__init__(self)
        self.src_image = pygame.image.load(image)
        self.position = position
        self.speed = self.direction = 0
        self.k_left = self.k_right = self.k_down = self.k_up = 0

    def update(self, deltat):
        # SIMULATION
        self.speed += (self.k_up + self.k_down)
        if self.speed > self.MAX_FORWARD_SPEED:
            self.speed = self.MAX_FORWARD_SPEED
        if self.speed < -self.MAX_REVERSE_SPEED:
            self.speed = -self.MAX_REVERSE_SPEED
        self.direction += (self.k_right + self.k_left)
        x, y = (self.position)
        rad = self.direction * math.pi / 180
        x += -self.speed * math.sin(rad)
        y += -self.speed * math.cos(rad)
        self.position = (x, y)
        self.image = pygame.transform.rotate(self.src_image, self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = self.position


class PadSprite(pygame.sprite.Sprite):

    def __init__(self, position, image):
        super(PadSprite, self).__init__()
        self.rect = pygame.Rect(self.normal.get_rect())
        self.rect.center = position
        self.image = self.normal



class HorizontalPad(PadSprite):
    normal = pygame.image.load('images/race_pads.png')

    def __init__(self, position):
        PadSprite.__init__(self, position, self.normal)


class VerticalPad(PadSprite):
    normal = pygame.image.load('images/vertical_pads.png')

    def __init__(self, position):
        PadSprite.__init__(self, position, self.normal)


pads = [
        HorizontalPad((250, 10)),
        HorizontalPad((750, 10)),
        VerticalPad((1014, 250)),
        VerticalPad((1014, 600)),
        HorizontalPad((250, 758)),
        HorizontalPad((750, 758)),
        VerticalPad((10, 250)),
        VerticalPad((10, 600)),

        VerticalPad((200, 400)),
        HorizontalPad((450, 160)),
        HorizontalPad((600, 160)),

        HorizontalPad((600, 400)),
        HorizontalPad((750, 400)),

        HorizontalPad((450, 640)),
        HorizontalPad((600, 640))
    ]
pad_group = pygame.sprite.RenderPlain(*pads)

def draw_window(win, car_group):
    win.blit(bg_img, (0, 0))

    pad_group.draw(win)
    car_group.draw(win)

    pygame.display.flip()


def main():
    car = CarSprite('images/car.png', (70, 700))
    car_group = pygame.sprite.RenderPlain(car)

    run = True
    crashed = False

    while run and not crashed:
        deltat = clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                break
            if not hasattr(event, 'key'): continue
            down = event.type == KEYDOWN
            if event.key == K_RIGHT:
                car.k_right = down * -5
            elif event.key == K_LEFT:
                car.k_left = down * 5
            elif event.key == K_UP:
                car.k_up = down * 2
            elif event.key == K_DOWN:
                car.k_down = down * -2

        car_group.update(deltat)

        collisions = pygame.sprite.groupcollide(car_group, pad_group, False, False, collided=None)
        if collisions != {}:
            crashed = True
            car.image = pygame.image.load('images/collision.png')
            car.MAX_FORWARD_SPEED = 0
            car.MAX_REVERSE_SPEED = 0
            car.k_right = 0
            car.k_left = 0

        draw_window(WIN, car_group)


main()