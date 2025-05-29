import pygame
import os
import sys
from config import SCREEN_WIDTH  # Importa a constante

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, x, y, size):
        super().__init__()
        self.tile_type = tile_type

        # Tamanhos customizados
        self.custom_sizes = {
            1: (SCREEN_WIDTH, size),  # Grama ocupa toda largura
            2: (500, 300),           # Plataforma
            3: (size, size),         # Subida diagonal
            4: (500, 150)            # Descida diagonal
        }

        try:
            if tile_type == 1:  # Grama única
                img = pygame.image.load(get_resource_path('assets/tiles/grass1.png')).convert_alpha()
                self.image = pygame.Surface(self.custom_sizes[1], pygame.SRCALPHA)
                
                # Calcula quantas repetições precisamos
                texture_width = img.get_width()
                reps = int(SCREEN_WIDTH / texture_width) + 1
                
                # Preenche sem sobreposição
                for i in range(reps):
                    self.image.blit(img, (i * texture_width, 0))
                    
            elif tile_type == 2:  # Plataforma
                img = pygame.image.load(get_resource_path('assets/tiles/plataforma.png')).convert_alpha()
                self.image = pygame.transform.scale(img, self.custom_sizes[2])
                
            elif tile_type in [3, 4]:  # Diagonais
                img = pygame.image.load(get_resource_path('assets/tiles/grassDiagonalDireita.png')).convert_alpha()
                if tile_type == 4:
                    img = pygame.transform.flip(img, True, False)
                self.image = pygame.transform.scale(img, self.custom_sizes[tile_type])
                
        except Exception as e:
            print(f"Erro ao carregar tile {tile_type}: {e}")
            width, height = self.custom_sizes.get(tile_type, (size, size))
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            colors = {
                1: (0, 255, 0),    # Grama
                2: (160, 82, 45),  # Plataforma
                3: (0, 200, 0),    # Subida
                4: (0, 150, 0)     # Descida
            }
            self.image.fill(colors.get(tile_type, (255, 0, 255)))
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
