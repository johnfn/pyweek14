import pygame
from collections import defaultdict
import sys

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
    self.img = SpriteSheet("tiles.png").image_at((0, 0, 20, 20))

  def render(self, dest):
    dest.blit(self.img, (self.x, self.y, 20, 20))

  def touches(self, other):
    return abs(self.x - other.x) + abs(self.y - other.y)

class Character(Entity):
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.speed = 6

    super(Character, self).__init__(self.x, self.y, ["render", "update"])

  def update(self, entities):
    dy = self.speed * (UpKeys.is_key_down(pygame.K_s) - UpKeys.is_key_down(pygame.K_w))
    dx = self.speed * (UpKeys.is_key_down(pygame.K_d) - UpKeys.is_key_down(pygame.K_a))

    self.x += dx
    if len(entities.get("wall", lambda e: e.touches(self))): self.x -= dx
    self.y += dy
    if len(entities.get("wall", lambda e: e.touches(self))): self.x -= dy

data = """00000000000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000001000000000000
00000000000000000000""".split("\n")

class Map(Entity):
  def __init__(self):
    super(Map, self).__init__(0, 0, ["wall"])

  def touches(self, other):
    return data[other.y//20][other.x//20] == "1"

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
  screen = pygame.display.set_mode((300, 300))

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

    pygame.display.flip()

main()
