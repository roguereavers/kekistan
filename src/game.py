# main game file


import general
import world
import pygame
import math

#=======================================================================

pygame.init()
mommy = 0
screen = pygame.display.set_mode((800,480))

done = False

## w = world.World("\resources")

World = pygame.image.load('resources/IMG-DairyTopBar.jpg')

print(World)

renderer = (World)

go_up = False
go_down = False
go_left = False
go_right = False

while not done:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      done = True
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_LEFT:
        go_left = True
      elif event.key == pygame.K_RIGHT:
        go_right = True
      if event.key == pygame.K_UP:
        go_up = True
      elif event.key == pygame.K_DOWN:
        go_down = True
    elif event.type == pygame.KEYUP:
      if event.key == pygame.K_LEFT:
        go_left = False
      elif event.key == pygame.K_RIGHT:
        go_right = False
      if event.key == pygame.K_UP:
        go_up = False
      elif event.key == pygame.K_DOWN:
        go_down = False

class Waifu(pygame.sprite.Sprite):
    def __init__(self):
        super(Cloud, self).__init__()
        self.surf = pygame.image.load("resources/IMG-LadyOfTheWoods2.jpg").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        # The starting position is randomly generated
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )

      )
        def update(self): 
            self.rect.move_ip(-5, 0)
            if self.rect.right < 0:
                 self.kill()


# Define a mommy object by extending pygame.sprite.Sprite
# The surface drawn on the screen is now an attribute of 'mommy'
class mommy(pygame.sprite.Sprite):
    def __init__(self):
        super(mommy, self).__init__()
        self.surf = pygame.Surface((75, 25))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        
# Fill the screen with black
screen.fill((0, 0, 0))

# Update the display
pygame.display.flip()

# Define the enemy object by extending pygame.sprite.Sprite
# The surface you draw on the screen is now an attribute of 'enemy'
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.Surface((20, 10))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(5, 20)

    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()
            