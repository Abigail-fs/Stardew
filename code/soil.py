import random

import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil']

class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil water']


class SoilLayer:
    def __init__(self, all_sprites):

        # sprite groups
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()

        # graphics
        self.soil_surf = pygame.image.load('../graphics/soil/o.png')
        self.soil_surfs = import_folder_dict('../graphics/soil')

        self.create_soil_grid()
        self.create_hit_rect()

    def create_soil_grid(self):
        ground = pygame.image.load('../graphics/world/ground.png')
        h_tiles = ground.get_width() // TILE_SIZE
        v_tiles = ground.get_height() // TILE_SIZE

        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')
        for row in self.grid:
            print(row)

    def create_hit_rect(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()

    def water(self, target_pos):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):

                # add an entry to the soil grid
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                self.grid[y][x].append('W')
                pos = soil_sprite.rect.topleft

                water_surface_list = import_folder('../graphics/soil_water')
                WaterTile(pos, random.choice(water_surface_list), (self.all_sprites, self.water_sprites))

    def remove_water(self):
        # destroy all water
        for sprite in self.water_sprites.sprites():
            sprite.kill()
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')


    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell, in enumerate(row):
                if 'X' in cell:

                    # tile options
                    t = 'X' in self.grid[index_row - 1][index_col]
                    r = 'X' in self.grid[index_row][index_col + 1]
                    l = 'X' in self.grid[index_row][index_col - 1]
                    b = 'X' in self.grid[index_row + 1][index_col]

                    tile_type = 'o'

                    # all sides
                    if all((t, r, l, b)):
                        tile_type = 'x'

                    # horizontal only
                    if l and not any((r, t, b)):
                        tile_type = 'r'
                    if r and not any((l, t, b)):
                        tile_type = 'l'
                    if r and l and not any((t, b)):
                        tile_type = 'lr'

                    # vertical only
                    if t and not any((l, b, r)):
                        tile_type = 'b'
                    if b and not any((t, l, r)):
                        tile_type = 't'
                    if b and t and not any((l, r)):
                        tile_type = 'tb'

                    # corners
                    if l and b and not any((t, r)):
                        tile_type = 'tr'
                    if r and b and not any((t, l)):
                        tile_type = 'tl'
                    if l and t and not any((b, r)):
                        tile_type = 'br'
                    if r and t and not any((b, l)):
                        tile_type = 'bl'

                    # T shapes
                    if all((t, b, r)) and not l:
                        tile_type = 'tbr'
                    if all((t, b, l)) and not r:
                        tile_type = 'tbl'
                    if all((l, r, t)) and not b:
                        tile_type = 'lrb'
                    if all((b, l, r)) and not t:
                        tile_type = 'lrt'






                    SoilTile((index_col * TILE_SIZE, index_row * TILE_SIZE),
                             self.soil_surfs[tile_type],
                             (self.all_sprites, self.soil_sprites))
