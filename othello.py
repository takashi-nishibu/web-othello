import pygame

# --- 定数設定 ---
BOARD_SIZE = 8
CELL_SIZE = 60
WINDOW_SIZE = BOARD_SIZE * CELL_SIZE

EMPTY = 0
BLACK = 1
WHITE = -1

BG_COLOR = (0, 120, 0)
GRID_COLOR = (0, 0, 0)
BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (240, 240, 240)
HINT_COLOR = (200, 200, 0)

FPS = 60

DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),          (0, 1),
    (1, -1),  (1, 0), (1, 1)
]

def create_board():
    board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    mid = BOARD_SIZE // 2
    board[mid - 1][mid - 1] = WHITE
    board[mid][mid] = WHITE
    board[mid - 1][mid] = BLACK
    board[mid][mid - 1] = BLACK
    return board

def in_bounds(x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

def get_flips(board, x, y, color):
    if board[y][x] != EMPTY:
        return []
    flips = []
    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        temp = []
        while in_bounds(nx, ny) and board[ny][nx] == -color:
            temp.append((nx, ny))
            nx += dx
            ny += dy
        if in_bounds(nx, ny) and board[ny][nx] == color and temp:
            flips.extend(temp)
    return flips

def get_valid_moves(board, color):
    moves = []
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if get_flips(board, x, y, color):
                moves.append((x, y))
    return moves

def apply_move(board, x, y, color):
    flips = get_flips(board, x, y, color)
    if not flips:
        return False
    board[y][x] = color
    for fx, fy in flips:
        board[fy][fx] = color
    return True

def count_discs(board):
    black = sum(cell == BLACK for row in board for cell in row)
    white = sum(cell == WHITE for row in board for cell in row)
    return black, white

def ai_choose_move(board, color):
    valid_moves = get_valid_moves(board, color)
    if not valid_moves:
        return None
    best_move = None
    best_score = -1
    for x, y in valid_moves:
        score = len(get_flips(board, x, y, color))
        if score > best_score:
            best_score = score
            best_move = (x, y)
    return best_move

def draw_board(screen, board, valid_moves, font, game_over, msg):
    screen.fill(BG_COLOR)

    for i in range(BOARD_SIZE + 1):
        pygame.draw.line(screen, GRID_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, WINDOW_SIZE), 2)
        pygame.draw.line(screen, GRID_COLOR, (0, i * CELL_SIZE), (WINDOW_SIZE, i * CELL_SIZE), 2)

    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            cell = board[y][x]
            if cell != EMPTY:
                cx = x * CELL_SIZE + CELL_SIZE // 2
                cy = y * CELL_SIZE + CELL_SIZE // 2
                color = BLACK_COLOR if cell == BLACK else WHITE_COLOR
                pygame.draw.circle(screen, color, (cx, cy), CELL_SIZE // 2 - 4)

    for x, y in valid_moves:
        cx = x * CELL_SIZE + CELL_SIZE // 2
        cy = y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, HINT_COLOR, (cx, cy), 6)

    black_count, white_count = count_discs(board)
    info_text = f"Player(B): {black_count}  CPU(W): {white_count}"
    screen.blit(font.render(info_text, True, (255, 255, 255)), (10, WINDOW_SIZE - 28))

    if game_over and msg:
        screen.blit(font.render(msg, True, (255, 255, 0)), (10, 10))

def pos_to_cell(pos):
    x, y = pos
    cx = x // CELL_SIZE
    cy = y // CELL_SIZE
    return (cx, cy) if in_bounds(cx, cy) else None

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    board = create_board()
    current_color = BLACK
    running = True
    game_over = False
    game_over_msg = ""

    while running:
        clock.tick(FPS)

        player_moves = get_valid_moves(board, BLACK)
        cpu_moves = get_valid_moves(board, WHITE)

        if not game_over and not player_moves and not cpu_moves:
            game_over = True
            b, w = count_discs(board)
            if b > w:
                game_over_msg = "Game Over: Player Wins!"
            elif w > b:
                game_over_msg = "Game Over: CPU Wins!"
            else:
                game_over_msg = "Game Over: Draw!"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_over:
                continue

            if current_color == BLACK and event.type == pygame.MOUSEBUTTONDOWN:
                cell = pos_to_cell(event.pos)
                if cell and apply_move(board, cell[0], cell[1], BLACK):
                    current_color = WHITE

        if not game_over and current_color == WHITE:
            move = ai_choose_move(board, WHITE)
            if move:
                apply_move(board, move[0], move[1], WHITE)
            current_color = BLACK

        valid_moves = get_valid_moves(board, current_color) if not game_over else []
        draw_board(screen, board, valid_moves, font, game_over, game_over_msg)
        pygame.display.flip()

    pygame.quit()

main()