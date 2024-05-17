import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
GRID_SIZE = 30
COLUMNS = SCREEN_WIDTH // GRID_SIZE
ROWS = SCREEN_HEIGHT // GRID_SIZE
high_score_file = "highscore.txt"

# Colors
NINTENDO_DK_GREY = (138, 137, 136)
NINTENDO_RED = (220, 46, 41)
NINTENDO_GREY = (241, 243, 237)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]  # Z
]

# Colors for each shape
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]


class Tetromino:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = SHAPE_COLORS[SHAPES.index(self.shape)]
        self.x = COLUMNS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]


try:
    with open(high_score_file, "r") as file:
        high_score = int(file.read())
except FileNotFoundError:
    high_score = 0


def update_high_score(new_score):
    global high_score
    if new_score > high_score:
        high_score = new_score
        with open(high_score_file, "w") as file:
            file.write(str(high_score))


def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLUMNS):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid


def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLUMNS):
            pygame.draw.rect(surface, grid[y][x], (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
    draw_grid_lines(surface)


def draw_grid_lines(surface):
    for x in range(COLUMNS):
        pygame.draw.line(surface, WHITE, (x * GRID_SIZE, 0), (x * GRID_SIZE, SCREEN_HEIGHT))
    for y in range(ROWS):
        pygame.draw.line(surface, WHITE, (0, y * GRID_SIZE), (SCREEN_WIDTH, y * GRID_SIZE))


def display_score(surface, current_score):
    score_font = pygame.font.SysFont('agencyfb', 32)
    score_label = score_font.render(f'     SCORE: {current_score}', 1, NINTENDO_RED)
    high_score_label = score_font.render(f'HI-SCORE: {high_score}', 1, NINTENDO_RED)
    surface.blit(score_label, (SCREEN_WIDTH + 5, 50))
    surface.blit(high_score_label, (SCREEN_WIDTH + 5, 20))


def draw_next_shape(surface, shape):
    font = pygame.font.SysFont('agencyfb', 42, bold=False)
    label = font.render('NEXT SHAPE', 1, NINTENDO_RED)
    surface.blit(label, (SCREEN_WIDTH + 10, 150))
    for y, row in enumerate(shape.shape):
        for x, col in enumerate(row):
            if col:
                pygame.draw.rect(surface, shape.color,
                                 (SCREEN_WIDTH + 40 + x * GRID_SIZE, 200 + y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)


def draw_panel(surface):
    pygame.draw.rect(surface, NINTENDO_GREY, (SCREEN_WIDTH, 0, 200, 300), 0)


def hide_previous_shape(surface):
    pygame.draw.rect(surface, NINTENDO_DK_GREY, (SCREEN_WIDTH, 302, 200, 300), 0)


def clear_rows(grid, locked_positions):
    cleared_rows = 0
    ind = ROWS - 1  # Start checking from the bottom row

    for y in range(ROWS - 1, -1, -1):
        row = grid[y]
        if BLACK not in row:
            cleared_rows += 1
            # Remove the positions from the locked_positions dictionary
            for x in range(COLUMNS):
                try:
                    del locked_positions[(x, y)]
                except KeyError:
                    continue

    # Shift every row down for each cleared row
    if cleared_rows > 0:
        for key in sorted(list(locked_positions), key=lambda k: k[1])[::-1]:
            x, y = key
            new_y = y + cleared_rows
            if new_y < ROWS:
                locked_positions[(x, new_y)] = locked_positions.pop(key)

    return cleared_rows


def get_score_from_row(grid):
    rows = 0
    for y in range(ROWS - 1, -1, -1):
        row = grid[y]
        if BLACK not in row:
            rows += 1
    return rows


def check_collision(shape, grid):
    for y, row in enumerate(shape.shape):
        for x, col in enumerate(row):
            if col and (shape.x + x < 0 or shape.x + x >= COLUMNS or shape.y + y >= ROWS or grid[shape.y + y][shape.x + x] != BLACK):
                return True
    return False


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH + 200, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.3
    current_score = 0
    locked_positions = {}
    grid = create_grid(locked_positions)

    def speed_increase(current_score, fall_speed):
        if current_score >= 1:
            fall_speed = 0.3 - (current_score // 10) * 0.02
        return fall_speed

    current_piece = Tetromino()
    next_piece = Tetromino()

    running = True
    while running:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if check_collision(current_piece, grid):
                current_piece.y -= 1
                for y, row in enumerate(current_piece.shape):
                    for x, col in enumerate(row):
                        if col:
                            locked_positions[(current_piece.x + x, current_piece.y + y)] = current_piece.color
                current_piece = next_piece
                next_piece = Tetromino()
                if check_collision(current_piece, grid):
                    # if collision true here, game is ended
                    running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if check_collision(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if check_collision(current_piece, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if check_collision(current_piece, grid):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                    if check_collision(current_piece, grid):
                        current_piece.rotate()
                        current_piece.rotate()
                        current_piece.rotate()

        draw_grid(screen, grid)
        hide_previous_shape(screen)
        draw_panel(screen)
        draw_next_shape(screen, next_piece)
        display_score(screen, current_score)

        for y, row in enumerate(current_piece.shape):
            for x, col in enumerate(row):
                if col:
                    pygame.draw.rect(screen, current_piece.color, (
                        current_piece.x * GRID_SIZE + x * GRID_SIZE, current_piece.y * GRID_SIZE + y * GRID_SIZE,
                        GRID_SIZE,
                        GRID_SIZE), 0)

        pygame.display.update()

        rows = get_score_from_row(grid)
        current_score += rows
        update_high_score(current_score)
        fall_speed = speed_increase(current_score, fall_speed)
        if clear_rows(grid, locked_positions):
            grid = create_grid(locked_positions)
        print(fall_speed)

    pygame.quit()


if __name__ == "__main__":
    main()
