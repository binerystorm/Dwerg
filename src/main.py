import sys
import pygame as pg
from pygame.math import Vector2

def vec_mul(v1, v2):
    if type(v1) == tuple:
        v1 = Vector2(v1)
    if type(v2) == tuple:
        v2 = Vector2(v2)
    return Vector2(v1.x * v2.x , v1.y * v2.y)

class Hitbox:
    def __init__(self,  pos, size):
        self.pos = pos
        self.size = size
        self.collisions = {
            "v_bl": False,
            "v_br": False,
            "v_tl": False,
            "v_tr": False,
        }

    @property
    def horizontal_points(self):
        mid_left = self.top_left + (0, self.size.y/2)
        mid_right = self.top_right + (0, self.size.y/2)
        return [self.bottom_left, self.bottom_right, self.top_left, self.top_right, mid_left, mid_right]

    @property
    def vertical_points(self):
        return [self.bottom_left, self.bottom_right, self.top_left, self.top_right]

    @property
    def bottom_left(self):
        return Vector2(self.pos.x - self.size.x / 2, self.pos.y + self.size.y / 2)
    @property
    def bottom_right(self):
        return self.pos + self.size / 2
    @property
    def top_left(self):
        return self.pos - self.size / 2
    @property
    def top_right(self):
        return Vector2(self.pos.x + self.size.x/2, self.pos.y - self.size.y/2)
    @property
    def top(self):
        return self.pos.y - self.size.y / 2
    @top.setter
    def top(self, val):
        self.pos.y = val + self.size.y / 2
    @property
    def bottom(self):
        return self.pos.y + self.size.y / 2
    @bottom.setter
    def bottom(self, val):
        self.pos.y = val - self.size.y / 2
    @property
    def left(self):
        return self.pos.x - self.size.x / 2
    @left.setter
    def left(self, val):
        self.pos.x = val + self.size.x / 2
    @property
    def right(self):
        return self.pos.x + self.size.x / 2
    @right.setter
    def right(self, val):
        self.pos.x = val - self.size.x / 2

    def get_collisions(self, vel, game_map, dir):
        # TODO(gerick): Get rid of this and make proper map class as soon as possible
        map_size = Vector2(24, 8)
        map_get_tile = lambda x,y: " "  if int(y*map_size.x + x) < 0 or int(y*map_size.x + x) >= len(game_map) else game_map[int(y*map_size.x + x)]
        tile = lambda x: tuple(map(int, x))

        collisions = []
        for point in self.vertical_points if dir else self.horizontal_points:
            new_point = point + vel
            tile_loc = tuple(map(int, new_point))
            col_norm = new_point // 1 - point // 1
            # NOTE(gerick): ignore multidimentional tile crossings
            if abs(col_norm.x) == 1 and abs(col_norm.y) == 1:
                pass
                # TODO(gerick): figure out whether this commented code is needed.
                # if so figure out why it didn't work

                # diag_tile = tile(point + col_norm)
                # ver_tile = tile(point+vec_mul((0,1), col_norm))
                # hor_tile = tile(point+vec_mul((1,0), col_norm))
                # if map_get_tile(*ver_tile) == "#" and map_get_tile(*hor_tile):
                #     print("corner")
                # if map_get_tile(*ver_tile) == "#" and map_get_tile(*diag_tile) == "#":
                #     print("floor")
                # if map_get_tile(*hor_tile) == "#" and map_get_tile(*diag_tile) == "#":
                #     print("wall")
            elif map_get_tile(*tile(new_point)) == "#" and col_norm != (0,0):
                collisions.append((tile_loc, col_norm.copy()))
                
        return collisions


    def check_vertical_collisions(self, old_pos, game_map):
        # TODO(gerick): Get rid of this and make proper map class as soon as possible
        map_size = Vector2(24, 8)
        map_get_tile = lambda x,y: " "  if int(y*map_size.x + x) < 0 or int(y*map_size.x + x) >= len(game_map) else game_map[int(y*map_size.x + x)]

        col_norm = (self.pos.y + self.size.y/2) // 1 - (old_pos.y + self.size.y/2) // 1
        print(col_norm)
        if col_norm == 1 and map_get_tile(*map(int, self.bottom_right)) == "#":
            self.collisions["v_br"] = True
        if col_norm == 1 and map_get_tile(*map(int, self.bottom_left)) == "#":
            self.collisions["v_bl"] = True
        if col_norm == -1 and map_get_tile(*map(int, self.top_right)) == "#":
            self.collisions["v_tr"] = True
        if col_norm == -1 and map_get_tile(*map(int, self.top_left)) == "#":
            self.collisions["v_tl"] = True


class Player:
    def __init__(self, w, h):
        # TODO(gerick): Do we really want a rect hitbox?
        # self.box = pg.rect.Rect((512,256), (w,h))
        self.pos = Vector2()
        self.box = Hitbox(self.pos, Vector2(w,h))
        self.front = Vector2()
        self.back = Vector2()
        self.speed = Vector2()
        self.force = Vector2()

        # TODO(start thinking about whether these flags can be put in a state machine)
        self.jumping  = False
        self.double_jumping = False
        self.rolling  = False
        self.has_rolled = False
        self.has_jumped = False

        self.rolling_timer = 0
        self.dir = 1

    def update(self, keys, game_map, dt):
        # TODO(gerick): Remove floating constants
        # TODO(gerick): calculate more accuratly calculate movement speed and the force required

        self.force.y += 50
        if self.has_rolled and not keys['s']:
            self.has_rolled = False
        if self.has_jumped and not keys['w']:
            self.has_jumped = False
        if self.rolling:
            self.rolling_timer += dt
            if self.rolling_timer >= 325:
                self.rolling_timer = 0
                self.rolling = False
                bottom = self.box.bottom
                self.box.h = 64*2
                self.box.bottom = bottom

        # TODO(gerick): Rolling doesn't feel quite right, think of a better system for it
        if keys["s"] and not self.rolling and not self.jumping and not self.has_rolled:
            self.rolling = True
            self.has_rolled = True
            bottom = self.box.bottom
            self.box.h = 64
            self.box.bottom = bottom
            self.speed.x += 0.8 * self.dir
        if keys["w"] and not self.double_jumping and not self.has_jumped:
            self.has_jumped = True
            if self.jumping:
                self.double_jumping = True
            else:
                self.jumping = True
            self.speed.y = -17
        if keys["d"]:
            self.dir = 1
            if self.jumping:
                self.force.x += 20
            else:
                self.force.x += 50
        if keys["a"]:
            self.dir = -1
            if self.jumping:
                self.force.x += -20
            else:
                self.force.x += -50
            
        self.speed += self.force*dt
        if abs(self.speed.x) < 0.001:
            self.speed.x = 0
        if self.jumping:
            self.speed.x += -self.speed.x/25
        self.speed.x = pg.math.clamp(self.speed.x, -16, 16)
        # NOTE(gerick): Vector2.update() with no args sets the vector to 0
        self.force.update()
        # self.detect_collisions(game_map, dt)
        # self.box.move_ip(*(self.speed*dt))
        # self.pos += self.speed*dt
        for t, n in self.box.get_collisions(self.speed*dt, game_map, True):
            if n.y == 1:
                self.box.bottom = t[1] - 0.01
                self.speed.y = 0
                self.jumping = False
                self.double_jumping = False
                self.speed.x += -self.speed.x/15
            if n.y == -1:
                self.box.top = t[1] + 1 + 0.01
                self.speed.y = 0
        for t, n in self.box.get_collisions(self.speed*dt, game_map, False):
            if n.x == 1:
                self.speed.x = 0
                self.box.right = t[0] - 0.01
            if n.x == -1:
                self.speed.x = 0
                self.box.left = t[0] + 1 + 0.01

        self.box.pos += self.speed * dt

    def render(self):
        #pg.draw.circle(pg.display.get_surface(), "red", self.pos*64, 5)
        #pg.draw.circle(pg.display.get_surface(), "red", self.front*64, 5)
        #pg.draw.circle(pg.display.get_surface(), "red", self.back*64, 5)
        pink = "#"
        pg.draw.circle(pg.display.get_surface(), "red", self.box.bottom_left*64, 5)
        pg.draw.circle(pg.display.get_surface(), "red", self.box.bottom_right*64, 5)
        pg.draw.circle(pg.display.get_surface(), "red", self.box.top_left*64, 5)
        pg.draw.circle(pg.display.get_surface(), "red", self.box.top_right*64, 5)

        # rect = pg.rect.Rect(0,0,64, 2*64)
        # rect.midbottom = self.pos*64
        # pg.draw.rect(pg.display.get_surface(), "red", rect)
    #pg.draw.rect(pg.display.get_surface(), "red", self.box)


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
    map_size = Vector2(24, 8)
    game_map =  "........................"
    game_map += ".###...........####....."
    game_map += "........#..............."
    game_map += "........#..............."
    game_map += "...#########............"
    game_map += ".................#####.."
    game_map += "........................"
    game_map += "########################"
    map_get_tile = lambda x,y: " "  if int(y*map_size.x + x) < 0 or int(y*map_size.x + x) >= len(game_map) else game_map[int(y*map_size.x + x)]
    CELL_SIZE = 64 # pixels
    WIN_RES = (16 * CELL_SIZE, 8 * CELL_SIZE) # 1024 x 512 pixels
    pg.init()
    window = pg.display.set_mode(WIN_RES)
    clock = pg.time.Clock()
    player = Player(0.6,1.4)
    keys = {
        "w": False,
        "a": False,
        "s": False,
        "d": False
    }
    while(True):
        # NOTE(gerick): de waarde van keys wordt veranderd
        handle_events(keys)
        dt = clock.get_time() / 1000
        player.update(keys, game_map, dt)

        if player.pos.y > map_size.y - 1:
            player.pos.y = map_size.y - 1
            player.speed.y = 0
            # TODO(gerick): deccelaration is not time bound (low frames = lots of slide)
            player.speed.x += -player.speed.x/9
            player.jumping = False
            player.double_jumping = False

            
        window.fill("black")
        for x in range(int(map_size.x)):
            for y in range(int(map_size.y)):
                if map_get_tile(x,y) == " ":
                    print("ERROR", x, y)
                elif map_get_tile(x,y) == "#":
                    tile = pg.rect.Rect((x*CELL_SIZE, y*CELL_SIZE), (CELL_SIZE,CELL_SIZE))
                    pg.draw.rect(window, "blue", tile)
        draw_grid(window, CELL_SIZE)
        player.render()

        pg.display.flip()
        clock.tick(50)

if __name__ == "__main__":
    main()
