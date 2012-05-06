import pygame
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
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.img = SpriteSheet("tiles.png").image_at((0, 0, 20, 20))

  def render(self, dest):
    dest.blit(self.img, (self.x, self.y, 20, 20))

class Character(Entity):
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.speed = 6

    super(Character, self).__init__(self.x, self.y)

  def update(self, entities):
    dy = self.speed * (UpKeys.is_key_down(pygame.K_s) - UpKeys.is_key_down(pygame.K_w))
    dx = self.speed * (UpKeys.is_key_down(pygame.K_d) - UpKeys.is_key_down(pygame.K_a))

    self.x += dx
    self.y += dy

def main():
  screen = pygame.display.set_mode((300, 300))

  pygame.display.init()
  pygame.font.init()

  e = Entity(80, 80)
  char = Character(40, 40)

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
      if event.type == pygame.KEYDOWN:
        UpKeys.add_key(event.key)
      if event.type == pygame.KEYUP:
        UpKeys.release_key(event.key)

    char.update({})
    screen.fill((0, 0, 0))
    e.render(screen)
    char.render(screen)

    pygame.display.flip()

main()
