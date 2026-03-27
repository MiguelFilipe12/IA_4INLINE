import random
import game_logic as gl
import copy
import math

class Node:
    def __init__(self, board, jogador_atual):
        self.board = copy.deepcopy(board)
        self.jogador_atual = jogador_atual
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = possible_moves(self.board, jogador_atual)
        self.parent = None
        self.move = None
    

    def expand(self):
        if len(self.untried_moves) == 0:
            return None
        move = self.untried_moves.pop()
        new_board = copy.deepcopy(self.board)
        if move[0] == "drop":
            gl.drop (new_board, self.jogador_atual, move[1])
        else:
            gl.pop (new_board, self.jogador_atual, move[1])
        child = Node(new_board, 3 - self.jogador_atual)
        child.move = move
        child.parent = self
        self.children.append(child)
        return child

    def select_child(self):
        best_score = -float('inf')
        best_child = None
        
        # Vitória imediata
        for child in self.children:
            if child.move:
                move_info = apply_move(self.board, self.jogador_atual, child.move)

                if gl.check_victory(self.board, self.jogador_atual):
                    undo_move(self.board, move_info)
                    return child

                undo_move(self.board, move_info)
        
        for child in self.children:
            if child.visits == 0:
                return child
            
            exploration = 1.2
            UCT = (child.wins / child.visits) + exploration * math.sqrt(math.log(self.visits) / child.visits)
            
            #so verifica ameaças 30% das vezes para não deixar o algoritmo muito lento
            if child.move and random.random() < 0.3:
                
                move_info = apply_move(self.board, self.jogador_atual, child.move)

                if gl.check_winning_threat(self.board, 2):
                    UCT += 0.2

                if gl.check_winning_threat(self.board, 1):
                    UCT -= 0.2

                undo_move(self.board, move_info)
            
            if UCT > best_score:
                best_score = UCT
                best_child = child

        return best_child

    def is_terminal(self):
        if gl.check_victory(self.board, 1) or gl.check_victory(self.board, 2):
            return True
        if len(possible_moves(self.board, self.jogador_atual)) == 0:
            return True 
        return False
    
    def backpropagate(self, result):
        node = self

        while node is not None:
            node.visits += 1

            
            if result == 2:
                node.wins += 1

            
            elif result == 0:
                node.wins += 0.5

            node = node.parent

def possible_moves(board, jogador_atual):
    
    winning_moves = []
    safe_moves = []
    dangerous_moves = []
    
    for col in range(gl.COLS):
        
        # -------- DROP --------
        if not gl.col_isFull(board, col):
            
            move = ("drop", col)
            move_info = apply_move(board, jogador_atual, move)

            # vitória imediata
            if gl.check_victory(board, jogador_atual):
                winning_moves.append(move)

            else:
                opponent = 3 - jogador_atual
                opponent_moves = []

                for c in range(gl.COLS):
                    if not gl.col_isFull(board, c):
                        opponent_moves.append(("drop", c))
                    if gl.check_pop(board, opponent, c):
                        opponent_moves.append(("pop", c))

                opponent_can_win = False

                for op_move in opponent_moves:
                    op_info = apply_move(board, opponent, op_move)

                    if gl.check_victory(board, opponent):
                        opponent_can_win = True

                    undo_move(board, op_info)

                    if opponent_can_win:
                        break

                if opponent_can_win:
                    dangerous_moves.append(move)
                else:
                    safe_moves.append(move)

            undo_move(board, move_info)

        # -------- POP --------
        if gl.check_pop(board, jogador_atual, col):

            move = ("pop", col)
            move_info = apply_move(board, jogador_atual, move)

            # vitória imediata
            if gl.check_victory(board, jogador_atual):
                winning_moves.append(move)

            else:
                opponent = 3 - jogador_atual
                opponent_moves = []

                for c in range(gl.COLS):
                    if not gl.col_isFull(board, c):
                        opponent_moves.append(("drop", c))
                    if gl.check_pop(board, opponent, c):
                        opponent_moves.append(("pop", c))

                opponent_can_win = False

                for op_move in opponent_moves:
                    op_info = apply_move(board, opponent, op_move)

                    if gl.check_victory(board, opponent):
                        opponent_can_win = True

                    undo_move(board, op_info)

                    if opponent_can_win:
                        break

                if opponent_can_win:
                    dangerous_moves.append(move)
                else:
                    safe_moves.append(move)

            undo_move(board, move_info)

    if winning_moves:
        return winning_moves
    elif safe_moves:
        return safe_moves
    else:
        return dangerous_moves

def simulate(board, jogador_atual):
    jogador = jogador_atual
    board_simulate = copy.deepcopy(board)

    while True:
        if gl.check_victory(board_simulate, 1):
            return 1
        if gl.check_victory(board_simulate, 2):
            return 2

        moves = possible_moves(board_simulate, jogador)

        if len(moves) == 0:
            return 0

        weights = []

        for move in moves:
            weight = 1.0

            
            move_info = apply_move(board_simulate, jogador, move)

           
            if gl.check_victory(board_simulate, jogador):
                weight = 100.0

            else:
                opponent = 3 - jogador
                opponent_moves = possible_moves(board_simulate, opponent)

                opponent_can_win = False

                for op_move in opponent_moves:
                    op_info = apply_move(board_simulate, opponent, op_move)

                    if gl.check_victory(board_simulate, opponent):
                        opponent_can_win = True

                    undo_move(board_simulate, op_info)

                    if opponent_can_win:
                        break

                if opponent_can_win:
                    weight -= 0.5
                else:
                    if move[0] == "drop":
                        if move[1] == gl.COLS // 2:
                            weight = 1.5
                        elif abs(move[1] - gl.COLS // 2) == 1:
                            weight = 1.2

            
            undo_move(board_simulate, move_info)

            weights.append(weight)

        move = random.choices(moves, weights=weights)[0]

        # jogada real
        if move[0] == "drop":
            gl.drop(board_simulate, jogador, move[1])
        else:
            gl.pop(board_simulate, jogador, move[1])

        jogador = 3 - jogador

def algoritmo_mcts(board, jogador_atual, iteracoes):
    
    root = Node(board, jogador_atual)
    if len(root.untried_moves) > 0:
        root.expand()
    
    # First, check for immediate winning move
    for col in range(gl.COLS):
        if not gl.col_isFull(board, col):
            test_board = copy.deepcopy(board)
            gl.drop(test_board, jogador_atual, col)
            if gl.check_victory(test_board, jogador_atual):
                return ("drop", col)
    
    # Check for immediate blocking move
    opponent = 3 - jogador_atual
    for col in range(gl.COLS):
        if not gl.col_isFull(board, col):
            test_board = copy.deepcopy(board)
            gl.drop(test_board, opponent, col)
            if gl.check_victory(test_board, opponent):
                return ("drop", col)
    
   
    for it in range(iteracoes):
        node = root
        while not node.is_terminal() and len(node.untried_moves) == 0:
            node = node.select_child()
        
        if not node.is_terminal():
            node = node.expand()
            if node is None:
                continue
        
        result = simulate(node.board, node.jogador_atual)
        node.backpropagate(result)
    
    best_child = None
    best_visits = -1
    for child in root.children:
        if child.visits > best_visits:
            best_visits = child.visits
            best_child = child
    
    if best_child is None:
        moves = possible_moves(board, jogador_atual)
        return random.choice(moves) if moves else None

    return best_child.move



def apply_move(board, jogador, move):
    if move[0] == "drop":
        row = gl.get_row_before_drop(board, move[1])
        gl.drop(board, jogador, move[1])
        return ("drop", move[1], row)
    else:
        removed = board[-1][move[1]]
        gl.pop(board, jogador, move[1])
        return ("pop", move[1], removed)


def undo_move(board, move_info):
    if move_info[0] == "drop":
        col = move_info[1]
        row = move_info[2]
        board[row][col] = 0
    else:
        col = move_info[1]
        removed = move_info[2]
        # desfazer pop → empurrar tudo para baixo
        for r in reversed(range(1, gl.ROWS)):
            board[r][col] = board[r-1][col]
        board[0][col] = removed
