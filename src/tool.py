## \file general.py
#  this file contains functions and classes for helper tools for the
#  game

import pygame

## Makes an map string from given bitmap image.
#
#  @param image_surface image (Surface) from which to make the map
#  @param color_map say how to interpret the colors in the image, this
#         should be a list of tuples in format: (color,tile_id,
#         tile_variant)
#  @param one_line if True, the string will be a single line in format
#         "width height data..." (interiors are encoded this way),
#         otherwise newspaces will be used and the string will be in
#         format "width \n height \n line1 \n line2 ..." (exterior
#         terrain is encoded this way)
#  @return map string

def image_to_map_string(image_surface, color_map, one_line = False):
  result = ""
  result += str(image_surface.get_width()) + " "

  if not one_line:
    result += "\n"

  result += str(image_surface.get_height()) + " "

  if not one_line:
    result += "\n"

  for j in range(image_surface.get_height()):
    for i in range(image_surface.get_width()):
      current_color = image_surface.get_at((i,j))

      found = False

      for item in color_map:
        if item[0] == current_color:
          found = True
          result += str(item[1]) + " " + str(item[2]) + " "
          break

      if not found:
        result += "N 0 "

    if not one_line:
      result += "\n"


  return result

img = pygame.image.load("resources/tile_city.png")
c_map = [
          (pygame.Color(0,255,0),0,0),
          (pygame.Color(0,128,0),0,1),
          (pygame.Color(0,64,0),0,2),
          (pygame.Color(0,32,0),0,3),
          (pygame.Color(255,0,0),2,0),
          (pygame.Color(128,0,0),2,1),
          (pygame.Color(64,0,0),2,2),
          (pygame.Color(32,0,0),2,3),
          (pygame.Color(255,255,255),3,0),
          (pygame.Color(128,128,128),3,1),
          (pygame.Color(64,64,64),3,2),
          (pygame.Color(32,32,32),3,3),
          (pygame.Color(0,255,255),4,0),
          (pygame.Color(0,128,128),4,1),
          (pygame.Color(0,64,64),4,2),
          (pygame.Color(0,32,32),4,3),
          (pygame.Color(0,0,255),1,0),
          (pygame.Color(128,64,0),2,0)
        ]

print(image_to_map_string(img,c_map))
