import pygame
import sys
import main  # importa seu arquivo principal do jogo
import os

def get_resource_path(relative_path):
    try:
        # Usado pelo PyInstaller para extrair arquivos embutidos
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Inicialização do Pygame
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1800, 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Milin Adventures - Menu")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Helvetica', 48)
menu_font = pygame.font.SysFont('Helvetica', 36, bold=True)

# Carregando imagem de fundo
background_img = pygame.image.load(get_resource_path('assets/images/background_menu.png')).convert()
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Carregando e tocando música de fundo
pygame.mixer.music.load(get_resource_path('assets/sounds/zoom.mp3'))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # <-- Isso aqui garante o loop!

# Cores
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
YELLOW = (255, 215, 0)

# Opções do menu
menu_options = ["START", "OPÇÕES", "SAIR"]
selected_option = 0

def draw_menu():
    screen.blit(background_img, (0, 0))  # Desenha a imagem de fundo

    title_surface = font.render("", True, YELLOW)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
    screen.blit(title_surface, title_rect)

    for index, option in enumerate(menu_options):
        color = YELLOW if index == selected_option else WHITE
        option_surface = menu_font.render(option, True, color)
        option_rect = option_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + index * 60))
        screen.blit(option_surface, option_rect)

def main_menu():
    global selected_option
    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:

                    if menu_options[selected_option] == "START":
                        # Para a música do menu
                        pygame.mixer.music.stop()
                        running = False
                        main.main()

                    elif menu_options[selected_option] == "OPÇÕES":
                        options_menu()
                    elif menu_options[selected_option] == "SAIR":
                        pygame.quit()
                        sys.exit()

        draw_menu()
        pygame.display.flip()

def options_menu():
    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((30, 30, 60))
        text_surface = menu_font.render("Nada aqui ainda minha cria - ESC para voltar", True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
