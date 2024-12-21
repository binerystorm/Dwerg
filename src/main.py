import sys
import pygame as pg
from pygame.math import Vector2

class Player:
    def __init__(self, w, h):
        self.box = pg.rect.Rect((512,256), (w,h))
        self.speed = Vector2()
        self.force = Vector2()
        self.jumping  = False

    def update(self, keys, dt):
        self.force.y += 0.005
        if keys["w"] and not self.jumping:
            self.jumping = True
            self.speed.y += -1.5
        if keys["d"]:
            self.force.x += 0.005
        if keys["a"]:
            self.force.x += -0.005
            
        self.speed += self.force*dt
        print(self.force, self.speed)
        self.force.update()
        self.box.move_ip(*(self.speed*dt))

    def render(self):
        pg.draw.rect(pg.display.get_surface(), "red", self.box)


def handle_events(keys):
    for event in pg.event.get():
        if event.type == pg.QUIT:
            # NOTE(gerick): Dit kunnen we meer robust worden gemaakt in de toekomts als het moet
            pg.quit()
            sys.exit(0)
        if event.type == pg.KEYDOWN and event.key == pg.K_w:
            keys["w"] = True
        if event.type == pg.KEYUP and event.key == pg.K_w:
            keys["w"] = False
        if event.type == pg.KEYDOWN and event.key == pg.K_a:
            keys["a"] = True
        if event.type == pg.KEYUP and event.key == pg.K_a:
            keys["a"] = False
        if event.type == pg.KEYDOWN and event.key == pg.K_s:
            keys["s"] = True
        if event.type == pg.KEYUP and event.key == pg.K_s:
            keys["s"] = False
        if event.type == pg.KEYDOWN and event.key == pg.K_d:
            keys["d"] = True
        if event.type == pg.KEYUP and event.key == pg.K_d:
            keys["d"] = False


def draw_grid(window, size):
    h, w = window.get_height(), window.get_width()
    for i in range(0, h, size):
        pg.draw.line(window, "gray", (0, i), (w, i))
    for i in range(0, w, size):
        pg.draw.line(window, "gray", (i, 0), (i, h))


def main():
    CELL_SIZE = 64 # pixels
    WIN_RES = (16 * CELL_SIZE, 8 * CELL_SIZE) # 1024 x 512 pixels
    pg.init()
    window = pg.display.set_mode(WIN_RES)
    clock = pg.time.Clock()
    player = Player(1*CELL_SIZE,2*CELL_SIZE)
    keys = {
        "w": False,
        "a": False,
        "s": False,
        "d": False
    }
    while(True):
        # NOTE(gerick): de waarde van keys wordt veranderd
        handle_events(keys)
        dt = clock.get_time()
        player.update(keys, dt)

        if player.box.bottom > window.get_height() - CELL_SIZE:
            player.box.bottom = window.get_height() - CELL_SIZE
            player.speed.y = 0
            player.speed.x += -player.speed.x/10
            player.jumping = False

        window.fill("black")
        draw_grid(window, CELL_SIZE)
        player.render()

        pg.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
