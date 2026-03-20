import pygame

# --- 定数設定 ---
BOARD_SIZE = 8
CELL_SIZE = 60
WINDOW_SIZE = BOARD_SIZE * CELL_SIZE

EMPTY = 0
BLACK = 1   # プレイヤー
WHITE = -1  # コンピューター

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


# --- 盤面関連ロジック ---

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
            flips = get_flips(board, x, y, color)
            if flips:
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


# --- AI（コンピューター） ---

def ai_choose_move(board, color):
    valid_moves = get_valid_moves(board, color)
    if not valid_moves:
        return None

    best_move = None
    best_score = -1
    for x, y in valid_moves:
        flips = get_flips(board, x, y, color)
        score = len(flips)
        if score > best_score:
            best_score = score
            best_move = (x, y)
    return best_move


# --- 描画関連 ---

def draw_board(screen, board, valid_moves, font, game_over, msg):
    screen.fill(BG_COLOR)

    # グリッド
    for i in range(BOARD_SIZE + 1):
        pygame.draw.line(
            screen, GRID_COLOR,
            (i * CELL_SIZE, 0),
            (i * CELL_SIZE, WINDOW_SIZE), 2
        )
        pygame.draw.line(
            screen, GRID_COLOR,
            (0, i * CELL_SIZE),
            (WINDOW_SIZE, i * CELL_SIZE), 2
        )

    # 石
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            cell = board[y][x]
            if cell != EMPTY:
                cx = x * CELL_SIZE + CELL_SIZE // 2
                cy = y * CELL_SIZE + CELL_SIZE // 2
                color = BLACK_COLOR if cell == BLACK else WHITE_COLOR
                pygame.draw.circle(screen, color, (cx, cy), CELL_SIZE // 2 - 4)

    # 打てる場所のハイライト
    for x, y in valid_moves:
        cx = x * CELL_SIZE + CELL_SIZE // 2
        cy = y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, HINT_COLOR, (cx, cy), 6)

    # スコア
    black_count, white_count = count_discs(board)
    info_text = f"Player(B): {black_count}  CPU(W): {white_count}"
    text_surf = font.render(info_text, True, (255, 255, 255))
    screen.blit(text_surf, (10, WINDOW_SIZE - 28))

    # ゲームオーバー表示
    if game_over and msg:
        text_surf2 = font.render(msg, True, (255, 255, 0))
        screen.blit(text_surf2, (10, 10))


def pos_to_cell(pos):
    x, y = pos
    cx = x // CELL_SIZE
    cy = y // CELL_SIZE
    if in_bounds(cx, cy):
        return cx, cy
    return None


# --- メインループ ---

def main():
    pygame.init()
    # Web では SCALED を付けておくと扱いやすい
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE), pygame.SCALED)
    pygame.display.set_caption("Othello (Web, Player vs CPU)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

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
            black_count, white_count = count_discs(board)
            if black_count > white_count:
                game_over_msg = "Game Over: Player Wins!"
            elif white_count > black_count:
                game_over_msg = "Game Over: CPU Wins!"
            else:
                game_over_msg = "Game Over: Draw!"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # ブラウザではウィンドウは閉じないが、ループは抜ける
                running = False

            if game_over:
                continue

            if current_color == BLACK and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cell = pos_to_cell(event.pos)
                if cell:
                    x, y = cell
                    if apply_move(board, x, y, BLACK):
                        current_color = WHITE

        # CPU 手番
        if not game_over and current_color == WHITE:
            move = ai_choose_move(board, WHITE)
            if move:
                x, y = move
                apply_move(board, x, y, WHITE)
            current_color = BLACK

        valid_moves = get_valid_moves(board, current_color) if not game_over else []
        draw_board(screen, board, valid_moves, font, game_over, game_over_msg)

        pygame.display.flip()

    # ブラウザ環境では pygame.quit() だけで十分
    pygame.quit()


# PyScript の py-game では、モジュール読み込み時に main() を呼ぶ必要がある
if __name__ == "__main__":
    main()
else:
    # py-game から読み込まれた場合も main を起動
    main()
    