import pygame
import MCTS
from game_logic import *

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


#loop principal do jogo
modo_jogo = 2
running = True
current_player = 1

while running:

    for event in pygame.event.get():

        if event.type == pygame.MOUSEBUTTONDOWN and not (modo_jogo == 2 and current_player == 2):
            
            x = event.pos[0]
            y = event.pos[1]

            col = x // cell_size

            if y < top_area:
                if not col_isFull(matrix, col):
                    drop(matrix, current_player, col)
                    if check_victory(matrix, current_player):
                        print("Jogador", current_player, "ganhou!")
                        running = False    

                    if current_player == 1:
                        current_player = 2
                    else:
                        current_player = 1


            elif y > height - bottom_area:
                if check_pop(matrix, current_player, col):
                    pop(matrix, current_player, col)
                    
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
                    else:
                        current_player = 1
            
    if modo_jogo == 2 and current_player == 2 and running:

        movimento = MCTS.algoritmo_mcts(matrix, current_player, 5000)

        if movimento[0] == "drop":
            drop(matrix, current_player, movimento[1])
        else:
            pop(matrix, current_player, movimento[1])

        # verificar vitória (igual ao teu código)
        boolean_victory_1 = check_victory(matrix, 1)
        boolean_victory_2 = check_victory(matrix, 2)

        if boolean_victory_1 and boolean_victory_2:
            print("Empate!")
            running = False
        elif boolean_victory_1:
            print("Jogador 1 ganhou!")
            running = False
        elif boolean_victory_2:
            print("IA ganhou!")
            running = False

        current_player = 1


        if event.type == pygame.QUIT:
            running = False

    
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

    if mouse_y < top_area:

        if current_player == 1:
            color = player1
        else:
            color = player2

        pygame.draw.circle(screen, color,(mouse_x, top_area//2), cell_size//2 - 10)




    pygame.display.update()



pygame.quit()