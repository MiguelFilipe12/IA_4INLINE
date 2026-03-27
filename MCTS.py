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

    def select_child (self):
        best_score = -float ('inf')
        best_child = None

        for child in self.children:

            if child.visits == 0:
                return child

            UCT = (child.wins / child.visits) + 1.414 * math.sqrt( math.log(self.visits) / child.visits )

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
            node = node.parent

def possible_moves(board, jogador_atual):
    
    moves = []
    for col in range(gl.COLS):
        if not gl.col_isFull(board, col):
            moves.append(("drop", col))
        if gl.check_pop(board, jogador_atual, col):
            moves.append(("pop", col))
    return moves


def simulate(board, jogador_atual):
    #verificar se o jogador 1 ganhou
    #verificar se o jogador 2 ganhou
    #cria jogadas possiveis
    #se não houver jogadas, é empate
    #escolhe uma jogada aleatoria
    #faz a jogada
    #muda o jogador atual
    jogador = jogador_atual
    board_simulate = copy.deepcopy(board)
    while True:
        boolean_victory_1 = gl.check_victory(board_simulate, 1)
        boolean_victory_2 = gl.check_victory(board_simulate, 2)

        if boolean_victory_1:
            return 1
        elif boolean_victory_2:
            return 2
        

        moves = possible_moves(board_simulate, jogador)
        if len(moves) == 0:
            return 0
        move = random.choice(moves)
        if move[0] == "drop":
            gl.drop (board_simulate, jogador, move[1])
        else:
            gl.pop (board_simulate, jogador, move[1])

        jogador = 3 - jogador

   

def algoritmo_mcts(board, jogador_atual, iteracoes):
    
    root  = Node(board, jogador_atual)
    for it in range(iteracoes):
        node = root
        while not node.is_terminal() and len(node.untried_moves) == 0:
            node = node.select_child()

        if not node.is_terminal():
            node = node.expand()

        result = simulate(node.board, node.jogador_atual)
        node.backpropagate(result)

    best_child = None
    best_visits = -1
    for child in root.children:
        if child.visits > best_visits:
            best_visits = child.visits
            best_child = child
    return best_child.move