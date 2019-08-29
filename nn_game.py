import pygame
import math
import os
import neat
from pygame.locals import *

pygame.init()
clock = pygame.time.Clock()

MIN_WIDTH = 1024
MIN_HEIGHT = 768
DRAW_SENSORS = True

WIN = pygame.display.set_mode((MIN_WIDTH, MIN_HEIGHT))
pygame.display.set_caption("Racing")

bg_img = pygame.image.load("images/bg.jpg").convert()


class Sensor:
    def __init__(self, angle):
        self.angle = angle
        self.distance = 0

    def update(self, position, direction):
        sensor_distance = 400

        for i in range(1, sensor_distance, 10):
            for pad in pads:
                x = (int)(position[0] + math.cos(math.radians(-direction - 90 + self.angle)) * i)
                y = (int)(position[1] + math.sin(math.radians(-direction - 90 + self.angle)) * i)
                if pad.contains_point((x, y)) and i < sensor_distance:
                    sensor_distance = i - 1
        self.distance = sensor_distance


class CarSprite(pygame.sprite.Sprite):
    MAX_FORWARD_SPEED = 10
    MAX_REVERSE_SPEED = 10
    ACCELERATION = 2
    TURN_SPEED = 10

    def __init__(self, image, position):
        pygame.sprite.Sprite.__init__(self)
        self.sensors = []
        self.src_image = pygame.image.load(image)
        self.position = position
        self.speed = self.direction = 0
        self.k_left = self.k_right = self.k_down = self.k_up = 0
        self.k_up = 5
        self.sensors = [Sensor(-90), Sensor(-70), Sensor(-45), Sensor(-15), Sensor(0),Sensor(15), Sensor(45),Sensor(70), Sensor(90)]

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
        self.update_sensors()

    def update_sensors(self):
        for sensor in self.sensors:
            sensor.update(self.rect.center, self.direction)

class PadSprite(pygame.sprite.Sprite):

    def __init__(self, position, image):
        super(PadSprite, self).__init__()
        self.rect = pygame.Rect(self.normal.get_rect())
        self.rect.center = position
        self.image = self.normal

    def contains_point(self, coordinates):
        return coordinates[0] >= self.rect.topleft[0] and coordinates[0] <= self.rect.bottomright[0] and coordinates[1] >= \
               self.rect.topleft[1] and coordinates[1] <= self.rect.bottomright[1]


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


def draw_sensor(win, car, angle, sensor_length):
    x = (int)(car.position[0] + math.cos(math.radians(-car.direction - 90 + angle)) * sensor_length)
    y = (int)(car.position[1] + math.sin(math.radians(-car.direction - 90 + angle)) * sensor_length)
    pygame.draw.line(win, Color("red"), car.rect.center, (x, y), 1)


def draw_window(win, car_groups, cars):
    win.blit(bg_img, (0, 0))

    if DRAW_SENSORS:
        for car in cars:
            for sensor in car.sensors:
                draw_sensor(win, car, sensor.angle, sensor.distance)

    pad_group.draw(win)
    for car_group in car_groups:
        car_group.draw(win)

    pygame.display.flip()


def eval_genomes(genomes, config):

    tick_count = 0

    nets = []
    cars = []
    car_groups = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        car = CarSprite('images/car.png', (70, 600))
        cars.append(car)
        car_groups.append(pygame.sprite.RenderPlain(car))
        ge.append(genome)


    run = True

    while run and len(cars) > 0:
        tick_count += 1
        if tick_count > 1800:  # if more than 10 seconds close the game
            break

        deltat = clock.tick(30)
        for car_group in car_groups:
            car_group.update(deltat)


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

        for x, car in enumerate(cars):
            params = []
            for sensor in car.sensors:
                params.append(sensor.distance)
            params.append(car.speed)
            inputs = (tuple(params))
            output = nets[x].activate(inputs)

            car.k_down = car.k_up = car.k_left = car.k_right = 0

            if output[0] > 0.5:
                car.k_right = -5

            if output[1] > 0.5:
                car.k_left = 5

            if output[2] > 0.5:
                car.k_up = 2

            if output[3] > 0.5:
                car.k_down = -2

        for x, car_group in enumerate(car_groups):
            collisions = pygame.sprite.groupcollide(car_group, pad_group, False, False, collided=None)
            if collisions != {}:
                car.image = pygame.image.load('images/collision.png')
                car.MAX_FORWARD_SPEED = 0
                car.MAX_REVERSE_SPEED = 0
                car.k_right = 0
                car.k_left = 0
                nets.pop(x)
                ge.pop(x)
                cars.pop(x)
                car_groups.pop(x)

        for x, car in enumerate(cars):
            ge[x].fitness += (cars[x].speed)

        for x, car in enumerate(cars):
            if tick_count > 400 and (ge[x].fitness < 1000 or car.speed == 0):  # if more than 10 seconds close the game
                nets.pop(x)
                ge[x].fitness -= 1000
                ge.pop(x)
                cars.pop(x)
                car_groups.pop(x)

        draw_window(WIN, car_groups, cars)


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
