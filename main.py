import pygame
import os
from config import *
from tile import Tile
import sys

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    # Inicialização
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Milin Adventures")

    # Carregar música de fundo com caminho compatível com .exe
    pygame.mixer.music.load(get_resource_path('assets/sounds/low.WAV'))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # loop da música do jogo
    
    # Constantes do jogo
    TILE_SIZE = 88
    scale_factor = 0.3
    JUMP_STRENGTH = -15
    GRAVITY = 0.8
    FPS = 60

    # Variáveis de controle do nível
    global current_scroll_x, current_level_part
    current_scroll_x = 0
    current_level_part = 1
    max_level_parts = 3

    # Fonte
    font = pygame.font.SysFont('arial', 24)

    # Grupos de sprites
    all_tiles = pygame.sprite.Group()  # TODOS os tiles do jogo
    visible_tiles = pygame.sprite.Group()  # Apenas tiles visíveis na área atual
    player_group = pygame.sprite.Group()
    all_items = pygame.sprite.Group()  # Grupo para os itens pegáveis

    # Funções auxiliares para carregar imagens
    def load_image(path):
        try:
            full_path = get_resource_path(path)
            return pygame.image.load(full_path).convert_alpha()
        except pygame.error as e:
            print(f"Erro ao carregar imagem: {full_path}")
            print(e)
            return pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)

    def slice_sprite_sheet(sheet, frame_width, frame_height):
        frames = []
        sheet_width, sheet_height = sheet.get_size()
        for i in range(sheet_width // frame_width):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            frames.append(frame)
        return frames

    def scale_frames(frames, scale_factor):
        return [pygame.transform.scale(frame,
                (int(frame.get_width() * scale_factor),
                 int(frame.get_height() * scale_factor)))
                for frame in frames]

    # Carregar sprites do jogador
    try:
        IDLE_FRAMES = scale_frames(
            slice_sprite_sheet(load_image(os.path.join("assets", "player", "milinIdle.png")), 240, 210),
            scale_factor)
        WALK_FRAMES = scale_frames(
            slice_sprite_sheet(load_image(os.path.join("assets", "player", "milinWalk.png")), 240, 210),
            scale_factor)
        JUMP_FRAMES = scale_frames(
            slice_sprite_sheet(load_image(os.path.join("assets", "player", "milinJump.png")), 255, 210),
            scale_factor)
        EAT_FRAMES = scale_frames(
            slice_sprite_sheet(load_image(os.path.join("assets", "player", "milinEato.png")), 188, 230),
            # slice_sprite_sheet(load_image(os.path.join("assets", "player", "milinHeart.png")), 200, 209),

            scale_factor)
    except Exception as e:
        print("Erro ao carregar sprites:")
        print(e)
        IDLE_FRAMES = [pygame.Surface((50, 50), pygame.SRCALPHA) for _ in range(4)]
        WALK_FRAMES = IDLE_FRAMES.copy()
        JUMP_FRAMES = IDLE_FRAMES.copy()
        EAT_FRAMES = IDLE_FRAMES.copy()

    # Classe do Item pegável (ex: moeda) com controle de tamanho
    class Item(pygame.sprite.Sprite):
        def __init__(self, x, y, size=40):
            super().__init__()
            image = load_image(os.path.join("assets", "items", "blusa.png"))  # imagem da moeda
            self.image = pygame.transform.scale(image, (size, size))
            self.rect = self.image.get_rect(topleft=(x, y))
            self.area = (x // SCREEN_WIDTH) + 1  # Identifica a área do item (1, 2 ou 3)

        def update(self):
            pass  # animação, se quiser


    # Classe do Balão de Fala
    class SpeechBubble:
        def __init__(self, text, duration=3000):
            self.text = text
            self.font = pygame.font.SysFont('arial', 20)
            self.duration = duration
            self.start_time = pygame.time.get_ticks()
            self.active = True
        
        def update(self):
            if pygame.time.get_ticks() - self.start_time > self.duration:
                self.active = False
        
        def draw(self, screen, player_rect):
            if not self.active:
                return
                
            # Ajusta posição considerando scroll da tela (camera)
            x = player_rect.centerx - current_scroll_x
            y = player_rect.top
            
            # Renderiza o texto
            text_surface = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect()
            
            # Cria o balão (retângulo com borda)
            bubble_width = text_rect.width + 20
            bubble_height = text_rect.height + 15
            bubble_rect = pygame.Rect(0, 0, bubble_width, bubble_height)
            bubble_rect.centerx = x
            bubble_rect.bottom = y - 10
            
            # Desenha o balão
            pygame.draw.rect(screen, (255, 255, 224), bubble_rect, border_radius=10)  # tom ligeiramente amarelado
            pygame.draw.rect(screen, (0, 0, 0), bubble_rect, 2, border_radius=10)
            
            # Desenha o texto no balão
            screen.blit(text_surface, (bubble_rect.x + 10, bubble_rect.y + 8))

    # Configuração dos mapas
    num_cols = SCREEN_WIDTH // TILE_SIZE
    num_rows = SCREEN_HEIGHT // TILE_SIZE

    # Definindo os mapas para cada área (todos com chão completo na última linha)
    level_maps = {
        1: [
            [0]*num_cols, [0]*num_cols, [0]*num_cols, [0]*num_cols, [0]*num_cols,
            [0]*num_cols, [0]*num_cols, [0]*num_cols, [0]*num_cols,
            [0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0] + [0]*(num_cols-21),
            [1]*num_cols  # Chão completo
        ],
        2: [
            [0]*num_cols, [0]*num_cols, [0]*num_cols, [0]*num_cols, [0]*num_cols,
            [0]*num_cols, [0]*num_cols, [0]*num_cols, [0]*num_cols,
            # [0]*num_cols, [0]*num_cols, [0]*num_cols, [0]*num_cols,
            [0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,2,0,0,0,0,0] + [0]*(num_cols-21),
            [1]*num_cols  # Chão completo
        ],
        3: [
            [0]*num_cols, [0]*num_cols, [0]*num_cols, [0]*num_cols, [0]*num_cols,
            [0]*num_cols, [0]*num_cols, [0]*num_cols, [0]*num_cols, [0]*num_cols,
            [1]*num_cols  # Chão completo
        ]
    }

    # Função para carregar TODOS os tiles do jogo de uma vez
    def load_all_tiles():
        for part_number, map_data in level_maps.items():
            for row_index, row in enumerate(map_data):
                for col_index, tile_type in enumerate(row):
                    x = col_index * TILE_SIZE + (part_number-1) * SCREEN_WIDTH
                    y = row_index * TILE_SIZE

                    if tile_type == 1:  # Chão
                        all_tiles.add(Tile(1, x, y, TILE_SIZE))
                    elif tile_type == 2:  # Plataforma
                        all_tiles.add(Tile(2, x, y, TILE_SIZE * 3))
                    elif tile_type == 3:  # Subida
                        all_tiles.add(Tile(3, x, y, TILE_SIZE))
                    elif tile_type == 4:  # Descida
                        all_tiles.add(Tile(4, x, y, TILE_SIZE))

    # Carregar os itens pegáveis por área, 2 por área
    def load_items():
        # Área 1 (offset horizontal 0)
        all_items.add(Item(800, SCREEN_HEIGHT - TILE_SIZE * 2, size=50))  # moeda 1 área 1
        all_items.add(Item(1200, SCREEN_HEIGHT - TILE_SIZE * 3, size=50))  # moeda 2 área 1

        # Área 2 (offset horizontal SCREEN_WIDTH)
        offset_area_2 = SCREEN_WIDTH
        all_items.add(Item(1200 + offset_area_2, SCREEN_HEIGHT - TILE_SIZE * 3, size=50))  # moeda 1 área 2
        all_items.add(Item(350 + offset_area_2, SCREEN_HEIGHT - TILE_SIZE * 2, size=50))  # moeda 2 área 2

        # Área 3 (offset horizontal SCREEN_WIDTH * 2)
        offset_area_3 = SCREEN_WIDTH * 2
        all_items.add(Item(350 + offset_area_3, SCREEN_HEIGHT - TILE_SIZE * 2, size=50))  # moeda 1 área 3
        all_items.add(Item(800 + offset_area_3, SCREEN_HEIGHT - TILE_SIZE * 1, size=50))  # moeda 2 área 3

    # Atualiza quais tiles estão visíveis na área atual
    def update_visible_tiles():
        visible_tiles.empty()
        left_bound = current_scroll_x
        right_bound = current_scroll_x + SCREEN_WIDTH

        for tile in all_tiles:
            if left_bound <= tile.rect.x < right_bound:
                visible_tiles.add(tile)

    # Classe para nuvem
    class Cloud:
        def __init__(self, x, y, speed, image):
            self.x = x
            self.y = y
            self.speed = speed
            self.image = image
            self.width = image.get_width()

        def update(self):
            self.x += self.speed
            if self.x > SCREEN_WIDTH:
                self.x = -self.width

        def draw(self, screen):
            screen.blit(self.image, (self.x, self.y))

    # Classe para árvore (fixa)
    class Tree:
        def __init__(self, x, y, image):
            self.x = x
            self.y = y
            self.image = image

        def draw(self, screen, scroll_x):
            screen.blit(self.image, (self.x - scroll_x, self.y))

    # Classe do Jogador
    class Player(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.walk_frames = WALK_FRAMES
            self.idle_frames = IDLE_FRAMES
            self.jump_frames = JUMP_FRAMES
            self.eat_frames = EAT_FRAMES
            self.image = self.idle_frames[0]
            self.rect = self.image.get_rect(topleft=(x, y))
            self.vel_y = 0
            self.on_ground = False
            self.frame_index = 0
            self.anim_speed = 150
            self.last_update = pygame.time.get_ticks()
            self.is_moving = False
            self.is_jumping = False
            self.facing_right = True
            self.idle_time = 0
            self.is_eating = False
            self.last_move_time = pygame.time.get_ticks()
            self.score = 0  # Pontuação do jogador, moedas coletadas
            self.items_area3 = 0  # Contador de itens da área 3 coletados

        def update(self):
            global current_scroll_x, current_level_part

            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            current_time = pygame.time.get_ticks()

            # Movimento
            if keys[pygame.K_LEFT]:
                dx = -5
                self.is_moving = True
                self.facing_right = False
            elif keys[pygame.K_RIGHT]:
                dx = 5
                self.is_moving = True
                self.facing_right = True
            else:
                self.is_moving = False

            # Verifica transição entre áreas
            screen_right = current_scroll_x + SCREEN_WIDTH
            screen_left = current_scroll_x

            if self.rect.right > screen_right and dx > 0 and current_level_part < max_level_parts:
                current_level_part += 1
                current_scroll_x += SCREEN_WIDTH
                self.rect.left = current_scroll_x + 100  # Posiciona 100px à direita do início
                update_visible_tiles()

            elif self.rect.left < screen_left and dx < 0 and current_level_part > 1:
                current_level_part -= 1
                current_scroll_x -= SCREEN_WIDTH
                self.rect.right = current_scroll_x + SCREEN_WIDTH - 100  # Posiciona 100px da borda esquerda
                update_visible_tiles()

            # Pulo e física
            if keys[pygame.K_SPACE] and self.on_ground:
                self.vel_y = JUMP_STRENGTH
                self.on_ground = False
                self.is_jumping = True

            self.vel_y += GRAVITY
            dy += self.vel_y

            # Atualiza posição e verifica colisões
            self.rect.x += dx
            self.handle_horizontal_collision(dx)

            self.rect.y += dy
            self.on_ground = False
            self.handle_vertical_collision(dy)

            # Verifica colisões com itens
            collected_items = pygame.sprite.spritecollide(self, all_items, True)  # Remove o item ao coletá-lo
            for item in collected_items:
                self.score += 1  # Incrementa pontuação
                if item.area == 3:
                    self.items_area3 += 1
                print(f"Item coletado! Pontuação: {self.score}")

            # Animação de comer após 5 segundos parado
            if not any([keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_SPACE]]):
                self.idle_time = current_time - self.last_move_time
                if self.idle_time >= 5000 and self.on_ground:
                    self.is_eating = True
            else:
                self.last_move_time = current_time
                self.is_eating = False

            self.animate()

        def handle_horizontal_collision(self, dx):
            for tile in visible_tiles:
                if self.rect.colliderect(tile.rect):
                    if dx > 0:  # Colisão à direita
                        self.rect.right = tile.rect.left
                    elif dx < 0:  # Colisão à esquerda
                        self.rect.left = tile.rect.right

        def handle_vertical_collision(self, dy):
            for tile in visible_tiles:
                if self.rect.colliderect(tile.rect):
                    if dy > 0:  # Colisão abaixo (chão)
                        self.rect.bottom = tile.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                        self.is_jumping = False
                    elif dy < 0:  # Colisão acima (teto)
                        self.rect.top = tile.rect.bottom
                        self.vel_y = 0

        def animate(self):
            now = pygame.time.get_ticks()

            # Seleciona animação
            if self.is_eating:
                frames = self.eat_frames
                anim_speed = 200
            elif self.is_jumping:
                frames = self.jump_frames
                anim_speed = 150
            elif self.is_moving:
                frames = self.walk_frames
                anim_speed = 100
            else:
                frames = self.idle_frames
                anim_speed = 300

            if now - self.last_update > anim_speed:
                self.last_update = now
                self.frame_index = (self.frame_index + 1) % len(frames)

                frame = frames[self.frame_index]
                if not self.facing_right:
                    frame = pygame.transform.flip(frame, True, False)

                old_pos = self.rect.midbottom
                self.image = frame
                self.rect = self.image.get_rect(midbottom=old_pos)

    # Classe da Caixa de Diálogo
    class DialogBox:
        def __init__(self, messages, width=600, height=150, typing_speed=50):
            self.messages = messages
            self.current_index = 0
            self.width = width
            self.height = height
            self.surface = pygame.Surface((self.width, self.height))
            self.surface.set_alpha(220)
            self.surface.fill((30, 30, 30))
            self.rect = self.surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT-self.height//2-20))
            self.font = pygame.font.SysFont('arial', 24)
            self.typing_speed = typing_speed
            self.last_update = pygame.time.get_ticks()
            self.current_text = ""
            self.char_index = 0
            self.finished_typing = False

        def update(self):
            if not self.finished_typing and self.current_index < len(self.messages):
                now = pygame.time.get_ticks()
                if now - self.last_update > self.typing_speed:
                    msg = self.messages[self.current_index]
                    if self.char_index < len(msg):
                        self.current_text += msg[self.char_index]
                        self.char_index += 1
                        self.last_update = now
                    else:
                        self.finished_typing = True

        def draw(self, screen):
            screen.blit(self.surface, self.rect)
            wrapped_text = []
            words = self.current_text.split(' ')
            line = ""

            for word in words:
                test_line = f"{line} {word}".strip()
                if self.font.size(test_line)[0] <= self.width - 40:
                    line = test_line
                else:
                    wrapped_text.append(line)
                    line = word
            if line:
                wrapped_text.append(line)

            for i, line in enumerate(wrapped_text):
                text_surface = self.font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (self.rect.x+20, self.rect.y+20+i*30))

        def next_message(self):
            if not self.finished_typing:
                self.current_text = self.messages[self.current_index]
                self.finished_typing = True
                self.char_index = len(self.current_text)
                return True

            if self.current_index < len(self.messages)-1:
                self.current_index += 1
                self.current_text = ""
                self.char_index = 0
                self.finished_typing = False
                return True
            return False

    # Inicialização do jogo
    messages = [
        "Bem-vinda ao Milin Adventures!",
        "Eu sou o milin, o devorador de blusas, me ajude a pegar todas ou devoro você ☺!",
        "Use as setas para mover e ESPAÇO para pular.",
        "Divirta-se!",
        "PS: o criador não teve muito tempo para fazer isso então só saiu isso!"
    ]

    dialog = DialogBox(messages)
    dialog_active = True

    # Carrega todos os tiles e inicia o jogador
    load_all_tiles()
    load_items()  # Carrega os itens pegáveis

    player = Player(100, SCREEN_HEIGHT - TILE_SIZE * 3)
    player_group.add(player)
    update_visible_tiles()  # Garante que apenas os tiles da área 1 são visíveis

    # Variáveis para controle do balão de fala
    speech_bubble = None
    total_items_area3 = 2  # Total de itens na área 3

    try:
        cloud_img = load_image(os.path.join("assets", "background", "cloud.png"))
    except:
        cloud_img = pygame.Surface((120, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(cloud_img, (255, 255, 255), cloud_img.get_rect())

    try:
        tree_img = load_image(os.path.join("assets", "background", "tree.png"))
    except:
        tree_img = pygame.Surface((60, 100), pygame.SRCALPHA)
        pygame.draw.rect(tree_img, (34, 139, 34), pygame.Rect(10, 40, 40, 60))
        pygame.draw.polygon(tree_img, (0, 100, 0), [(30,0), (0, 50), (60, 50)])

    # Criar objetos nuvem
    clouds = [
        Cloud(100, 80, 0.3, cloud_img),
        Cloud(400, 50, 0.2, cloud_img),
        Cloud(700, 70, 0.4, cloud_img)
    ]

    # Criar objetos árvore (posições fixas)
    trees = [
        Tree(150, SCREEN_HEIGHT - TILE_SIZE - 100, tree_img),
        Tree(550 + SCREEN_WIDTH, SCREEN_HEIGHT - TILE_SIZE - 100, tree_img),
        Tree(1000 + 2*SCREEN_WIDTH, SCREEN_HEIGHT - TILE_SIZE - 100, tree_img)
    ]

    # Loop principal
    running = True
    while running:
        dt = clock.tick(FPS)
        screen.fill((135, 206, 235))  # Céu azul

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and dialog_active:
                    if not dialog.next_message():
                        dialog_active = False

        # Atualiza nuvens, que se movem na tela independente do scroll do chão
        for cloud in clouds:
            cloud.update()
            cloud.draw(screen)

        # Desenha as árvores atrás dos tiles, considerando scroll da tela
        for tree in trees:
            tree.draw(screen, current_scroll_x)

        # Verifica se todos os itens da área 3 foram coletados
        if (current_level_part == 3 and 
            player.items_area3 >= total_items_area3 and
            speech_bubble is None):
            
            speech_bubble = SpeechBubble("Muito obrigado! Voce me ajudou a comer, digo coletar todas as blusas, me sinto muito satisfeito.", 10000)  # duração maior
            
        # Atualiza e desenha
        player_group.update()
        all_items.update()

        # Desenha apenas os tiles visíveis
        for tile in visible_tiles:
            screen.blit(tile.image, (tile.rect.x - current_scroll_x, tile.rect.y))

        # Desenha os itens
        for item in all_items:
            screen.blit(item.image, (item.rect.x - current_scroll_x, item.rect.y))

        # Desenha o jogador
        for p in player_group:
            screen.blit(p.image, (p.rect.x - current_scroll_x, p.rect.y))

        # Atualiza e desenha o balão de fala se existir
        if speech_bubble:
            speech_bubble.update()
            if speech_bubble.active:
                speech_bubble.draw(screen, player.rect)
            else:
                speech_bubble = None

        if dialog_active:
            dialog.update()
            dialog.draw(screen)

        # Mostra a área atual e a pontuação
        level_text = font.render(f"{current_level_part}/{max_level_parts}", True, (0, 0, 0))
        score_text = font.render(f"Blusas: {player.score}", True, (255, 215, 0))
        screen.blit(level_text, (10, 10))
        screen.blit(score_text, (10, 40))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()