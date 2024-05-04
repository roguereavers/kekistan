## \file kek.py
#
#  This file contains main game core classes.

import os
import pygame
import general
import time
import sys
import numpy

#=======================================================================

## Represents an abstract RPG object class.
#
#  An RPG object class is a template for concrete RPG objects. This
#  includes for example an item template, whereas the concrete item
#  instance in the kek is an RPG object instance.

class RPGObjectClass:
  def __init__(self):
    return

#=======================================================================

## Represents an abstract RPG object instance.
#
#  An RPG object instance is an instance of an RPG object class, i.e.
#  a concrete existing object, not a template for it.

class RPGObjectInstance:
  def __init__(self):
    return

#=======================================================================

## Represents an abstract instance placed in the kek.
#
#  That is an instance that is placed in the game kek, in an exterior
#  or an interior, such as a tree, an item placed on ground, a cow etc.
#  This doesn't include an item in inventory or a spell as they aren't
#  placed directly in the kek.

class kekInstance:
  def __init_attributes(self):
    return

  def __init__(self):
    return

#=======================================================================

## Represents a kek object that is placed at given tile of the
#  terrain.
#
#  That means that its position consists of two integers.

class TilekekInstance(kekInstance):
  def __init__(self):
    return

#=======================================================================

## Represents a kek object that is placed at given precise
#  position in the kek.
#
#  That means its position consists of two floating-point numbers.

class FloatingkekInstance(kekInstance):
  def __init__(self):
    return

#=======================================================================

## Represents a game tile type (RPG class). I.e. not a single tile but
#  rather a type of tile, such as grass, road etc.

class TileType:
  last_identifier = 0

  ## Private method, initialises the default attribute values

  def __init_attributes(self):
    ## tile with higher priority will overlap the tile with lower
    #  priority at their borders
    self.priority = 0
    ## tile name
    self.name = ""
    ## whether the tile is animated
    self.animated = False
    ## number of tile variants in range <1,4>
    self.variants = 1
    ## whether the tile is steppable
    self.steppable = True
    ## whether the tile can be flied over
    self.flyable = True
    ## whether the tile can be swimmed on
    self.swimmable = False
    ## unique tile identifier
    self.identifier = TileType.last_identifier
    TileType.last_identifier += 1

  def __init__(self):
    self.__init_attributes()

  ## Initialises a new object with given attribute values.
  #
  #  @param priority integer tile priority, this affects how the tiles
  #         overlap
  #  @param name name of the the tile, it is not a filename, so only  a
  #         name must be given without a path to it or a file extension,
  #         for example: "grass"
  #  @param variants number of tile variants (if not animated) or
  #         animation frames (if animated), must be integer in range
  #         <1,4>
  #  @param steppable whether the tile can be stepped on (bool)
  #  @param flyable whether the tile can be flied over (bool)
  #  @param swimmable whether the tile can be swimmed on (bool)

  def __init__(self, priority = 0, name = "", steppable = True, variants = 1, animated = False, flyable = True, swimmable = False):
    self.__init_attributes()
    self.priority = priority
    self.steppable = steppable
    self.variant = variants
    self.animated = animated
    self.flyable = flyable
    self.name = name
    self.swimmable = swimmable

  def __str__(self):
    return "Tile: '" + self.name + "' (" + str(self.identifier) + "), prior.: " + str(self.priority) + ", step.: " + str(self.steppable) + ", fly.: " + str(self.flyable) + ", swim.: " + str(self.swimmable)

#=======================================================================

## Represents a prop type (RPG class), not a concrete prop (RPG
#  instance).

class PropType:
  ## Private method, initialises the default attribute values.

  def __init_attributes(self):
    ## prop name, is used to construct a filename of the prop image
    self.name = ""
    ## an id of the shadow for the prop, negative value means no shadow
    self.shadow = -1
    ## prop width in tiles
    self.width = 0
    ## prop height in tiles
    self.height = 0
    ## whether the prop can be walked on
    self.walkable = False
    ## whether the prop can be flown over
    self.flyable = True
    ## whether the prop can be swimmed at
    self.swimmable = False
    ## number of animation frames
    self.frames = 1
    ## animation speed multiplier
    self.animation_speed = 1.0
    ## if the prop is drawn in lower or upper layer
    self.draw_in_foreground = True
    ## 2D array of boolean values representing the prop mask that says
    #  which tiles of the width x height rectangle the prop
    #  actualy occupies
    self.mask = None

  def __str__(self):
    result = "prop '" + self.name + "' :\n"
    result += "  shadow id = " + str(self.shadow) + "\n"
    result += "  size = " + str(self.width) + " x " + str(self.height) + "\n"
    result += "  walk/fly/swim = " + str(int(self.walkable)) + str(int(self.flyable)) + str(int(self.swimmable)) + "\n"
    result += "  animation frames = " + str(self.frames) + "\n"
    result += "  animation speed = " + str(self.animation_speed) + "\n"
    result += "  foreground = " + str(self.draw_in_foreground) + "\n"
    result += "  mask = " + str(self.mask)
    return result

  def __init__(self):
    self.__init_attributes()

#=======================================================================

## Represents a prop RPG instance, i.e. a concrete prop placed in the
#  kek.

class PropInstance:
  ## Private method, initialises the default attribute values.

  def __init_attributes(self):
    ## references the prop type (RPG class)
    self.prop_type = None
    ## position of the lower bottom corner of the prop in game tiles
    self.position = (0,0)

  def __str__(self):
    result = "prop instance: class = " + self.prop_type.name + ", position = [" + str(self.position[0]) + "," + str(self.position[1]) + "]\n"
    return result

  @property
  def width(self):
    return self.prop_type.width

  @property
  def height(self):
    return self.prop_type.height

  def __init__(self):
    self.__init_attributes()

#=======================================================================

## Represents a part of kek. It is basically a 2D array of triplets
#  [TileType reference,variant (int),object list] where object list is
#  reference to a list of objects at given tile or None.

class kekArea:
  def __init__(self, width, height):

    ## the terrain array, it's format is [x][y][tiletype,variant,object_list]:
    self.terrain_array = numpy.zeros((width,height),dtype=object)

    if (len(self.terrain_array) != 0):
      for j in range(len(self.terrain_array[0])):
        for i in range(len(self.terrain_array)):
          self.terrain_array[i,j] = numpy.array([None,0,None])

  ## the area width in tiles

  @property
  def width(self):
    return len(self.terrain_array)

  ## the area height in tiles

  @property
  def height(self):
    if self.width == 0:
      return 0
    else:
      return len(self.terrain_array[0])

  ## Sets the tile at given position. If the position is outside the
  #  terrain, nothing happens.

  def set_tile(self, x, y, tile_type, variant, object_list):
    try:
      self.terrain_array[x][y][0] = tile_type
      self.terrain_array[x][y][1] = variant
      self.terrain_array[x][y][2] = object_list
    except IndexError:
      return

  ## Gets the tile type at given position.
  #
  #  @return tile type object at [x,y], if the position is outside
  #          terrain array, closest tile type is returned

  def get_tile_type(self, x, y):
    return self.terrain_array[general.saturate(x,0,self.width - 1)][general.saturate(y,0,self.height - 1)][0]

  ## Same as get_tile_type, just returns the tile variant.

  def get_tile_variant(self, x, y):
    return self.terrain_array[general.saturate(x,0,self.width - 1)][general.saturate(y,0,self.height - 1)][1]

  ## Same as get_tile_type, just returns the object list.

  def get_object_list(self, x, y):
    return self.terrain_array[general.saturate(x,0,self.width - 1)][general.saturate(y,0,self.height - 1)][2]

  def __str__(self):
    result = ""

    for j in range(self.height):
      for i in range(self.width):
        tile_type = self.get_tile_type(i,j)
        tile_variant = self.get_tile_variant(i,j)

        if tile_type == None:
          result += "N (" + str(tile_variant) + ") "
        else:
          result += str(tile_type.identifier) + " (" + str(tile_variant) + ") "

      result += "\n"

    return result

#=======================================================================

## Represents a concrete tile in game kek, consists of tile type
#  plus objects at the tile.

class TileInfo:

  def __init__(self, tile_type, game_object_list):
    ## type of the tile
    self.tile_type = tile_type
    ## objects at the tile
    self.objects = game_object_list

#=======================================================================

## Represents the game kek and a proxy for game kek file.
#
#  The kek consists of 2D array of game tiles plus NPCs, objects, items
#  etc. There is always an active area of the kek, which is the
#  player's close area, the class provides methods for setting the
#  and handling the active area as well as the rest of the kek.

class kek:

  ## Private method, loads all the items from the kek file except for
  #  terrain, this is done with __load_active_terrain().

  def __load_non_terrain(self):
    kek_file = open("resources\kek.tmx")

    for line in kek_file:

      #-------------------------
      if general.begins_with(line,"shadows:"):            # load shadows
        while True:
          line2 = kek_file.readline()

          if general.begins_with(line2,"end"):
            break

          split_line = line2.split()

          self.shadows[int(split_line[0])] = split_line[1]
      #-------------------------
      if general.begins_with(line,"prop_instances:"):     # load prop instances
        while True:
          line2 = kek_file.readline()

          if general.begins_with(line2,"end"):
            break

          split_line = line2.split()

          new_instance = PropInstance()
          new_instance.position = (int(split_line[2]),int(split_line[3]))
          new_instance.prop_type = self.prop_types[int(split_line[1])]

          self.prop_instances[int(split_line[0])] = new_instance
      #-------------------------
      if general.begins_with(line,"prop_classes:"):       # load prop classes
        while True:
          line2 = kek_file.readline()

          if general.begins_with(line2,"end"):
            break

          split_line = line2.split()

          prop_type = PropType()
          prop_type.name = split_line[1]
          prop_type.shadow = int(split_line[2])
          prop_type.width = int(split_line[3])
          prop_type.height = int(split_line[4])
          prop_type.walkable = split_line[5] == "T"
          prop_type.swimmable = split_line[6] == "T"
          prop_type.flyable = split_line[7] == "T"
          prop_type.frames = int(split_line[8])
          prop_type.animation_speed = float(split_line[9])
          prop_type.draw_in_front = split_line[10] == "T"
          # load the mask:
          prop_type.mask = numpy.zeros((prop_type.width,prop_type.height),dtype=object)

          helper_position = 2 # the field where the mask sequence begins

          for j in range(prop_type.height):
            for i in range(prop_type.width):
              prop_type.mask[i,j] = int(split_line[helper_position]) == 1
              helper_position += 1

          self.prop_types[int(split_line[0])] = prop_type
      #-------------------------
      if general.begins_with(line,"tiles:"):              # load tiles
        while True:
          line2 = kek_file.readline()

          if general.begins_with(line2,"end"):
            break

          split_line = line2.split()

          self.tile_types[int(split_line[0])] = TileType(int(split_line[2]),split_line[1],split_line[5] == "T",int(split_line[3]),split_line[4] == "T",split_line[6] == "T",split_line[7] == "T")
      #-------------------------
      if general.begins_with(line,"terrain:"):            # load kek size
        self.kek_width = int(kek_file.readline())
        self.kek_height = int(kek_file.readline())

        while True:
          line2 = kek_file.readline()

          if general.begins_with(line2,"end"):
            break
      #-------------------------

    kek_file.close()

  ## Gets the props in current active area. This include props that are
  #  only partially contained within the area.
  #
  #  @return list of props in current active area

  def get_active_area_props(self):
    result = []

    # active area in format (x1, y1, x2, y2):
    active_area = (self.active_area[0], self.active_area[1], self.active_area[0] + self.active_area[2], self.active_area[1] + self.active_area[3])

    for prop_id in self.prop_instances:
      prop = self.prop_instances[prop_id]

      # prop position in format (x1, y1, x2, y2):
      prop_position = (prop.position[0],prop.position[1],prop.position[0] + prop.width,prop.position[1] + prop.height)

      if ( (prop_position[0] > active_area[0] and prop_position[0] < active_area[2]) or
           (prop_position[2] > active_area[0] and prop_position[2] < active_area[2]) ):
        if ( (prop_position[1] > active_area[1] and prop_position[1] < active_area[3]) or
             (prop_position[3] > active_area[1] and prop_position[3] < active_area[3]) ):
          result.append(prop)

    return result

  ## Private method, loads the active terrain area from the kek file.

  def __load_active_terrain(self):
    kek_file = open("resources\kek.tmx")
    end_it = False

    self.kek_area = kekArea(self._active_area[2],self._active_area[3])

    helper_width = self._active_area[2]
    helper_height = self._active_area[3]

    for line in kek_file:

      if line[:8] == "terrain:":     # load tiles
        kek_file.readline()        # skip the width and height lines
        kek_file.readline()

        counter = 0

        while counter < self._active_area[1]:
          kek_file.readline()
          counter += 1

        y = 0

        while counter < self._active_area[1] + helper_height:
          line2 = kek_file.readline()

          if line2[:3] == "end":
            end_it = True
            break

          terrain_line = line2.split()

          for x in range(0,helper_width):
            try:
              self.kek_area.set_tile(x,y,self.tile_types[int(terrain_line[(self._active_area[0] + x) * 2])],int(terrain_line[(self._active_area[0] + x) * 2 + 1]),None)
            except Exception:
              pass

          counter += 1
          y += 1

        # TODO LOAD TERRAAAAAAAAAIN

      if end_it:
        break

    kek_file.close()

  ## Private method, initialises the default attribute values

  def __init_attributes(self):
    ## contains the name of the kek file for which the object is a proxy
    self.filename = ""
    ## active kek (player's close) area in format (x,y,width,height) in tiles
    self._active_area = (0, 0, 0, 0)
    ## kekArea object reference
    self.kek_area = None
    ## all kek tile types loaded from the kek file, the key is the tile id, the items are TileType objects
    self.tile_types = {}
    ## all shadows loaded from the kek file, the key is the tile id, the items are name strings
    self.shadows = {}
    ## all prop types (RPG classes) loaded from the kek file, the key is the prop type id, the items are PropType objects
    self.prop_types = {}
    ## all prop instances (RPG instances) loaded from the kek file, the key is the prop instance id, the items are PropInstance objects
    self.prop_instances = {}
    ## kek width in tiles
    self.kek_width = 0
    ## kek height in tiles
    self.kek_height = 0

  ## Initialises a new kek proxy for given kek file.
  #
  #  @param filename name of the kek file for which the object will
  #         be proxy

  def __init__(self, filename):
    self.__init_attributes()
    self.filename = filename
    self.__load_non_terrain()
    self.__load_active_terrain()

  @property
  def width(self):
    return self.kek_width

  @property
  def height(self):
    return self.kek_height

  ## The active area of the kek (the player's close area which
  #  can then be handled in a detailed way). It is a tuple in fomrmat:
  #  (x,y,width,height) where the rectangle must be inside the kek
  #  map.

  @property
  def active_area(self):
    return self._active_area

  @active_area.setter
  def active_area(self,value):
    self._active_area = value
    self.__load_active_terrain()

  def __str__(self):
    result = ""
    result += "kek width: "
    result += str(self.kek_width)
    result += "\nkek height: "
    result += str(self.kek_height)
    result += "\ntiles:\n"

    for tile in self.tile_types:
      result += str(self.tile_types[tile]) + "\n"

    result += "\nprop types:\n"

    for prop in self.prop_types:
      result += str(self.prop_types[prop])

    result += "\n\nprop instances:\n"

    for prop in self.prop_instances:
      result += str(self.prop_instances[prop])

    result += "\nactive area:\n"
    result += str(self.kek_area)

    result += "\nshadows:" + str(self.shadows)

    return result
