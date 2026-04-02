import game_logic as gl
import math
import random
from collections import defaultdict

def get_legal_moves(board, player):
    """Retorna todos os movimentos possíveis, na forma (tipo de jogada, coluna)"""
    moves = []
    for col in range(gl.COLS):
        if not gl.col_isFull(board, col):
            moves.append(("drop", col))
        if gl.check_pop(board, player, col):
            moves.append(("pop", col))
    return moves

def is_winning_move(board, player, move):
    """Verifica se um movimento específico é terminal (vitória)"""
    temp_board = [row[:] for row in board]
    # Simula a jogada
    if move[0] == "drop":
        gl.drop(temp_board, player, move[1])
    else:
        gl.pop(temp_board, player, move[1])
    return gl.check_victory(temp_board, player)

def is_blocking_move(board, player, move):
    """Verifica se um movimento bloqueia uma jogada terminal do adversário (derrota)"""
    opponent = 3 - player
    temp_board = [row[:] for row in board]
    if move[0] == "drop":
        gl.drop(temp_board, player, move[1])
    else:
        gl.pop(temp_board, player, move[1])
    return not gl.check_winning_threat(temp_board, opponent)

def evaluate_window(window, player, opponent):
    """Avalia todas as janelas de 4 peças possíveis"""
    player_count = window.count(player)
    opponent_count = window.count(opponent)
    empty_count = window.count(0)
    
    if player_count == 4: return 10000000 # Vitória
    if player_count == 3 and empty_count == 1: return 100000 # Jogada quase terminal
    
    # Ameaça dupla
    if player_count == 2 and empty_count == 2:
        # Se tiver 2 caminhos possíveis de vitória, favorece a jogada
        if window[0] == 0 and window[3] == 0:
            return 5000
        return 1000
    
    # Bloqueia ameaças
    if opponent_count == 3 and empty_count == 1:
        return -100000  # Tem de bloquear
    
    if opponent_count == 4:
        return -10000000 # Derrota
    
    if player_count == 1 and empty_count == 3:
        return 10
    
    if opponent_count == 2 and empty_count == 2:
        return -500
    
    return 0

def evaluate_position(board, player):
    """
    Heuristica de avaliação com reconhecimento de padrões
    """
    opponent = 3 - player
    total_score = 0
    
    # Cache for window evaluation
    windows = []
    
    # Horizontal
    for r in range(gl.ROWS):
        for c in range(gl.COLS - 3):
            window = [board[r][c + i] for i in range(4)] # Cria janela
            score = evaluate_window(window, player, opponent) # Avalia o score potencial da janela
            total_score += score
            windows.append((score, r, c, 'h')) # Armazena a janela
    
    # Vertical
    for c in range(gl.COLS):
        for r in range(gl.ROWS - 3):
            window = [board[r + i][c] for i in range(4)]
            score = evaluate_window(window, player, opponent)
            total_score += score
            windows.append((score, r, c, 'v'))
    
    # Diagonal 
    for r in range(gl.ROWS - 3):
        for c in range(gl.COLS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score = evaluate_window(window, player, opponent)
            total_score += score
            windows.append((score, r, c, 'd'))
    
    # Diagonal
    for r in range(3, gl.ROWS):
        for c in range(gl.COLS - 3):
            window = [board[r - i][c + i] for i in range(4)]
            score = evaluate_window(window, player, opponent)
            total_score += score
            windows.append((score, r, c, 'u'))
    
    # Controlo do centro do tabuleiro
    center_col = gl.COLS // 2
    center_weight = 0
    # Favorece o controlo da coluna central, premiando as jogadas
    for r in range(gl.ROWS):
        if board[r][center_col] == player:
            center_weight += 3
        elif board[r][center_col] == opponent:
            center_weight -= 3 
    total_score += center_weight
    
    # Premia a versatilidade consonate o estado do tabuleiro (quantas mais jogadas melhor)
    player_moves = len(get_legal_moves(board, player))
    opponent_moves = len(get_legal_moves(board, opponent))
    total_score += (player_moves - opponent_moves) * 2
    
    # Verifica a existência de ameaças duplas (jogadas com mais de 1 vitória possível)
    threat_count = 0
    for window_score, _, _, _ in windows:
        if abs(window_score) >= 100000 and window_score > 0:
            threat_count += 1
    if threat_count >= 2:
        total_score += 500000 
    
    return total_score

def minimax(board, depth, alpha, beta, maximizing_player, player, caching=None):
    """
    Algoritmo minimax com alpha-beta pruning
    """
    if caching is None:
        caching = {}
    
    opponent = 3 - player
    current = player if maximizing_player else opponent
    
    # Verifica se é estado terminal
    if gl.check_victory(board, player):
        return (10000000 + depth, None)
    if gl.check_victory(board, opponent):
        return (-10000000 - depth, None)
    
    is_full = True
    for col in range(gl.COLS):
        if not gl.col_isFull(board, col):
            is_full = False
            break
    if is_full:
        return (0, None)
    
    if depth == 0:
        return (evaluate_position(board, player), None)
    
    # Verifica se o estado atual já foi encontrado na pesquisa, utilizando o que resulta da pesquisa mais profunda
    board_key = str(board)
    if board_key in caching and caching[board_key][0] >= depth:
        return caching[board_key][1]
    
    moves = get_legal_moves(board, current)
    if not moves:
        return (0, None)
    
    # Ordenação de movimentos a explorar
    def move_priority(move):
        priority = 0
        # Quanto mais próximo do centro, maior o nº de combinações possíveis (suposto), logo melhor jogada
        priority += 10 - abs(move[1] - gl.COLS//2) * 2
        
        # Se o movimento resultar em vitória, prioridade máxima
        if is_winning_move(board, current, move):
            priority += 1000000
        
        # Se o próximo movimento do adversário resultar em derrota, priorizar o bloqueio
        if current == player and is_winning_move(board, opponent, move):
            priority += 500000
            
        return priority
    
    moves.sort(key=move_priority, reverse=True)
    
    if maximizing_player:
        max_score = -math.inf
        best_move = moves[0] # Jogadas aparecem por ordem de prioridade
        
        for move in moves:
            temp_board = [row[:] for row in board]
            if move[0] == "drop":
                gl.drop(temp_board, current, move[1])
            else:
                gl.pop(temp_board, current, move[1])
            
            score, _ = minimax(temp_board, depth - 1, alpha, beta, False, player, caching)
            
            if score > max_score:
                max_score = score
                best_move = move
            
            alpha = max(alpha, max_score)
            if beta <= alpha:
                break
        
        caching[board_key] = (depth, (max_score, best_move))
        return (max_score, best_move)
    
    else:
        min_score = math.inf
        best_move = moves[0]
        
        for move in moves:
            temp_board = [row[:] for row in board]
            if move[0] == "drop":
                gl.drop(temp_board, current, move[1])
            else:
                gl.pop(temp_board, current, move[1])
            
            score, _ = minimax(temp_board, depth - 1, alpha, beta, True, player, caching)
            
            if score < min_score:
                min_score = score
                best_move = move
            
            beta = min(beta, min_score)
            if beta <= alpha:
                break
        
        caching[board_key] = (depth, (min_score, best_move))
        return (min_score, best_move)

def get_best_move(board, player, max_depth=8, time_limit=2.0):
    """
    Encontrar o melhor movimento com iterative deepening
    """
    import time
    start_time = time.time()
    
    moves = get_legal_moves(board, player)
    if not moves:
        return None
    
    # Verificação de jogadas terminais
    for move in moves:
        if is_winning_move(board, player, move):
            return move
    
    # Verificação de bloqueios
    opponent = 3 - player
    for move in moves:
        temp_board = [row[:] for row in board]
        if move[0] == "drop":
            gl.drop(temp_board, player, move[1])
        else:
            gl.pop(temp_board, player, move[1])
        
        # ISe o oponente não estiver em vias de ganhar, é seguro
        if not gl.check_winning_threat(temp_board, opponent):
            opponent_can_win = False
            for opp_move in get_legal_moves(temp_board, opponent):
                if is_winning_move(temp_board, opponent, opp_move):
                    opponent_can_win = True
                    break
            
            if not opponent_can_win:
                # Movimento seguro
                safe_move = move
                # Verificação da existência de alguma jogada melhor
                if abs(move[1] - gl.COLS//2) <= 1:
                    return move
        
    # Iterative deepening
    best_move = None
    best_score = -math.inf
    
    for depth in range(1, max_depth + 1):
        if time.time() - start_time > time_limit:
            break
        
        try:
            score, move = minimax(board, depth, -math.inf, math.inf, True, player)
            
            if move is not None and score > best_score:
                best_score = score
                best_move = move
                
            # Parar se encontrarmos uma jogada terminal (vitória)
            if score >= 10000000:
                break
        except:
            break
    
    # Caso não encontremos uma jogada superior
    if best_move is None:
        center_col = gl.COLS // 2
        center_moves = [m for m in moves if m[1] == center_col]
        if center_moves:
            best_move = center_moves[0]
        else:
            best_move = moves[0]
    
    return best_move