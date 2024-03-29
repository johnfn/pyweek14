from __future__ import division
from collections import defaultdict

import math
import pygame
import sys

TILE_SIZE = 20

def sign(x):
  if x > 0: return 1
  if x < 0: return -1
  return 0

def rects_touch(a, b):
    return a.x < b.x + TILE_SIZE and \
           a.x + TILE_SIZE > b.x and \
           a.y < other.y + TILE_SIZE and \
           a.y + TILE_SIZE > other.y

class Tick:
  ticks = 0

  @staticmethod
  def tick(): Tick.ticks += 1

  @staticmethod
  def get(n): return Tick.ticks % n == 0

class UpKeys:
  keysup = []
  keysdown = []

  @staticmethod
  def flush(): UpKeys.keysup = []

  @staticmethod
  def add_key(val):
    UpKeys.keysup.append(val)
    UpKeys.keysdown.append(val)

  @staticmethod
  def release_key(val):
    if val in UpKeys.keysdown: UpKeys.keysdown.remove(val)

  @staticmethod
  def invalidate_key(val):
    if val in UpKeys.keysup: UpKeys.keysup.remove(val)

  @staticmethod
  def is_key_down(val): return val in UpKeys.keysdown

  @staticmethod
  def is_key_up(val):
    if val in UpKeys.keysup:
      UpKeys.keysup.remove(val)
      return False
    return True

class SpriteSheet(object):
  saved_images = {}

  def __init__(self, filename):
    self.sheet = pygame.image.load(filename).convert()

  def image_at(self, rectangle, colorkey = None):
    if rectangle in SpriteSheet.saved_images:
      return SpriteSheet.saved_images[rectangle]

    rect = pygame.Rect(rectangle)
    image = pygame.Surface(rect.size).convert()
    image.blit(self.sheet, (0, 0), rect)

    if colorkey is not None:
      image.set_colorkey(colorkey, pygame.RLEACCEL)

    SpriteSheet.saved_images[rectangle] = image
    return image

class Entity(object):
  def __init__(self, x, y, tilesheet_coords, groups, entities):
    self.x = x
    self.y = y
    self.groups = groups
    self.img = SpriteSheet("tiles.png").image_at((tilesheet_coords[0], tilesheet_coords[1], TILE_SIZE, TILE_SIZE))
    self.size = TILE_SIZE

    entities.add(self)

  def boundary_points(self):
    return [[self.x, self.y], [self.x + self.size, self.y], [self.x, self.y + self.size], [self.x + self.size, self.y + self.size]]

  def in_bounds(self):
    return self.x > 0 and self.y > 0 and self.x <= 400 and self.y <= 400

  def hurt(self, amt, entities):
    assert(hasattr(self, 'hp'))

    self.hp -= amt
    if self.hp < 0:
      self.kill(entities)

  def kill(self, entities):
    entities.remove(self)

  def render(self, dest):
    dest.blit(self.img, (self.x, self.y, TILE_SIZE, TILE_SIZE))

  def touches(self, other):
    return (math.sqrt(abs(self.x ** 2 - other.x ** 2)) + math.sqrt(abs(self.y ** 2 - other.y ** 2))) < 100

class Enemy(Entity):
  def __init__(self, x, y, entities):
    super(Enemy, self).__init__(x, y, (2, 2), ["render", "update", "enemy"], entities)

    self.direction = {'x': 1, 'y': 0}
    self.speed = 4
    self.hp = 5
    self.hp_max = 5

  def update(self, entities):
    self.x += self.direction['x'] * self.speed
    self.y += self.direction['y'] * self.speed

    if not self.in_bounds():
      self.direction['x'] *= -1
      self.direction['y'] *= -1

class Bullet(Entity):
  def __init__(self, owner, direction, entities):
    super(Bullet, self).__init__(owner.x + 4, owner.y + 4, (0, 0), ["render", "update", "bullet"], entities)

    self.direction = owner.direction
    self.speed = 6
    self.dmg = 1
    self.size = 4

  def update(self, entities):
    self.x += self.direction['x'] * self.speed
    self.y += self.direction['y'] * self.speed

    if len(entities.get("wall", lambda e: e.touches(self))) or not self.in_bounds():
      self.kill(entities)

    enemies = entities.get("enemy", lambda e: e.touches(self))
    if len(enemies):
      enemies[0].hurt(self.dmg, entities)
      self.kill(entities)

class Bar(Entity):
  def __init__(self, x, y, entities):
    super(Bar, self).__init__(x, y, (0, 0), ["render", "update", "bar"], entities)

    self.width = 50
    self.height = 10
    self.border_width = 2

    self.img = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
    pygame.draw.rect(self.img, (0, 0, 255), (0, 0, self.width, self.height))

  def update(self, entities):
    pass

  def render(self, screen):
    screen.blit(self.img, (self.x, self.y))

class Character(Entity):
  def __init__(self, x, y, entities):
    self.vx = 0
    self.vy = 0
    self.on_ground = False
    self.LAG_FACTOR = 8

    self.speed = 4
    self.direction = {'x': 1, 'y': 0}

    super(Character, self).__init__(x, y, (1, 1), ["render", "update"], entities)
    self.size = TILE_SIZE - 1

  def check_shoot(self, entities):
    if not UpKeys.is_key_down(pygame.K_SPACE): return
    if not Tick.get(10): return

    b = Bullet(self, self.direction, entities)

  def update(self, entities):
    self.check_shoot(entities)

    if UpKeys.is_key_down(pygame.K_w):
      if self.on_ground and UpKeys.is_key_down(pygame.K_w):
        self.vy = -12
    else:
      self.vy = max(self.vy, 0)

    dy = self.vy
    dx = self.speed * (UpKeys.is_key_down(pygame.K_d) - UpKeys.is_key_down(pygame.K_a))

    if sign(dx) != 0:
      self.direction = {'x': sign(dx), 'y': 0}

    for _ in range(abs(int(dx))):
      self.x += sign(dx)
      if len(entities.get("wall", lambda e: e.touches(self))):
        self.x -= sign(dx)
        break

    self.on_ground = False

    for _ in range(abs(int(dy))):
      self.y += sign(dy)
      if len(entities.get("wall", lambda e: e.touches(self))):
        if sign(dy) > 0: self.on_ground = True
        self.vy = 0
        self.y -= sign(dy)
        break

    self.vy += 0.5

data = """00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000100010000000000
00000000000000000000
00000100010000000000
00000000000000000000
00010001001000000000
00000001100000000000
00000110000001000000
00000000000000000000
00000000100100010000
00000000000000000000
11111111111111111110
00000000000000000000""".split("\n")

class Map(Entity):
  def __init__(self, entities):
    super(Map, self).__init__(0, 0, (0, 0), ["wall", "render"], entities)
    self.img = SpriteSheet("tiles.png").image_at((20, 0, TILE_SIZE, TILE_SIZE))
    self.map_w = 20
    self.map_h = 20

  def is_wall(self, x, y):
    return data[y][x] == "1"

  def touches(self, other):
    try:
      for point in other.boundary_points():
        point = [coord//TILE_SIZE for coord in point]
        if self.is_wall(*point): 
          return True

      return False
    except:
      #print "out of bounds: TODO"
      return False

  def render(self, dest):
    for x in range(self.map_w):
      for y in range(self.map_h):
        if data[x][y] == "1":
          dest.blit(self.img, (y * 20, x * 20, 20, 20))

def isalambda(v):
  return isinstance(v, type(lambda: None)) and v.__name__ == '<lambda>'

class Entities(object):
  def __init__(self):
    self.entities = defaultdict(set)

  def get_all_groups(self, ent):
    groups = ent.groups[:]
    groups.append("all")

    return groups

  def add(self, entity):
    groups = self.get_all_groups(entity)

    for group in groups:
      self.entities[group].add(entity)

  def remove(self, entity):
    groups = self.get_all_groups(entity)
    
    for group in groups:
      self.entities[group].remove(entity)

  def get(self, *props):
    results = self.entities["all"]

    for p in props:
      if isinstance(p, str): results = results & self.entities[p]
      if isalambda(p): results = [e for e in results if p(e)]

    return results

def main():
  screen = pygame.display.set_mode((600, 600))

  pygame.display.init()
  pygame.font.init()

  entities = Entities()

  m = Map(entities)
  char = Character(40, 40, entities)
  e = Enemy(100, 100, entities)
  b = Bar(10, 10, entities)

  while True:
    Tick.tick()

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
      if event.type == pygame.KEYDOWN:
        UpKeys.add_key(event.key)
      if event.type == pygame.KEYUP:
        UpKeys.release_key(event.key)

    screen.fill((0, 0, 0))

    for e in entities.get("update"): e.update(entities)
    for e in entities.get("render"): e.render(screen)

    pygame.display.flip()

main()
