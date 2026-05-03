import pygame
import MCTS
from game_logic import *
from ID3 import Node as ID3Node

dataset = []
def reset_game():
    return iniciar_matrix(), 1, None

#TEMOS DE IMPLEMENTAR AS 3 REGRAS Q ESTAO NO GUIA, N TEMOS NENHUMA
#HUMAN VS AI TEM DE TER 2 IAs? PERGUNTAR

pygame.init()

#defenir as dimensões da tela e tamanho das células do tabuleiro

cell_size = 100
top_area = 100
bottom_area = 100

width = COLS * cell_size 
height = ROWS * cell_size + top_area + bottom_area

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("connect 4")

#definir as cores
blue = (0, 0, 255)
black = (0, 0, 0)   
red = (255, 0, 0)
yellow = (255, 255, 0)
green = (0, 255, 0)
WHITE = (255, 255, 255)

background = (12,16,40)
board_color = (35,85,140)
hole_color = (230,235,240)

player1 = (255,130,60)
player2 = (130,190,120)


#desenhar o tabuleiro

def draw_board(board):

    board_x = 0
    board_y = top_area
    board_width = COLS * cell_size
    board_height = ROWS * cell_size

    #desenhar o retângulo do tabuleiro
    pygame.draw.rect(
        screen,
        board_color,
        (board_x, board_y, board_width, board_height),
        border_radius=25
    )
   
    for r in range(ROWS):
        for c in range(COLS):

            #desenhar os círculos para as peças
            x = c * cell_size
            y = r * cell_size + top_area

            center = (x + cell_size//2, y + cell_size//2)

            if board[r][c] == 0:
                pygame.draw.circle(screen, hole_color, center, cell_size//2 - 10)

            elif board[r][c] == 1:
                pygame.draw.circle(screen, player1, center, cell_size//2 - 10)

            elif board[r][c] == 2:
                pygame.draw.circle(screen, player2, center, cell_size//2 - 10)


# ─── FUNÇÃO AUXILIAR: Decision Tree play ───────────────────────────────────────
def dt_play(board, tree):
    """Converte o tabuleiro para o formato da árvore e devolve a jogada"""
    example = {}
    for r in range(6):
        for c in range(7):
            example[f"cell_{r}_{c}"] = str(board[r][c])
    
    label = tree.predict(example)  # ex: "drop_5" ou "pop_3"
    
    if label is None:
        # fallback: jogada aleatória válida
        import random
        from MCTS import get_legal_moves
        moves = get_legal_moves(board, 1)
        return random.choice(moves) if moves else ("drop", 3)
    
    action, col = label.split("_")
    return (action, int(col))


# ─── FUNÇÃO AUXILIAR: carregar a árvore de decisão ─────────────────────────────
def load_dt():
    import csv
    try:
        examples = []
        with open("dataset.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                example = {}
                for r in range(6):
                    for c in range(7):
                        example[f"cell_{r}_{c}"] = row[f"cell_{r}_{c}"]
                example["label"] = f"{row['action']}_{row['col']}"
                examples.append(example)

        attributes = [f"cell_{r}_{c}" for r in range(6) for c in range(7)]
        tree = ID3Node(max_depth=10)
        tree.build_tree(examples, attributes, depth=0)
        print(f"[DT] Árvore treinada com {len(examples)} exemplos.")
        return tree
    except Exception as e:
        print(f"[DT] Erro ao carregar dataset: {e}")
        return None

# Menu para escolher o modo de jogo
def show_menu():
    menu_running = True
    modo_selecionado = None
    
    # Fontes para o menu
    font_title = pygame.font.Font(None, 72)
    font_options = pygame.font.Font(None, 48)
    font_hover = pygame.font.Font(None, 52)
    
    # Cores do menu
    title_color = (255, 255, 255)
    option_color = (200, 200, 200)
    option_hover_color = (255, 130, 60)  # Cor do player1
    border_color = (255, 215, 0)
    
    # Opções do menu
    opcoes = ["HUMAN vs HUMAN", "HUMAN vs AI", "AI vs AI"]
    opcao_hover = -1
    
    clock = pygame.time.Clock()
    
    while menu_running:
        dt = clock.tick(60)
        
        screen.fill(background)
        
        # Criar efeito gradiente de fundo
        for i in range(height):
            gradient_color = (
                background[0] + int(i * (10 - background[0]) / height),
                background[1] + int(i * (20 - background[1]) / height),
                background[2] + int(i * (30 - background[2]) / height)
            )
            pygame.draw.line(screen, gradient_color, (0, i), (width, i))
        
        # Desenhar círculos decorativos
        for i in range(15):
            circle_x = (pygame.time.get_ticks() * 0.03 + i * 80) % (width + 100) - 50
            circle_y = (pygame.time.get_ticks() * 0.02 + i * 70) % (height + 100) - 50
            circle_alpha = 30 + i * 5
            circle_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (*player1, circle_alpha), (50, 50), 40)
            screen.blit(circle_surface, (circle_x, circle_y))
        
        # Desenhar título com sombra
        titulo = font_title.render("CONNECT 4", True, title_color)
        titulo_sombra = font_title.render("CONNECT 4", True, (50, 50, 50))
        titulo_rect = titulo.get_rect(center=(width//2, height//4 - 10))
        titulo_sombra_rect = titulo_sombra.get_rect(center=(width//2 + 4, height//4 - 6))
        screen.blit(titulo_sombra, titulo_sombra_rect)
        screen.blit(titulo, titulo_rect)
        
        # Desenhar linha decorativa abaixo do título
        pygame.draw.line(screen, title_color, (width//2 - 150, height//4 + 40), (width//2 + 150, height//4 + 40), 3)
        pygame.draw.line(screen, title_color, (width//2 - 140, height//4 + 45), (width//2 + 140, height//4 + 45), 2)
        
        # Desenhar opções
        for i, opcao in enumerate(opcoes):
            y_pos = height//2 + i * 80 - 40
            
            # Verificar hover
            mouse_x, mouse_y = pygame.mouse.get_pos()
            text_width = font_options.size(opcao)[0]
            text_height = font_options.size(opcao)[1]
            text_rect = pygame.Rect(width//2 - text_width//2 - 20, y_pos - 20, text_width + 40, text_height + 40)
            
            if text_rect.collidepoint(mouse_x, mouse_y):
                opcao_hover = i
                texto = font_hover.render(opcao, True, option_hover_color)
            else:
                texto = font_options.render(opcao, True, option_color)
            
            texto_rect = texto.get_rect(center=(width//2, y_pos))
            screen.blit(texto, texto_rect)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for i, opcao in enumerate(opcoes):
                    y_pos = height//2 + i * 80 - 40
                    text_width = font_options.size(opcao)[0]
                    text_height = font_options.size(opcao)[1]
                    text_rect = pygame.Rect(width//2 - text_width//2 - 20, y_pos - 20, text_width + 40, text_height + 40)
                    
                    if text_rect.collidepoint(x, y):
                        if i == 0:
                            modo_selecionado = 1  # Human vs Human
                        elif i == 1:
                            modo_selecionado = 2  # Human vs AI
                        elif i == 2:
                            modo_selecionado = 3  # AI vs AI
                        menu_running = False
    
    return modo_selecionado


# ─── NOVO: Menu para escolher a IA de cada jogador ─────────────────────────────
def show_ai_selection_menu(player_num):
    """Menu para escolher a IA de um jogador (1 ou 2)"""
    menu_running = True
    choice = None

    font_title    = pygame.font.Font(None, 56)
    font_subtitle = pygame.font.Font(None, 36)
    font_options  = pygame.font.Font(None, 44)
    font_hover    = pygame.font.Font(None, 48)

    title_color        = (255, 255, 255)
    option_color       = (200, 200, 200)
    option_hover_color = player1 if player_num == 1 else player2

    opcoes = ["MCTS", "Decision Tree"]
    clock  = pygame.time.Clock()

    while menu_running:
        clock.tick(60)
        screen.fill(background)

        # gradiente de fundo (igual ao resto dos menus)
        for i in range(height):
            gradient_color = (
                background[0] + int(i * (10 - background[0]) / height),
                background[1] + int(i * (20 - background[1]) / height),
                background[2] + int(i * (30 - background[2]) / height)
            )
            pygame.draw.line(screen, gradient_color, (0, i), (width, i))

        # Título
        titulo = font_title.render("AI vs AI", True, title_color)
        titulo_rect = titulo.get_rect(center=(width//2, height//4 - 20))
        screen.blit(titulo, titulo_rect)

        # Subtítulo com o número do jogador e cor respetiva
        cor_jogador = player1 if player_num == 1 else player2
        sub_text = f"Choose AI for Player {player_num}:"
        subtitulo = font_subtitle.render(sub_text, True, cor_jogador)
        subtitulo_rect = subtitulo.get_rect(center=(width//2, height//4 + 35))
        screen.blit(subtitulo, subtitulo_rect)

        # Linha decorativa
        pygame.draw.line(screen, title_color,
                         (width//2 - 200, height//4 + 60),
                         (width//2 + 200, height//4 + 60), 2)

        # Opções
        for i, opcao in enumerate(opcoes):
            y_pos = height//2 + i * 90 - 40

            mouse_x, mouse_y = pygame.mouse.get_pos()
            text_width  = font_options.size(opcao)[0]
            text_height = font_options.size(opcao)[1]
            text_rect   = pygame.Rect(width//2 - text_width//2 - 20,
                                      y_pos - 20,
                                      text_width + 40,
                                      text_height + 40)

            if text_rect.collidepoint(mouse_x, mouse_y):
                texto = font_hover.render(opcao, True, option_hover_color)
            else:
                texto = font_options.render(opcao, True, option_color)

            texto_rect = texto.get_rect(center=(width//2, y_pos))
            screen.blit(texto, texto_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for i, opcao in enumerate(opcoes):
                    y_pos       = height//2 + i * 90 - 40
                    text_width  = font_options.size(opcao)[0]
                    text_height = font_options.size(opcao)[1]
                    text_rect   = pygame.Rect(width//2 - text_width//2 - 20,
                                              y_pos - 20,
                                              text_width + 40,
                                              text_height + 40)
                    if text_rect.collidepoint(x, y):
                        choice = "mcts" if i == 0 else "dt"
                        menu_running = False

    return choice  # "mcts" ou "dt"


def show_end_popup(winner):
    """Display end game popup with winner information"""
    overlay = pygame.Surface((width, height))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    popup_width  = 350
    popup_height = 150
    popup_x = (width  - popup_width)  // 2
    popup_y = (height - popup_height) // 2
    
    popup = pygame.Surface((popup_width, popup_height))
    popup.fill((40, 40, 60))
    pygame.draw.rect(popup, (100, 100, 120), popup.get_rect(), 3, border_radius=15)
    
    font_title = pygame.font.Font(None, 36)
    
    if winner == 1:
        winner_text  = "PLAYER 1 WINS!"
        winner_color = player1
    elif winner == 2:
        winner_text  = "PLAYER 2 WINS!"
        winner_color = player2
    elif winner == 3:
        winner_text  = "MCTS WINS!"
        winner_color = (255, 255, 255)
    elif winner == 4:
        winner_text  = "MINIMAX WINS!"
        winner_color = (255, 255, 255)
    else:
        winner_text  = "IT'S A TIE!"
        winner_color = (255, 255, 255)
    
    text      = font_title.render(winner_text, True, winner_color)
    text_rect = text.get_rect(center=(popup_width//2, popup_height//2))
    popup.blit(text, text_rect)
    
    screen.blit(popup, (popup_x, popup_y))
    pygame.display.update()
    pygame.time.wait(2000)


# ─── SETUP ─────────────────────────────────────────────────────────────────────
modo_jogo = show_menu()

# Configuração AI vs AI
ai_p1 = None  # "mcts" ou "dt"
ai_p2 = None
dt_tree = None  # árvore partilhada (carregada uma vez se necessário)

if modo_jogo == 3:
    ai_p1 = show_ai_selection_menu(1)
    ai_p2 = show_ai_selection_menu(2)
    # Carregar a árvore se algum jogador for DT
    if ai_p1 == "dt" or ai_p2 == "dt":
        dt_tree = load_dt()
    matrix = iniciar_matrix()

running        = True
current_player = 1
mcts_root      = None

# Teste de melhoria
reuse_ok   = 0
reuse_fail = 0

# Cenas para dataset
turn  = 0
jogos = 0
MAX   = 2


# ─── LOOP PRINCIPAL ────────────────────────────────────────────────────────────
while running:

    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not (modo_jogo == 2 and current_player == 2) and not (modo_jogo == 3):
            
            x = event.pos[0]
            y = event.pos[1]

            col = x // cell_size
            jogada_feita = False
            if y < top_area:
                if not col_isFull(matrix, col):
                    drop(matrix, current_player, col)
                    jogada_feita = True

            elif y > height - bottom_area:
                if check_pop(matrix, current_player, col):
                    pop(matrix, current_player, col)
                    jogada_feita = True

            if jogada_feita:
                if y < top_area:
                    novo_root = MCTS.atualizar_root(mcts_root, ("drop", col))
                else:
                    novo_root = MCTS.atualizar_root(mcts_root, ("pop", col))

                if novo_root is None:
                    reuse_fail += 1
                else:
                    reuse_ok += 1
                mcts_root = novo_root

                screen.fill(black)
                draw_board(matrix)
                pygame.display.update()

                venceu_atual    = check_victory(matrix, current_player)
                venceu_oponente = check_victory(matrix, 3 - current_player)
                
                if venceu_atual and venceu_oponente:
                    show_end_popup(current_player)
                    running = False
                elif venceu_atual:
                    show_end_popup(current_player)
                    running = False
                elif venceu_oponente:
                    show_end_popup(3 - current_player)
                    running = False
                else:
                    current_player = 3 - current_player
        
    # ── AI moves ──
    if running:

        # ── Modo 2: Human vs AI ──
        if modo_jogo == 2 and current_player == 2:
            movimento, mcts_root = MCTS.algoritmo_mcts(matrix, current_player, 5000, mcts_root)
            if movimento[0] == "drop":
                drop(matrix, current_player, movimento[1])
            else:
                pop(matrix, current_player, movimento[1])

            novo_root = MCTS.atualizar_root(mcts_root, movimento)
            if novo_root is None:
                reuse_fail += 1
            else:
                reuse_ok += 1

            screen.fill(black)
            draw_board(matrix)
            pygame.display.update()

            venceu_atual    = check_victory(matrix, current_player)
            venceu_oponente = check_victory(matrix, 3 - current_player)
                
            if venceu_atual and venceu_oponente:
                show_end_popup(current_player)
                running = False
            elif venceu_atual:
                show_end_popup(current_player)
                running = False
            elif venceu_oponente:
                show_end_popup(3 - current_player)
                running = False
            else:
                current_player = 3 - current_player

        # ── Modo 3: AI vs AI ──
        elif modo_jogo == 3:

            pygame.time.wait(1000)  # pequena pausa para visualização
            screen.fill(black)
            draw_board(matrix)
            pygame.display.update()

            # Escolher a IA do jogador atual
            ai_atual = ai_p1 if current_player == 1 else ai_p2
            print(f"Jogador atual: {current_player} | IA: {ai_atual}")
            if ai_atual == "mcts":
                movimento, _ = MCTS.algoritmo_mcts(matrix, current_player, 5000)
            else:
                # Decision Tree
                movimento = dt_play(matrix, dt_tree)
                # Validar jogada (pode ser inválida se a árvore sugerir coluna cheia)
                from MCTS import get_legal_moves
                if movimento not in get_legal_moves(matrix, current_player):
                    movimento, _ = MCTS.algoritmo_mcts(matrix, current_player, 5000)

            # Guardar para dataset
            if turn > 3:
                estado = [row[:] for row in matrix]
                dataset.append((estado, movimento))

            # Aplicar jogada
            if movimento[0] == "drop":
                drop(matrix, current_player, movimento[1])
            else:
                pop(matrix, current_player, movimento[1])
            turn += 1

            screen.fill(black)
            draw_board(matrix)
            pygame.display.update()

            venceu_atual    = check_victory(matrix, current_player)
            venceu_oponente = check_victory(matrix, 3 - current_player)
                
            if venceu_atual and venceu_oponente:
                show_end_popup(current_player)
                matrix, current_player, mcts_root = reset_game()
                turn = 0
            elif venceu_atual:
                show_end_popup(current_player)
                matrix, current_player, mcts_root = reset_game()
                turn = 0
            elif venceu_oponente:
                show_end_popup(3 - current_player)
                matrix, current_player, mcts_root = reset_game()
                turn = 0
            else:
                current_player = 3 - current_player

        if jogos > MAX:
            running = False

    # Only draw if game is still running
    if running:
        screen.fill(black)
        draw_board(matrix)

        if modo_jogo != 3:
            mouse_x = pygame.mouse.get_pos()[0]
            mouse_y = pygame.mouse.get_pos()[1]
            col = mouse_x // cell_size
            highlight = pygame.Surface((cell_size, ROWS * cell_size), pygame.SRCALPHA)
            highlight.fill((255, 255, 255, 40))
            screen.blit(highlight, (col * cell_size, top_area))

            if mouse_y < top_area and not (modo_jogo == 2 and current_player == 2) and not (modo_jogo == 3):
                color = player1 if current_player == 1 else player2
                pygame.draw.circle(screen, color, (mouse_x, top_area//2), cell_size//2 - 10)

        pygame.display.update()


pygame.quit()

print("\n--- STATS ---")
print("Reuse OK:", reuse_ok)
print("Reuse FAIL:", reuse_fail)

with open("dataset.txt", "a") as f:
    for estado, mov in dataset:
        f.write(f"{estado}; {mov}\n")