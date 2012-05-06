import pygame
from collections import defaultdict
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
  def __init__(self, x, y, groups):
    self.x = x
    self.y = y
    self.groups = groups
    self.img = SpriteSheet("tiles.png").image_at((0, 0, TILE_SIZE, TILE_SIZE))

  def render(self, dest):
    dest.blit(self.img, (self.x, self.y, TILE_SIZE, TILE_SIZE))

  def touches(self, other):
    return abs(self.x - other.x) + abs(self.y - other.y)

class Character(Entity):
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.vx = 0
    self.vy = 0
    self.on_ground = False

    self.speed = 6

    super(Character, self).__init__(self.x, self.y, ["render", "update"])

  def update(self, entities):
    if self.on_ground and UpKeys.is_key_down(pygame.K_w): 
      self.vy = -15

    dy = self.vy
    dx = self.speed * (UpKeys.is_key_down(pygame.K_d) - UpKeys.is_key_down(pygame.K_a))

    for _ in range(abs(dx)):
      self.x += sign(dx)
      if len(entities.get("wall", lambda e: e.touches(self))): 
        self.x -= sign(dx)
        break

    self.on_ground = False

    for _ in range(abs(dy)):
      self.y += sign(dy)
      if len(entities.get("wall", lambda e: e.touches(self))): 
        self.vy = 0
        self.y -= sign(dy)
        self.on_ground = True
        break

    self.vy += 1

data = """00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
00000000000000000000
11111111111111111110
00000000000000000000""".split("\n")

class Map(Entity):
  def __init__(self):
    super(Map, self).__init__(0, 0, ["wall", "render"])
    self.img = SpriteSheet("tiles.png").image_at((20, 0, TILE_SIZE, TILE_SIZE))
    self.map_w = 20
    self.map_h = 20

  def touches(self, other):
    try:
      return data[(other.y + 0 )//TILE_SIZE][(other.x + 0 )//TILE_SIZE] == "1" or \
             data[(other.y + 0 )//TILE_SIZE][(other.x + TILE_SIZE - 1)//TILE_SIZE] == "1" or \
             data[(other.y + TILE_SIZE - 1)//TILE_SIZE][(other.x + 0)//TILE_SIZE] == "1" or \
             data[(other.y + TILE_SIZE - 1)//TILE_SIZE][(other.x + TILE_SIZE - 1)//TILE_SIZE] == "1"
    except:
      print "out of bounds"
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

  def add(self, entity):
    groups = entity.groups
    groups.append("all")

    for group in groups:
      self.entities[group].add(entity)

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
  m = Map()
  char = Character(40, 40)
  entities.add(m)
  entities.add(char)

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
      if event.type == pygame.KEYDOWN:
        UpKeys.add_key(event.key)
      if event.type == pygame.KEYUP:
        UpKeys.release_key(event.key)

    char.update(entities)
    screen.fill((0, 0, 0))
    char.render(screen)
    m.render(screen)

    pygame.display.flip()

main()
