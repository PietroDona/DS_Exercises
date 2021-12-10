import pygame
import time
from random import randrange

SQUARE_SIZE = 20

white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

SCORE_FONT = None


class Screen():
    x, y = 600, 800

    def __init__(self, X, Y):
        self.x = X
        self.y = Y

    def __str__(self):
        return f"Screen size is {self.x} x {self.y}"


class Snake():
    head = pygame.Rect(100, 100, SQUARE_SIZE-2, SQUARE_SIZE-2)
    body = [head]
    length = 1
    game = None

    def __init__(self, thisgame):
        self.game = thisgame

    def eat(self):
        self.length += 1
        self.game.add_score(self.game.fruit.points)
        self.game.fruit.relocate()

    def move(self, movestep):
        mx, my = movestep

        self.head.move_ip(mx*SQUARE_SIZE, my*SQUARE_SIZE)

        if self.head.center == self.game.fruit.pos.center:
            self.eat()

        self.body.append(self.head.copy())
        if len(self.body) > self.length:
            self.body.pop(0)

        # check if I die
        # exiting X bounds
        if self.head.centerx < 0 or self.head.centerx > self.game.screen.x:
            self.game.game_over = True
        # exiting Y bounds
        if self.head.centery < 0 or self.head.centery > self.game.screen.y:
            self.game.game_over = True
        # self intersecting
        if self.head.center in [s.center for s in self.body[:-1]]:
            self.game.game_over = True

    def draw_snake(self):
        for square in self.body:
            pygame.draw.rect(self.game.display, green, square)


class Fruit():
    pos = pygame.Rect(200, 200, SQUARE_SIZE-2, SQUARE_SIZE-2)
    points = 10
    game = None

    def __init__(self, thisgame):
        self.game = thisgame
        self.relocate()
        # make random position

    def relocate(self):
        newx = randrange(round(self.game.screen.x/SQUARE_SIZE))*SQUARE_SIZE
        newy = randrange(round(self.game.screen.y/SQUARE_SIZE))*SQUARE_SIZE
        self.pos = pygame.Rect(newx, newy, SQUARE_SIZE-2, SQUARE_SIZE-2)

    def draw_fruit(self):
        pygame.draw.rect(self.game.display, red, self.pos)


class Game():
    screen = None
    clock = None
    display = None
    snake = None
    fruit = None
    direction = None
    speed = 10
    game_over = None
    score = 0

    def __init__(self, title):
        self.clock = pygame.time.Clock()
        self.screen = Screen(800, 600)
        self.display = pygame.display.set_mode((self.screen.x, self.screen.y))
        pygame.display.set_caption(title)
        self.snake = Snake(self)
        self.snake.draw_snake()
        self.fruit = Fruit(self)
        self.game_over = False

    def draw_score(self):
        value = SCORE_FONT.render(f"Score: {self.score}", True, white)
        self.display.blit(value, [0, 0])

    def add_score(self, add):
        self.score += add
        self.speed = 10 + self.score/100

    def gameLoop(self):
        while not self.game_over:
            self.display.fill(blue)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_LEFT
                            and self.direction != (1, 0)):
                        self.direction = (-1, 0)
                    elif (event.key == pygame.K_RIGHT
                          and self.direction != (-1, 0)):
                        self.direction = (1, 0)
                    elif (event.key == pygame.K_UP
                          and self.direction != (0, 1)):
                        self.direction = (0, -1)
                    elif (event.key == pygame.K_DOWN
                          and self.direction != (0, -1)):
                        self.direction = (0, 1)
                    elif (event.key == pygame.K_LCTRL):
                        self.speed -= 2
                    elif (event.key == pygame.K_RCTRL):
                        self.speed += 2
            if self.direction:
                self.snake.move(self.direction)
            self.snake.draw_snake()
            self.fruit.draw_fruit()
            self.draw_score()

            pygame.display.update()
            self.clock.tick(self.speed)
        pygame.quit()
        quit()


if __name__ == "__main__":
    pygame.init()
    SCORE_FONT = pygame.font.SysFont("arial", 20)

    game = Game('Snake Game')
    game.gameLoop()
