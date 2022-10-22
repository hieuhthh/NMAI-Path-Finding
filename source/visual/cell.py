import enum
import pygame

# SETTINGS
class CellType(enum.Enum):
    blank = 0
    start = 1
    wall = 2
    bonus = 3
    mustgo = 4
    tele = 5

    def get_color(type):
        switcher = {
            CellType.blank: pygame.Color('white'),
            CellType.start: pygame.Color('blue'),
            CellType.wall: pygame.Color('darkgray'),
            CellType.bonus: pygame.Color('gold'),
            CellType.mustgo: pygame.Color('red'),
            CellType.tele: pygame.Color('forestgreen')
        }

        return switcher.get(type,"Invalid cell type")

    def get_cell_type(sign):
        switcher = {
            ' ': CellType.blank,
            'x': CellType.wall,
            'S': CellType.start, 
            '+': CellType.bonus,
            '=': CellType.mustgo,
            '_': CellType.tele,
        }

        return switcher.get(sign, "Invalid sign")

class Cell:
    def __init__(self, x, y, sign, tile_size, tile_padding):
        self.x, self.y = x, y
        self.tile_size = tile_size
        self.tile_padding = tile_padding
        self.tile_actual_size = tile_size - 2 * tile_padding
        self.type = CellType.get_cell_type(sign)
        self.cell = pygame.Rect((x * self.tile_size + self.tile_padding, y * self.tile_size + self.tile_padding), 
                            (self.tile_actual_size, self.tile_actual_size))
        self.color = CellType.get_color(self.type)
        
        self.inPath = False
        self.inSearch = False
        self.set_in_path(False)

    def check_in_path(self):
        if (self.type == CellType.blank or self.type == CellType.bonus or self.type == CellType.tele):
            return self.inPath
        return False

    def check_in_search(self):
        if (self.type == CellType.blank):
            return self.inSearch
        return False

    def set_in_path(self, inPath):
        if (self.type == CellType.blank or self.type == CellType.bonus or self.type == CellType.tele):
            self.inPath = inPath

            if self.inPath:
                self.inSearch = False
        else:
            self.inPath = False

    def set_in_search(self, inSearch):
        if (self.type == CellType.blank or self.type == CellType.bonus or self.type == CellType.tele):
            self.inSearch = inSearch
        else:
            self.inSearch = False

    def draw(self, screen):
        if (self.check_in_path()):
            color = pygame.Color('darkorange')
        elif (self.check_in_search()):
            color = pygame.Color('bisque')
        else:
            color = self.color
    
        pygame.draw.rect(screen, color, self.cell, border_radius = self.tile_size // 6)

    def draw_border(self, screen):
        border_x, border_y = self.x * self.tile_size, self.y * self.tile_size
        border = pygame.Rect((border_x, border_y), (self.tile_size, self.tile_size))
        border_color = pygame.Color('black')

        pygame.draw.rect(screen, border_color, border)
