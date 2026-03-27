ROWS = 6
COLS = 7

def iniciar_matrix (): 
    matrix = []
    for r in range(ROWS):

        linha = []

        for c in range(COLS):
            linha.append(0)

        matrix.append(linha)
    return matrix


matrix = iniciar_matrix () 

def print_matrix (board):

    for row in board:
        print (row)


def drop(board, peca, col):

    if col_isFull(board, col):
        print("não podes colocar aqui")
        return

    for r in range(ROWS-1, -1, -1):
        if board[r][col] == 0:
            board[r][col] = peca
            break

    

def col_isFull(board, col):
    if board[0][col] != 0:
        return True
    return False

def check_victory(board, peca):
    # horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if board[r][c] == peca and board[r][c+1] == peca and board[r][c+2] == peca and board[r][c+3] == peca:
                return True

    # vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if board[r][c] == peca and board[r+1][c] == peca and board[r+2][c] == peca and board[r+3][c] == peca:
                return True

    # diagonal (descer)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if board[r][c] == peca and board[r+1][c+1] == peca and board[r+2][c+2] == peca and board[r+3][c+3] == peca:
                return True

    # diagonal (subir)
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if board[r][c] == peca and board[r-1][c+1] == peca and board[r-2][c+2] == peca and board[r-3][c+3] == peca:
                return True

    return False

def pop (board, player, col):
    
    for r in range (ROWS - 1, 0, -1):
        board[r][col] = board [r-1][col]


    board[0][col] = 0            

def check_pop(board, player, col):

    if col < 0 or col >= COLS:
        return False

    if board[ROWS-1][col] != player:
        return False

    return True

################################# MAIN ###################################


