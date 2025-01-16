import sys
import pygame as pg
from pygame.math import Vector2
import enum


def vec_mul(v1, v2):
    if type(v1) == tuple:
        v1 = Vector2(v1)
    if type(v2) == tuple:
        v2 = Vector2(v2)
    return Vector2(v1.x * v2.x , v1.y * v2.y)

class KeyEvent:
    def __init__(self):
        self.down = False
        self.pressed = False

    # NOTE(gerick): This is conveluted lazyness on my part 
    # However I do think a general keyevent is a good idea
    # just not the bool method
    def __bool__(self):
        return self.down

    def activate(self):
        self.down = True
        self.pressed = True

    def deactivate(self):
        self.down = False
        self.pressed = False

class Camara:
    CELL_SIZE = 64
    SCREEN_TILES = Vector2(15,8)
    SCREEN_RES = SCREEN_TILES * CELL_SIZE
    def __init__(self):
        self.offset = Vector2() 
        self.w = self.SCREEN_TILES.x
        self.h = self.SCREEN_TILES.y

__default_camara = None
def get_camara():
    global __default_camara
    if __default_camara is None:
        raise Exception("Camara not set. Set with `set_camara(Camara)`")
    return __default_camara

def set_camara(cam):
    global __default_camara
    if type(cam) != Camara:
        raise Exception(f"set_camara expects camara type, recieved {type(cam)}")
    if __default_camara is not None:
        raise Exception("camara already set")
    else:
        __default_camara = cam

class Map:
    TEXTURE_SIZE = 16
    def __init__(self, w, h, data, path_texture):
        if w*h != len(data):
            raise ValueError("width and hieght values do not corolate with the data length")
        self.texture = pg.image.load(path_texture).subsurface(((0,16),(16,16)))
        self.w = w
        self.h = h
        self.data = data

    @classmethod
    def from_ascii_file(cls, path_map, path_texture):
        # TODO(gerick): missing texture managing
        # TODO(gerick): proper user error reporting
        with open(path_map, "r") as f:
            lines = f.readlines()
            lines = list(map(lambda x: x.strip(), lines))
            if len(lines) == 0:
                raise Exception(f"file: {path_map} is empty, can not load map")
            h = len(lines)
            w = len(lines[0])
            if any(map(lambda x: len(x) != w, lines)) or w == 0:
                raise Exception(f"Incorrect file format, can not load map")
        return cls(w, h, "".join(lines), path_texture)
            
    # TODO make camera class that is globaly accessible which contains of all
    # of the screen size and tile size info
    def render(self):
        cam = get_camara()
        texture_to_render = pg.transform.scale_by(self.texture, cam.CELL_SIZE / self.TEXTURE_SIZE)
        # for x in range(int(cam.offset.x), int(cam.offset.x + cam.SCREEN_TILES.x)+1):
        #     for y in range(int(cam.offset.y), int(cam.offset.y + cam.SCREEN_TILES.y)+1):
        for x in range(self.w):
            for y in range(self.h):
                if self[x,y] == "#":
                    # tile_loc = Vector2((x-cam.offset.x)*cam.CELL_SIZE, y*cam.CELL_SIZE)
                    tile_loc = (Vector2(x,y) - cam.offset) * cam.CELL_SIZE
                    pg.display.get_surface().blit(texture_to_render, tile_loc)
                    #pg.draw.rect(pg.display.get_surface(), "blue", tile)
                

    def __getitem__(self, idx):
        if type(idx) != tuple:
            raise IndexError("Map takes two index values, one was given")
        if (n := len(idx)) > 2:
            raise IndexError(f"Map takes two index values, {n} were given")
        if not all(map(lambda x: type(x) == int, idx)):
            raise IndexError(f"Map indexing requires intereger arguments")

        x, y = idx
        if not (0 <= x < self.w):
            raise IndexError(f"X is out of bounds: x:{x} range:{0}-{self.w-1}")
        if not (0 <= y < self.h):
            raise IndexError(f"Y is out of bounds: x:{y} range:{0}-{self.h-1}")
        return self.data[y*self.w + x]

__game_map = Map.from_ascii_file("./test_map.ascii", "./tile_sheet_crappy.png")
def get_current_map():
    global __game_map
    return __game_map

def xor(b1, b2):
    if type(b1) == bool and type(b2) == bool:
        return (b1 or b2) and not (b1 and b2)
    if type(b1) == KeyEvent and type(b2) == KeyEvent:
        return (b1 or b2) and not (b1 and b2)
    
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

    def get_collisions(self, vel, dir):
        # ERROR(gerick): funcy bussniss going when leaving the confines of the map,
        # only throws error when half the sprite leaves in the up and left directions
        
        tile = lambda x: tuple(map(int, x))
        game_map = get_current_map()

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
            elif game_map[*tile(new_point)] == "#" and col_norm != (0,0):
                collisions.append((tile_loc, col_norm.copy()))
                
        return collisions

class PlayerState(enum.Enum):
    idle = 0
    running = 1
    slowing = 2
    jumping = 3
    d_jumping = 4
    falling = 5
    d_falling = 6
    rolling = 7

class Player:
    TEXTURE_SIZE = 32
    def __init__(self, w, h):
        self.camara = Camara()
        self.SCALE_FACTOR = (self.camara.CELL_SIZE/self.TEXTURE_SIZE) * 2
        self.sprite_sheet = pg.transform.scale_by(pg.image.load("./dwarf.png"), self.SCALE_FACTOR)
        self.sprite_idx = 0
        self.idle_elap_frame = 0
        self.box = Hitbox(Vector2(), Vector2(w,h))
        self.speed = Vector2()
        self.force = Vector2()
        set_camara(self.camara)

        # TODO(gerick): start thinking about whether these flags can be put in a state machine
        self.state = PlayerState.idle
        self.jumping  = False
        self.double_jumping = False
        self.rolling  = False
        self.has_rolled = False
        self.has_jumped = False

        self.rolling_timer = 0
        self.dir = 1

    def update(self, keys, dt):
        self.force.y += 50

        # TODO(gerick): set up state anitialization functions, so setup does not need to be done at every state change
        # TODO(gerick): turn this into a series of ifs if's so states can share code
        match self.state:
            case PlayerState.idle:
                if self.idle_elap_frame == 5:
                    self.idle_elap_frame = 0
                    self.sprite_idx = (self.sprite_idx + 1) % 5
                if keys["w"].pressed:
                    self.state = PlayerState.jumping
                    self.speed.y = -17
                    self.idle_elap_frame = 0
                    self.sprite_idx = 0
                if xor(keys['a'], keys['d']):
                    self.state = PlayerState.running
                    self.idle_elap_frame = 0
                    self.sprite_idx = 0

                self.idle_elap_frame += 1
            case PlayerState.running:
                if not xor(keys['a'], keys['d']):
                    self.state = PlayerState.slowing
                else:
                    if keys['a']:
                        self.dir = -1
                    elif keys['d']:
                        self.dir = 1
                    self.force.x += 50 * self.dir

                if keys["w"].pressed:
                    self.state = PlayerState.jumping
                    self.speed.y = -17
            case PlayerState.slowing:
                if keys["w"].pressed:
                    self.state = PlayerState.jumping
                    self.speed.y = -17

                if xor(keys['a'], keys['d']):
                    self.state = PlayerState.running

                if abs(self.speed.x) < 0.01:
                    self.state = PlayerState.idle
                    self.speed.x = 0

            case PlayerState.rolling:
                pass

            # NOTE(gerick): all air movement is the same so it is handled in the if below
            case PlayerState.jumping:
                if self.speed.y > 0:
                    self.state = PlayerState.falling
                if keys['w'].pressed:
                    self.state = PlayerState.d_jumping
                    self.speed.y = -17
            case PlayerState.d_jumping:
                if self.speed.y > 0:
                    self.state = PlayerState.d_falling
            case PlayerState.falling:
                if keys['w']:
                    self.state = PlayerState.d_jumping
                    self.speed.y = -17
            case PlayerState.d_falling:
                pass

        if self.state in (PlayerState.falling, PlayerState.d_falling, PlayerState.jumping, PlayerState.d_jumping):
            # air resistance
            if xor(keys['a'], keys['d']):
                if keys['a']:
                    self.dir = -1
                elif keys['d']:
                    self.dir = 1

                self.force.x += 20 * self.dir
            self.speed.x += -self.speed.x/25

        self.speed += self.force*dt
        # NOTE(gerick): Vector2.update() with no args sets the vector to 0
        self.force.update()

        ground_collision = False
        # NOTE(gerick): I do not know if it is wise to allow states to be
        # changed from outside the state machine but it is currently the 
        # simeples sollution and there for the one I adopt
        for t, n in self.box.get_collisions(self.speed*dt, True):
            if n.y == 1:
                ground_collision = True
                self.box.bottom = t[1] - 0.01
                self.speed.y = 0
                self.speed.x += -self.speed.x/15

                # State changing logic
                if self.state in (PlayerState.falling, PlayerState.d_falling):
                    if self.speed.x == 0: self.state = PlayerState.idle
                    elif xor(keys['a'], keys['d']): self.state = PlayerState.running
                    else: self.state = PlayerState.slowing

            if n.y == -1:
                self.box.top = t[1] + 1 + 0.01
                self.speed.y = 0
        for t, n in self.box.get_collisions(self.speed*dt, False):
            # TODO(gerick): maybe add a player smashed into wall state for the animation
            if n.x == 1:
                self.state = PlayerState.idle
                self.speed.x = 0
                self.box.right = t[0] - 0.01
            if n.x == -1:
                self.state = PlayerState.idle
                self.speed.x = 0
                self.box.left = t[0] + 1 + 0.01


        if not ground_collision and self.speed.y > 0 and self.state not in (PlayerState.falling, PlayerState.d_falling, PlayerState.jumping, PlayerState.d_jumping):
            self.state = PlayerState.falling

        self.box.pos += self.speed * dt

        if self.box.pos.y - self.camara.offset.y >= self.camara.SCREEN_TILES.y - 2:
            x = (self.box.pos.y - self.camara.offset.y) - (self.camara.SCREEN_TILES.y - 2)
            self.camara.offset.y += x
        if self.box.pos.y - self.camara.offset.y <= 2:
            x = abs(self.box.pos.y - self.camara.offset.y - 2)
            self.camara.offset.y -= x
        if self.box.pos.x - self.camara.offset.x >= self.camara.SCREEN_TILES.x - 5:
            x = (self.box.pos.x - self.camara.offset.x) - (self.camara.SCREEN_TILES.x - 5)
            self.camara.offset.x += x
        if self.box.pos.x - self.camara.offset.x <= 5:
            x = abs(self.box.pos.x - self.camara.offset.x - 5)
            self.camara.offset.x -= x
        self.camara.offset.x = pg.math.clamp(self.camara.offset.x, 0, get_current_map().w - self.camara.w)
        self.camara.offset.y = pg.math.clamp(self.camara.offset.y, 0, get_current_map().h - self.camara.h)
        self.box.pos.x = pg.math.clamp(self.box.pos.x, 0, get_current_map().w)



    def render(self):
        # TODO(gerick): fix the sprite drawing locaction so it better fits the hitbox
        # (e.g. the sprite is in a different location relative to the hitbox when fliped)
        # TODO(gerick): get rid of all the magic constants and make the al relative to the 
        # screen size and cell size
        sprite_loc = self.box.bottom_left - self.camara.offset - (0.7, 2)
        # sprite_to_draw = self.sprite if self.dir > 0 else pg.transform.flip(self.sprite, 1, 0)
        scaled_texture_size = self.TEXTURE_SIZE*self.SCALE_FACTOR
        if self.dir > 0:
            sprite_to_draw = self.sprite_sheet.subsurface((self.sprite_idx * scaled_texture_size, 0, scaled_texture_size, scaled_texture_size))
        else:
            sprite_to_draw = pg.transform.flip(self.sprite_sheet.subsurface((self.sprite_idx * scaled_texture_size, 0, scaled_texture_size, scaled_texture_size)), 1, 0)

        pg.draw.circle(pg.display.get_surface(), "red", (self.box.bottom_left - self.camara.offset)*self.camara.CELL_SIZE, 5)
        pg.draw.circle(pg.display.get_surface(), "red", (self.box.bottom_right - self.camara.offset)*self.camara.CELL_SIZE, 5)
        pg.draw.circle(pg.display.get_surface(), "red", (self.box.top_left - self.camara.offset)*self.camara.CELL_SIZE, 5)
        pg.draw.circle(pg.display.get_surface(), "red", (self.box.top_right - self.camara.offset)*self.camara.CELL_SIZE, 5)
        pg.display.get_surface().blit(sprite_to_draw, sprite_loc * self.camara.CELL_SIZE)

        # rect = pg.rect.Rect(0,0,64, 2*64)
        # rect.midbottom = self.pos*64
        # pg.draw.rect(pg.display.get_surface(), "red", rect)
    #pg.draw.rect(pg.display.get_surface(), "red", self.box)


def handle_events(keys):
    # TODO(gerick): more understandable robust system for key presses needed
    for k, v in keys.items():
        if v.pressed: keys[k].pressed = False

    for event in pg.event.get():
        if event.type == pg.QUIT:
            # NOTE(gerick): Dit kunnen we meer robust worden gemaakt in de toekomts als het moet
            pg.quit()
            sys.exit(0)
        if event.type == pg.KEYDOWN and event.key == pg.K_w:
            keys['w'].activate()
        if event.type == pg.KEYUP and event.key == pg.K_w:
            keys['w'].deactivate()
        if event.type == pg.KEYDOWN and event.key == pg.K_a:
            keys['a'].activate()
        if event.type == pg.KEYUP and event.key == pg.K_a:
            keys['a'].deactivate()
        if event.type == pg.KEYDOWN and event.key == pg.K_s:
            keys['s'].activate()
        if event.type == pg.KEYUP and event.key == pg.K_s:
            keys['s'].deactivate()
        if event.type == pg.KEYDOWN and event.key == pg.K_d:
            keys['d'].activate()
        if event.type == pg.KEYUP and event.key == pg.K_d:
            keys['d'].deactivate()


def draw_grid(window, size):
    h, w = window.get_height(), window.get_width()
    for i in range(0, h, size):
        pg.draw.line(window, "gray", (0, i), (w, i))
    for i in range(0, w, size):
        pg.draw.line(window, "gray", (i, 0), (i, h))


def main():
    # CELL_SIZE = 128 # pixels
    # WIN_TILES = Vector2(15, 8)
    # WIN_RES = WIN_TILES * CELL_SIZE

    # WIN_RES = (16 * CELL_SIZE, 8 * CELL_SIZE) # 1024 x 512 pixels
    pg.init()
    game_map = get_current_map()
    player = Player(0.7, 1.4)
    window = pg.display.set_mode(get_camara().SCREEN_RES)
    clock = pg.time.Clock()
    # camera_offset = Vector2(0,0)
    keys = {
        "w": KeyEvent(),
        "a": KeyEvent(),
        "s": KeyEvent(),
        "d": KeyEvent()
    }
    while(True):
        # NOTE(gerick): de waarde van keys wordt veranderd
        handle_events(keys)
        dt = clock.get_time() / 1000
        player.update(keys, dt)

            
        window.fill("black")
        game_map.render()
        #draw_grid(window, get_camara().CELL_SIZE)
        player.render()

        pg.display.flip()
        clock.tick(50)

if __name__ == "__main__":
    main()
