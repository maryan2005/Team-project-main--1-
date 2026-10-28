
import pygame
import random

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 500
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 20
BOARD_X = 100
BOARD_Y = 60
FPS = 25
SHAPE_SIZE = 4
EMPTY_CELL = 0

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

COLORS = (
    BLACK,
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
)

FIGURES = (
    ((1, 5, 9, 13), (4, 5, 6, 7)),
    ((4, 5, 9, 10), (2, 6, 5, 9)),
    ((6, 7, 9, 10), (1, 5, 6, 10)),
    ((1, 2, 5, 9), (0, 4, 5, 6), (1, 5, 9, 8), (4, 5, 6, 10)),
    ((1, 2, 6, 10), (5, 6, 7, 9), (2, 6, 10, 11), (3, 5, 6, 7)),
    ((1, 4, 5, 6), (1, 4, 5, 9), (4, 5, 6, 9), (1, 5, 6, 9)),
    ((1, 2, 5, 6),),
)


class TetrisGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Calibri", 25, True, False)
        self.game_over_font = pygame.font.SysFont(
            "Calibri", 55, True, False
        )
        self.reset_game()

    def reset_game(self):
        self.board = [
            [EMPTY_CELL for _ in range(BOARD_WIDTH)]
            for _ in range(BOARD_HEIGHT)
        ]
        self.score = 0
        self.state = "playing"
        self.piece_type = 0
        self.piece_color = 0
        self.rotation = 0
        self.piece_x = 3
        self.piece_y = 0
        self.spawn_piece()

    def spawn_piece(self):
        self.piece_type = random.randrange(len(FIGURES))
        self.piece_color = random.randrange(1, len(COLORS))
        self.rotation = 0
        self.piece_x = 3
        self.piece_y = 0

        if self.intersects(self.current_figure()):
            self.state = "gameover"

    def current_figure(self):
        return FIGURES[self.piece_type][self.rotation]

    def figure_cells(self, figure=None, x=None, y=None):
        if figure is None:
            figure = self.current_figure()
        if x is None:
            x = self.piece_x
        if y is None:
            y = self.piece_y

        cells = []

        for position in figure:
            row = position // SHAPE_SIZE
            column = position % SHAPE_SIZE
            cells.append((x + column, y + row))

        return cells

    def intersects(self, figure, dx=0, dy=0):
        for column, row in self.figure_cells(
            figure,
            self.piece_x + dx,
            self.piece_y + dy
        ):
            if column < 0 or column >= BOARD_WIDTH:
                return True

            if row >= BOARD_HEIGHT:
                return True

            if row >= 0 and self.board[row][column] != EMPTY_CELL:
                return True

        return False

    def move_side(self, direction):
        if not self.intersects(self.current_figure(), dx=direction):
            self.piece_x += direction

    def move_down(self):
        if not self.intersects(self.current_figure(), dy=1):
            self.piece_y += 1
        else:
            self.lock_piece()

    def rotate_piece(self):
        next_rotation = (self.rotation + 1) % len(
            FIGURES[self.piece_type]
        )

        if not self.intersects(FIGURES[self.piece_type][next_rotation]):
            self.rotation = next_rotation

    def hard_drop(self):
        distance = 0

        while not self.intersects(self.current_figure(), dy=1):
            self.piece_y += 1
            distance += 1

        self.update_score(distance * 2)
        self.lock_piece()

    def lock_piece(self):
        for column, row in self.figure_cells():
            if row < 0:
                self.state = "gameover"
                return

            self.board[row][column] = self.piece_color

        self.clear_lines()
        self.spawn_piece()

    def is_row_full(self, row):
        return all(
            cell != EMPTY_CELL
            for cell in self.board[row]
        )

    def remove_row(self, row):
        del self.board[row]
        self.board.insert(
            0,
            [EMPTY_CELL for _ in range(BOARD_WIDTH)]
        )

    def clear_lines(self):
        cleared_lines = 0
        row = BOARD_HEIGHT - 1

        while row >= 0:
            if self.is_row_full(row):
                self.remove_row(row)
                cleared_lines += 1
            else:
                row -= 1

        self.update_score(self.calculate_line_score(cleared_lines))

    def calculate_line_score(self, lines):
        return lines ** 2

    def update_score(self, points):
        self.score += points

    def draw_board(self):
        self.screen.fill(WHITE)

        for row in range(BOARD_HEIGHT):
            for column in range(BOARD_WIDTH):
                x = BOARD_X + CELL_SIZE * column
                y = BOARD_Y + CELL_SIZE * row

                pygame.draw.rect(
                    self.screen,
                    GRAY,
                    (x, y, CELL_SIZE, CELL_SIZE),
                    1
                )

                color_index = self.board[row][column]

                if color_index != EMPTY_CELL:
                    pygame.draw.rect(
                        self.screen,
                        COLORS[color_index],
                        (
                            x + 1,
                            y + 1,
                            CELL_SIZE - 2,
                            CELL_SIZE - 2
                        )
                    )

    def draw_piece(self):
        for column, row in self.figure_cells():
            if row >= 0:
                x = BOARD_X + CELL_SIZE * column
                y = BOARD_Y + CELL_SIZE * row

                pygame.draw.rect(
                    self.screen,
                    COLORS[self.piece_color],
                    (
                        x + 1,
                        y + 1,
                        CELL_SIZE - 2,
                        CELL_SIZE - 2
                    )
                )

    def draw(self):
        self.draw_board()

        if self.state == "playing":
            self.draw_piece()

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            BLACK
        )
        self.screen.blit(score_text, (0, 0))

        if self.state == "gameover":
            game_over_text = self.game_over_font.render(
                "Game Over",
                True,
                (255, 125, 0)
            )
            quit_text = self.font.render(
                "Press R to Restart or Q to Quit",
                True,
                BLACK
            )

            self.screen.blit(game_over_text, (35, 200))
            self.screen.blit(quit_text, (25, 270))

        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False

        if event.type != pygame.KEYDOWN:
            return True

        if event.key == pygame.K_q:
            return False

        if self.state == "gameover":
            if event.key == pygame.K_r:
                self.reset_game()
            return True

        if event.key == pygame.K_LEFT:
            self.move_side(-1)
        elif event.key == pygame.K_RIGHT:
            self.move_side(1)
        elif event.key == pygame.K_DOWN:
            self.move_down()
        elif event.key == pygame.K_UP:
            self.rotate_piece()
        elif event.key == pygame.K_SPACE:
            self.hard_drop()

        return True

    def run(self):
        running = True
        fall_timer = 0
        fall_interval = 500

        while running:
            elapsed_time = self.clock.tick(FPS)
            fall_timer += elapsed_time

            for event in pygame.event.get():
                running = self.handle_event(event) and running

            if (
                running
                and self.state == "playing"
                and fall_timer >= fall_interval
            ):
                self.move_down()
                fall_timer = 0

            if running:
                self.draw()

        pygame.quit()


if __name__ == "__main__":
    game = TetrisGame()
    game.run()
