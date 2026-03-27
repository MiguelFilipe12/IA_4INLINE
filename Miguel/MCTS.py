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
        
        # Check for immediate winning moves first (heuristic)
        for child in self.children:
            if child.move and child.move[0] == "drop":
                # Check if this move would win for the current player
                test_board = copy.deepcopy(self.board)
                gl.drop(test_board, self.jogador_atual, child.move[1])
                if gl.check_victory(test_board, self.jogador_atual):
                    return child
        
        for child in self.children:
            if child.visits == 0:
                return child
            
            # Increased exploration constant for better exploration
            exploration = 1.0  # Reduced from sqrt(2) to focus more on exploitation for critical moves
            UCT = (child.wins / child.visits) + exploration * math.sqrt(math.log(self.visits) / child.visits)
            
            # Bonus for moves that are close to winning (heuristic)
            if child.move and child.move[0] == "drop":
                # Check if this move creates a threat
                test_board = copy.deepcopy(self.board)
                gl.drop(test_board, self.jogador_atual, child.move[1])
                if gl.check_winning_threat(test_board, self.jogador_atual):
                    UCT += 0.5  # Bonus for threatening moves
            
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
            if result == node.jogador_atual:
                node.wins += 1
            elif result == 0:
                # For draws, give partial credit
                node.wins += 0.5
            node = node.parent

def possible_moves(board, jogador_atual):
    
    moves = []
    
    # Prioritize winning moves and blocking moves
    winning_moves = []
    blocking_moves = []
    regular_moves = []
    
    for col in range(gl.COLS):
        if not gl.col_isFull(board, col):
            # Check if this move wins
            test_board = copy.deepcopy(board)
            gl.drop(test_board, jogador_atual, col)
            if gl.check_victory(test_board, jogador_atual):
                winning_moves.append(("drop", col))
            else:
                # Check if this move blocks opponent's win
                opponent = 3 - jogador_atual
                test_board_opponent = copy.deepcopy(board)
                gl.drop(test_board_opponent, opponent, col)
                if gl.check_victory(test_board_opponent, opponent):
                    blocking_moves.append(("drop", col))
                else:
                    regular_moves.append(("drop", col))
        
        if gl.check_pop(board, jogador_atual, col):
            regular_moves.append(("pop", col))
    
    # Prioritize winning moves first, then blocking moves
    moves = winning_moves + blocking_moves + regular_moves
    return moves


def simulate(board, jogador_atual):
    jogador = jogador_atual
    board_simulate = copy.deepcopy(board)
    
    # Heuristic-based simulation instead of purely random
    max_moves = 42  # Maximum possible moves in Connect 4
    
    for _ in range(max_moves):
        boolean_victory_1 = gl.check_victory(board_simulate, 1)
        boolean_victory_2 = gl.check_victory(board_simulate, 2)
        
        if boolean_victory_1:
            return 1
        elif boolean_victory_2:
            return 2
        
        moves = possible_moves(board_simulate, jogador)
        if len(moves) == 0:
            return 0
        
        # Use weighted random selection for better simulations
        # Prioritize winning moves and blocking moves in simulation
        weighted_moves = []
        for move in moves:
            weight = 1.0
            if move[0] == "drop":
                # Check if move wins
                test_board = copy.deepcopy(board_simulate)
                gl.drop(test_board, jogador, move[1])
                if gl.check_victory(test_board, jogador):
                    weight = 100.0  # Very high weight for winning moves
                else:
                    # Check if move blocks opponent
                    opponent = 3 - jogador
                    test_board_opponent = copy.deepcopy(board_simulate)
                    gl.drop(test_board_opponent, opponent, move[1])
                    if gl.check_victory(test_board_opponent, opponent):
                        weight = 50.0  # High weight for blocking moves
                    else:
                        # Center column bias for better play
                        if move[1] == gl.COLS // 2:
                            weight = 1.5
                        elif abs(move[1] - gl.COLS // 2) == 1:
                            weight = 1.2
            weighted_moves.extend([move] * int(weight))
        
        if weighted_moves:
            move = random.choice(weighted_moves)
        else:
            move = random.choice(moves)
            
        if move[0] == "drop":
            gl.drop(board_simulate, jogador, move[1])
        else:
            gl.pop(board_simulate, jogador, move[1])
        
        jogador = 3 - jogador
    
    return 0


def algoritmo_mcts(board, jogador_atual, iteracoes):
    
    root = Node(board, jogador_atual)
    
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
    
    # Increase iterations for better decision making
    # Use dynamic iterations based on board state
    empty_cells = sum(row.count(0) for row in board)
    if empty_cells > 30:
        iteracoes = 3000  # Early game - fewer iterations
    elif empty_cells > 15:
        iteracoes = 5000  # Mid game - medium iterations
    else:
        iteracoes = 8000  # End game - more iterations to find winning moves
    
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
    
    return best_child.move