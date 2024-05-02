#  working with graphics.

import os
import pygame
import general
import time
import world
import draw
import math
import random
import time

## Serves as a proxy image loader for tile images - all tile images
#  access should be done via this class.
#
#  The class uses lazy image loading.

class TileImageLoader:

  ## A dictionary that holds the images, the keys are tile ids.

  tile_images = {}

  ## Gets an TileImageContainer of a tile with given tile_id.
  #
  #  @param tile_type TileType object to get the image for
  #  @return tile image

  def get_tile_image(tile_type):
    if not (tile_type.identifier in TileImageLoader.tile_images):  # lazy image loading
      TileImageLoader.tile_images[tile_type.identifier] = TileImageContainer(os.path.join(general.RESOURCE_PATH,"tile_" + tile_type.name + ".png"))

    return TileImageLoader.tile_images[tile_type.identifier]

#=======================================================================

## Holds images (i.e. main tile variations, corners etc.) of a game
#  (terrain) tile, the corners are represented by a string in following
#  format: cornar_AB_XY, where A is U or D (up, down), B is L or R
#  (left, right) and X and Y are either 0 (opposite not present) or 1
#  (opposite present).
#  For example if there is a part of terrain as follows:
#    0 1
#    0 K L
#    1 K L
#  then for example in the upper left corner of L at [1,1] there should
#  be drawn a corner of K with identifier corner_UL_01.

class TileImageContainer:
  def init(self):
    self.main_tile = [None,None,None,None] # main tile variations or alternatively animation frames
    self.corner_UL_00 = None
    self.corner_UL_01 = None
    self.corner_UL_10 = None
    self.corner_UL_11 = None

    self.corner_UR_00 = None
    self.corner_UR_01 = None
    self.corner_UR_10 = None
    self.corner_UR_11 = None

    self.corner_DL_00 = None
    self.corner_DL_01 = None
    self.corner_DL_10 = None
    self.corner_DL_11 = None

    self.corner_DR_00 = None
    self.corner_DR_01 = None
    self.corner_DR_10 = None
    self.corner_DR_11 = None

  def __init__(self,filename):
    self.init()
    self.load_from_file(filename)

  def load_from_file(self,filename):
    image = pygame.image.load(filename)
    image = image.convert_alpha()

    self.main_tile[0] = image.subsurface(general.TILE_WIDTH * 2,0,general.TILE_WIDTH,general.TILE_HEIGHT)
    self.main_tile[1] = image.subsurface(general.TILE_WIDTH * 3,0,general.TILE_WIDTH,general.TILE_HEIGHT)
    self.main_tile[2] = image.subsurface(general.TILE_WIDTH * 2,general.TILE_HEIGHT,general.TILE_WIDTH,general.TILE_HEIGHT)
    self.main_tile[3] = image.subsurface(general.TILE_WIDTH * 3,general.TILE_HEIGHT,general.TILE_WIDTH,general.TILE_HEIGHT)

    self.corner_UL_00 = image.subsurface(general.SUBTILE_WIDTH * 3,general.SUBTILE_HEIGHT * 3,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)
    self.corner_UL_01 = image.subsurface(general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT * 3,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)
    self.corner_UL_10 = image.subsurface(general.SUBTILE_WIDTH * 3,general.SUBTILE_HEIGHT,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)
    self.corner_UL_11 = image.subsurface(general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)
    self.corner_UR_00 = image.subsurface(0,general.SUBTILE_HEIGHT * 3,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)
    self.corner_UR_01 = image.subsurface(general.SUBTILE_WIDTH * 2,general.SUBTILE_HEIGHT * 3,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)
    self.corner_UR_10 = image.subsurface(0,general.SUBTILE_HEIGHT,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)
    self.corner_UR_11 = image.subsurface(general.SUBTILE_WIDTH * 2,general.SUBTILE_HEIGHT,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)
    self.corner_DL_00 = image.subsurface(general.SUBTILE_WIDTH * 3,0,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)
    self.corner_DL_01 = image.subsurface(general.SUBTILE_WIDTH,0,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)
    self.corner_DL_10 = image.subsurface(general.SUBTILE_WIDTH * 3,general.SUBTILE_HEIGHT * 2,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)
    self.corner_DL_11 = image.subsurface(general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT * 2,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)
    self.corner_DR_00 = image.subsurface(0,0,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)
    self.corner_DR_01 = image.subsurface(general.SUBTILE_WIDTH * 2,0,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)
    self.corner_DR_10 = image.subsurface(0,28,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)
    self.corner_DR_11 = image.subsurface(general.SUBTILE_WIDTH * 2,general.SUBTILE_HEIGHT * 2,general.SUBTILE_WIDTH,general.SUBTILE_HEIGHT)

#=======================================================================

## Assembles images out of image resources.

class ImageCompositor:

  ## Makes a character image with given body, head, animation type, frame
  #  and gear
  #
  #  @param self object pointer
  #  @param body_name resource name of the body
  #
  #  @return Surface object - the generated image

  def make_character_image(self, race, gender, head_number, animation_type, animation_frame):

    animation_string = ""
    direction_string = ""
    race_string = ""
    gender_string = ""

    head_coordinates = (0,0)

    if race == general.RACE_HUMAN:
      race_string = "human"

    if gender == general.GENDER_MALE:
      gender_string = "male"
    else:
      gender_string = "female"

    if animation_type == general.ANIMATION_IDLE_UP:
      animation_string = "idle"
      direction_string = "up"
      head_coordinates = (4,0)
    elif animation_type == general.ANIMATION_IDLE_RIGHT:
      animation_string = "idle"
      direction_string = "right"
      head_coordinates = (6,0)
    elif animation_type == general.ANIMATION_IDLE_DOWN:
      animation_string = "idle"
      direction_string = "down"
      head_coordinates = (4,0)
    else:                         # idle left
      animation_string = "idle"
      direction_string = "left"
      head_coordinates = (3,0)

    image_head = pygame.image.load(os.path.join(general.RESOURCE_PATH,"character_" + race_string + "_" + gender_string + "_head_" + str(head_number) + "_" + direction_string + ".png"))

    if animation_type in (general.ANIMATION_IDLE_RIGHT,general.ANIMATION_IDLE_LEFT):
      image1 = pygame.image.load(os.path.join(general.RESOURCE_PATH,"character_" + race_string + "_" + gender_string + "_body_" + animation_string + "_" + direction_string + "_layer1.png"))
      image2 = pygame.image.load(os.path.join(general.RESOURCE_PATH,"character_" + race_string + "_" + gender_string + "_body_" + animation_string + "_" + direction_string + "_layer2.png"))
      image3 = pygame.image.load(os.path.join(general.RESOURCE_PATH,"character_" + race_string + "_" + gender_string + "_body_" + animation_string + "_" + direction_string + "_layer3.png"))

      image1.blit(image2,(0,0))
      image1.blit(image3,(0,0))
      image1.blit(image_head,head_coordinates)
    else:
      image1 = pygame.image.load(os.path.join(general.RESOURCE_PATH,"character_" + race_string + "_" + gender_string + "_body_" + animation_string + "_" + direction_string + ".png"))
      image1.blit(image_head,head_coordinates)

    return image1

  ## Helper private method that returns the priority of given tile type
  #  or 0 if the argument is not of TileType class.

  def __tile_priority(self, tile_type):
    try:
      return tile_type.priority
    except Exception:
      return 0

  ## Helper private method, returns ordered list of all tile priorities
  #  that appear in given TerrainArray object.

  def __make_tile_priority_list(self, terrain_array):
    result = []

    for j in range(terrain_array.height):
      for i in range(terrain_array.width):
        tile_type = terrain_array.get_tile_type(i,j)

        if tile_type != None and tile_type.animated:    # this maked animated tiles not render, they are drawn differently (the cannot be prerendered because they are changing constantly)
          continue

        priority = self.__tile_priority(tile_type)

        if not priority in result:
          result.append(priority)

    return sorted(result)

  ## Makes a terrain image.
  #
  #  @param terrain_array TerrainArray object to be drawn
  #  @return Surface object - the generated image

  def make_terrain_image(self, terrain_array):
    result_image = pygame.Surface((terrain_array.width * general.TILE_WIDTH, terrain_array.height * general.TILE_HEIGHT),flags = pygame.SRCALPHA)
    result_image.fill((255,255,255,0))

    for current_priority in self.__make_tile_priority_list(terrain_array):      # draw the terrain in layers
      for j in range(terrain_array.height):
        for i in range(terrain_array.width):
          tile_type = terrain_array.get_tile_type(i,j)

          if tile_type == None:
            continue

          tile_priority = tile_type.priority

          if tile_priority != current_priority:   # only draw one priority at a time
            continue

          variant = terrain_array.get_tile_variant(i,j)
          tile_id = tile_type.identifier

          tile_picture = TileImageLoader.get_tile_image(tile_type)

          # draw the main tile:
          result_image.blit(tile_picture.main_tile[variant],(i * general.TILE_WIDTH,j * general.TILE_HEIGHT))

          # draw corners and borders:

          # UL corner:
          if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i - 1,j - 1)) and \
             tile_priority > self.__tile_priority(terrain_array.get_tile_type(i,j - 1)) and \
             tile_priority > self.__tile_priority(terrain_array.get_tile_type(i - 1,j)):
           result_image.blit(tile_picture.corner_DR_00,(i * general.TILE_WIDTH - general.SUBTILE_WIDTH,j * general.TILE_HEIGHT - general.SUBTILE_HEIGHT))

          # UR corner
          if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i + 1,j - 1)) and \
             tile_priority > self.__tile_priority(terrain_array.get_tile_type(i,j - 1)) and \
             tile_priority > self.__tile_priority(terrain_array.get_tile_type(i + 1,j)):
            result_image.blit(tile_picture.corner_DL_00,(i * general.TILE_WIDTH + general.TILE_WIDTH,j * general.TILE_HEIGHT - general.SUBTILE_HEIGHT))

          # DR corner
          if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i + 1,j + 1)) and \
             tile_priority > self.__tile_priority(terrain_array.get_tile_type(i,j + 1)) and \
             tile_priority > self.__tile_priority(terrain_array.get_tile_type(i + 1,j)):
            result_image.blit(tile_picture.corner_UL_00,(i * general.TILE_WIDTH + general.TILE_WIDTH,j * general.TILE_HEIGHT + general.TILE_HEIGHT))

          # DL corner
          if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i - 1,j + 1)) and \
             tile_priority > self.__tile_priority(terrain_array.get_tile_type(i,j + 1)) and \
             tile_priority > self.__tile_priority(terrain_array.get_tile_type(i - 1,j)):
            result_image.blit(tile_picture.corner_UR_00,(i * general.TILE_WIDTH - general.SUBTILE_WIDTH,j * general.TILE_HEIGHT + general.TILE_HEIGHT))

          # upper border
          if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i,j - 1)):
            if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i - 1,j - 1)):  # left
              helper_image = tile_picture.corner_DL_01
            else:
              helper_image = tile_picture.corner_DL_11

            result_image.blit(helper_image,(i * general.TILE_WIDTH,j * general.TILE_HEIGHT - general.SUBTILE_HEIGHT))

            if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i + 1,j - 1)):  # right
              helper_image = tile_picture.corner_DR_01
            else:
              helper_image = tile_picture.corner_DR_11

            result_image.blit(helper_image,(i * general.TILE_WIDTH + general.SUBTILE_WIDTH,j * general.TILE_HEIGHT - general.SUBTILE_HEIGHT))

          # left border
          if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i - 1,j)):
            if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i - 1,j - 1)):  # up
              helper_image = tile_picture.corner_UR_10
            else:
              helper_image = tile_picture.corner_UR_11

            result_image.blit(helper_image,(i * general.TILE_WIDTH - general.SUBTILE_WIDTH,j * general.TILE_HEIGHT))

            if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i - 1,j + 1)):  # down
              helper_image = tile_picture.corner_DR_10
            else:
              helper_image = tile_picture.corner_DR_11

            result_image.blit(helper_image,(i * general.TILE_WIDTH - general.SUBTILE_WIDTH,j * general.TILE_HEIGHT + general.SUBTILE_HEIGHT))

          # right border
          if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i + 1,j)):
            if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i + 1,j - 1)):  # up
              helper_image = tile_picture.corner_UL_10
            else:
              helper_image = tile_picture.corner_UL_11

            result_image.blit(helper_image,(i * general.TILE_WIDTH + general.TILE_WIDTH,j * general.TILE_HEIGHT))

            if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i + 1,j + 1)):  # down
              helper_image = tile_picture.corner_DL_10
            else:
              helper_image = tile_picture.corner_DL_11

            result_image.blit(helper_image,(i * general.TILE_WIDTH + general.TILE_WIDTH,j * general.TILE_HEIGHT + general.SUBTILE_HEIGHT))

          # lower border
          if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i,j + 1)):
            if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i - 1,j + 1)):  # left
              helper_image = tile_picture.corner_UL_01
            else:
              helper_image = tile_picture.corner_UL_11

            result_image.blit(helper_image,(i * general.TILE_WIDTH,j * general.TILE_HEIGHT + general.TILE_HEIGHT))

            if tile_priority > self.__tile_priority(terrain_array.get_tile_type(i + 1,j + 1)):  # right
              helper_image = tile_picture.corner_UR_01
            else:
              helper_image = tile_picture.corner_UR_11

            result_image.blit(helper_image,(i * general.TILE_WIDTH + general.SUBTILE_WIDTH,j * general.TILE_HEIGHT + general.TILE_HEIGHT))

    return result_image

#=======================================================================

## Efficiently renders a part of the game world with given settings.
#
#  The object of WorldRenderer class keeps a reference to World object
#  which it will be rendering. It keeps a pre-rendered image of the
#  world's active area terrain so it can be rendered quickly for
#  real-time viewing. WorldRenderer will smartly change the world active
#  area when the view shifts to the edge of the current area.

class WorldRenderer:

  ## view width in pixels
  VIEW_WIDTH = 800

  ## view height in pixels
  VIEW_HEIGHT = 480

  ## view width in pixels
  VIEW_WIDTH_TILES = math.ceil(VIEW_WIDTH / general.TILE_WIDTH)

  ## view height in pixels
  VIEW_HEIGHT_TILES = math.ceil(VIEW_HEIGHT / general.TILE_HEIGHT)

  ## along with VIEW_WIDTH and VIEW_HEIGHT determines the active area
  #  size, which is width: VIEW_WIDTH_TILES + 2 * TILE_PADDING, height:
  #  VIEW_HEIGHT_TILES + 2 * TILE_PADDING

  TILE_PADDING = 15

  ## active area width in tiles

  ACTIVE_AREA_WIDTH = VIEW_WIDTH_TILES + 2 * TILE_PADDING

  ## active area height in tiles

  ACTIVE_AREA_HEIGHT = VIEW_HEIGHT_TILES + 2 * TILE_PADDING

  def _view_top_left_tiles(self):
    return (math.floor(self._view_top_left[0] / general.TILE_WIDTH),math.floor(self._view_top_left[1] / general.TILE_HEIGHT))

  @property
  def view_top_left(self):
    return self._view_top_left

  @view_top_left.setter
  def view_top_left(self,value):
    self._view_top_left = value
    in_tiles = self._view_top_left_tiles()

    # here the world active area is being potentially changed if the view rectangle is at the border of the active area:
    if ((self.world.active_area[0] > 0 and in_tiles[0] <= self.world.active_area[0]) or
        (self.world.active_area[1] > 0 and in_tiles[1] <= self.world.active_area[1]) or
        (self.world.active_area[0] + self.world.active_area[2] < self.world.width and in_tiles[0] + WorldRenderer.VIEW_WIDTH_TILES >= self.world.active_area[0] + self.world.active_area[2]) or
        (self.world.active_area[1] + self.world.active_area[3] < self.world.height and in_tiles[1] + WorldRenderer.VIEW_HEIGHT_TILES >= self.world.active_area[1] + self.world.active_area[3])):
      print("changing active area")
      print(self.world.get_active_area_props())

      self.__change_active_area()

  def __init_attributes(self):
    ## prerendered terrain of the active part of the world
    self.terrain_image = None
    ## position of the top left corner of the view rectangle in pixels
    self._view_top_left = (0,0)
    ## image to which the terrain will be rendered and which will be
    #  returned as the rendered part of the world
    self.canvas = pygame.Surface((WorldRenderer.VIEW_WIDTH,WorldRenderer.VIEW_HEIGHT))
    ## world that is being rendered
    self.world = None

  ## Gets the pixel coordinates of the top left corner of the view
  #  rectangle relative to the world active area.
  #
  #  @return pixel coordinates in format (x,y)

  def view_top_left_relative(self):
    return (self.view_top_left[0] - self.world.active_area[0] * general.TILE_WIDTH,self.view_top_left[1] - self.world.active_area[1] * general.TILE_HEIGHT)

  ## Same as view_top_left_relative, just returns tiles plus pixel
  #  difference.
  #
  #  @return tuple in format (x,y,pixel_diff_x,pixel_diff_y),
  #          pixel_diff_x and pixel_diff_y are the pixel difference
  #          relative to given tile

  def view_top_left_relative_tiles(self):
    pixel_coordinates = self.view_top_left_relative()
    x = math.floor(pixel_coordinates[0] / general.TILE_WIDTH)
    y = math.floor(pixel_coordinates[1] / general.TILE_HEIGHT)
    return (x,y,pixel_coordinates[0] - x * general.TILE_WIDTH,pixel_coordinates[1] - y * general.TILE_HEIGHT)

  def __init__(self,world):
    self.__init_attributes()
    self.world = world
    self.__change_active_area()

  ## Private method that is called to change the world active area and
  #  prerender the terrain for it. The active area is set depending on
  #  the current view coordinates.

  def __change_active_area(self):
    image_compositor = ImageCompositor()
    view_tile_coordinates = self._view_top_left_tiles()

    new_area = (general.saturate(view_tile_coordinates[0] - WorldRenderer.TILE_PADDING,0,self.world.width - WorldRenderer.ACTIVE_AREA_WIDTH),
                general.saturate(view_tile_coordinates[1] - WorldRenderer.TILE_PADDING,0,self.world.height - WorldRenderer.ACTIVE_AREA_HEIGHT),
                WorldRenderer.ACTIVE_AREA_WIDTH,
                WorldRenderer.ACTIVE_AREA_HEIGHT)

    self.world.active_area = new_area
    self.terrain_image = image_compositor.make_terrain_image(self.world.world_area)

  ## Renders the current world view.
  #
  #  @return the image (Surface object) of the rendered world area, its
  #          size is defined by VIEW_WIDTH and VIEW_HEIGHT constants,
  #          if the image couldn't be rendered (no world assigned etc.),
  #          None is returned

  def render(self):
    self.canvas.fill((255,0,0,0))

    view_top_left_tile = self.view_top_left_relative_tiles()

    # prepass, get objects in view to be rendered plus render animated files
    y = -view_top_left_tile[3]
    for j in range(view_top_left_tile[1],view_top_left_tile[1] + WorldRenderer.ACTIVE_AREA_HEIGHT):
      x = -view_top_left_tile[2]
      for i in range(view_top_left_tile[0],view_top_left_tile[0] + WorldRenderer.ACTIVE_AREA_WIDTH):
        tile_type = self.world.world_area.get_tile_type(i,j)
        if tile_type.animated:
          self.canvas.blit(TileImageLoader.get_tile_image(tile_type).main_tile[int(time.time()) % 4],(x,y))
        x += general.TILE_WIDTH
      y += general.TILE_HEIGHT

    view_relative = self.view_top_left_relative()
    self.canvas.blit(self.terrain_image,(-1 * view_relative[0],-1 * view_relative[1]))
    return self.canvas
