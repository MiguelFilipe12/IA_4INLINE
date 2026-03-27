import pygame
import MCTS
from game_logic import *
import time

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
                # Desenhar fundo do hover
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
                # Verificar qual opção foi clicada
                for i, opcao in enumerate(opcoes):
                    y_pos = height//2 + i * 80 - 40
                    text_width = font_options.size(opcao)[0]
                    text_height = font_options.size(opcao)[1]
                    text_rect = pygame.Rect(width//2 - text_width//2 - 20, y_pos - 20, text_width + 40, text_height + 40)
                    
                    if text_rect.collidepoint(x, y):
                        if i == 0:
                            modo_selecionado = 1  # Human vs Human
                            menu_running = False
                        elif i == 1:
                            modo_selecionado = 2  # AI vs Human
                            menu_running = False
                        elif i == 2:
                            #modo_selecionado = 3   AI vs AI
                            pass
    
    return modo_selecionado

def show_end_popup(winner):
    """Display end game popup with winner information"""
    # Create a semi-transparent overlay
    overlay = pygame.Surface((width, height))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Create popup surface
    popup_width = 350
    popup_height = 150
    popup_x = (width - popup_width) // 2
    popup_y = (height - popup_height) // 2
    
    popup = pygame.Surface((popup_width, popup_height))
    popup.fill((40, 40, 60))
    pygame.draw.rect(popup, (100, 100, 120), popup.get_rect(), 3, border_radius=15)
    
    # Font
    font_title = pygame.font.Font(None, 36)
    
    # Determine winner text and color
    if winner == 1:
        winner_text = "PLAYER 1 WINS!"
        winner_color = player1
    elif winner == 2:
        winner_text = "PLAYER 2 WINS!"
        winner_color = player2
    elif winner == 3:
        winner_text = "AI 1 WINS!"
        winner_color = player1
    elif winner == 4:
        winner_text = "AI 2 WINS!"
        winner_color = player2
    else:
        winner_text = "IT'S A TIE!"
        winner_color = (255, 215, 0)
    
    # Render winner text
    text = font_title.render(winner_text, True, winner_color)
    text_rect = text.get_rect(center=(popup_width//2, popup_height//2))
    popup.blit(text, text_rect)
    
    # Blit popup to screen
    screen.blit(popup, (popup_x, popup_y))
    pygame.display.update()
    
    # Wait 2 seconds then close
    pygame.time.wait(2000)

#loop principal do jogo
modo_jogo = show_menu()
running = True
current_player = 1
ia_turn = False
while running:

    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not (modo_jogo == 2 and current_player == 2):# and not (modo_jogo == 3 and current_player == 1):
            
            x = event.pos[0]
            y = event.pos[1]

            col = x // cell_size

            if y < top_area:
                if not col_isFull(matrix, col):
                    drop(matrix, current_player, col)
                    screen.fill(black)
                    draw_board(matrix)
                    pygame.display.update()

                    if check_victory(matrix, current_player):
                        show_end_popup(current_player)
                        running = False    

                    if current_player == 1:
                        current_player = 2
                        ia_turn = True
                    else:
                        current_player = 1


            elif y > height - bottom_area:
                if check_pop(matrix, current_player, col):
                    pop(matrix, current_player, col)
                    screen.fill(black)
                    draw_board(matrix)
                    pygame.display.update()



                    boolean_victory_1 = check_victory(matrix, 1)
                    boolean_victory_2 = check_victory(matrix, 2)
                
                    if boolean_victory_1 and boolean_victory_2:
                        print("Empate!")
                        running = False

                    elif boolean_victory_1:
                        print("Jogador 1 ganhou!")
                        running = False
                    elif boolean_victory_2:
                        print("Jogador 2 ganhou!")
                        running = False

                        
                    if current_player == 1:
                         
                        current_player = 2
                        ia_turn = True
                    else:
                        current_player = 1
            
    if modo_jogo == 2 and current_player == 2 and running and ia_turn  :

        movimento = MCTS.algoritmo_mcts(matrix, current_player, 5000)

        if movimento[0] == "drop":
            drop(matrix, current_player, movimento[1])
            screen.fill(black)
            draw_board(matrix)

        else:
            pop(matrix, current_player, movimento[1])
            screen.fill(black)
            draw_board(matrix)




        # verificar vitória (igual ao teu código)
        boolean_victory_1 = check_victory(matrix, 1)
        boolean_victory_2 = check_victory(matrix, 2)

        if boolean_victory_1 and boolean_victory_2:
            show_end_popup(0)  # Tie
            running = False
        elif boolean_victory_1:
            show_end_popup(3)
            time.delay(2000)
            running = False
        elif boolean_victory_2:
            show_end_popup(4)
            pygame.time.delay(300)
            running = False

        current_player = 1
        ia_turn = False
    '''
    if modo_jogo == 3 and current_player == 2 and running:

        movimento = MCTS.algoritmo_mcts(matrix, current_player, 5000)

        if movimento[0] == "drop":
            drop(matrix, current_player, movimento[1])
        else:
            pop(matrix, current_player, movimento[1])

        # verificar vitória
        boolean_victory_1 = check_victory(matrix, 1)
        boolean_victory_2 = check_victory(matrix, 2)

        if boolean_victory_1 and boolean_victory_2:
            show_end_popup(0)  # Tie
            running = False
        elif boolean_victory_1:
            show_end_popup(3)
            running = False
        elif boolean_victory_2:
            show_end_popup(4)
            running = False

        current_player = 1
    
    if modo_jogo == 3 and current_player == 1 and running:

        movimento = MCTS.algoritmo_mcts(matrix, current_player, 5000)

        if movimento[0] == "drop":
            drop(matrix, current_player, movimento[1])
        else:
            pop(matrix, current_player, movimento[1])

        # verificar vitória
        boolean_victory_1 = check_victory(matrix, 1)
        boolean_victory_2 = check_victory(matrix, 2)

        if boolean_victory_1 and boolean_victory_2:
            print("Empate!")
            running = False
        elif boolean_victory_1:
            print("IA 1 ganhou!")
            running = False
        elif boolean_victory_2:
            print("IA 2 ganhou!")
            running = False

        current_player = 2
    '''
    
    screen.fill(black)
    draw_board(matrix) 


    #destacar a coluna onde o rato está 

    mouse_x = pygame.mouse.get_pos()[0]
    mouse_y = pygame.mouse.get_pos()[1]

    
    col = mouse_x // cell_size

    highlight = pygame.Surface((cell_size, ROWS * cell_size), pygame.SRCALPHA)
    highlight.fill((255, 255, 255, 40))

    screen.blit(highlight, (col * cell_size, top_area))

    #desenhar a peça do jogador atual na parte superior do tabuleiro

    if mouse_y < top_area and not (modo_jogo == 2 and current_player == 2): #and not (modo_jogo == 3):

        if current_player == 1:
            color = player1
        else:
            color = player2

        pygame.draw.circle(screen, color,(mouse_x, top_area//2), cell_size//2 - 10)




    pygame.display.update()



pygame.quit()