import pygame
import sys
import random
import json
import os

pygame.init()
WIDTH, HEIGHT = 600, 700
TOP_MARGIN = 100  # Space at top for scores
GRID_SIZE = 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🕹️ Neon Arcade Tic-Tac-Toe")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
NEON_ORANGE = (255, 165, 0)
GLOW = (255, 140, 0)
WHITE = (255, 255, 255)

# Fonts
# Fonts
FONT = pygame.font.SysFont("Courier", 60, bold=True)        # For X and O
SMALL_FONT = pygame.font.SysFont("Courier", 20, bold=True)  # For status and scores


# Music
try:
    pygame.mixer.music.load("arcade_theme.mp3")
    pygame.mixer.music.play(-1)
except:
    pass

# Score
score_file = "scores.json"
scores = {"X": 0, "O": 0, "Draws": 0}
if os.path.exists(score_file):
    with open(score_file, "r") as f:
        scores = json.load(f)

def save_scores():
    with open(score_file, "w") as f:
        json.dump(scores, f)

# Game state
board = [" " for _ in range(9)]
current_player = "X"
mode = "PVP"
game_over = False
winner = None
particles = []
menu_active = True

def draw_menu():
    SCREEN.fill(BLACK)
    title = FONT.render("NEON TIC-TAC-TOE", True, NEON_ORANGE)
    pvp = SMALL_FONT.render("1. Player vs Player", True, WHITE)
    pvc = SMALL_FONT.render("2. Player vs CPU", True, WHITE)
    quit_game = SMALL_FONT.render("Q. Quit", True, WHITE)
    SCREEN.blit(title, title.get_rect(center=(WIDTH // 2, 150)))
    SCREEN.blit(pvp, pvp.get_rect(center=(WIDTH // 2, 250)))
    SCREEN.blit(pvc, pvc.get_rect(center=(WIDTH // 2, 300)))
    SCREEN.blit(quit_game, quit_game.get_rect(center=(WIDTH // 2, 350)))
    pygame.display.flip()

def draw_particles():
    for p in particles[:]:
        p["x"] += p["dx"]
        p["y"] += p["dy"]
        p["life"] -= 1
        p["radius"] *= 0.97
        if p["life"] <= 0:
            particles.remove(p)
        else:
            pygame.draw.circle(SCREEN, NEON_ORANGE, (int(p["x"]), int(p["y"])), int(p["radius"]))

def spawn_particles(x, y):
    for _ in range(20):
        particles.append({
            "x": x,
            "y": y + TOP_MARGIN,
            "radius": random.randint(2, 5),
            "dx": random.uniform(-2, 2),
            "dy": random.uniform(-2, 2),
            "life": random.randint(30, 60)
        })

def draw_board():
    SCREEN.fill(BLACK)

    # Draw score/status at the top
    status_text = SMALL_FONT.render(
        f"Turn: {current_player}   |   Wins - X: {scores['X']} O: {scores['O']}   |   Draws: {scores['Draws']}",
        True, NEON_ORANGE
    )
    SCREEN.blit(status_text, (WIDTH // 2 - status_text.get_width() // 2, 10))

    # 🔻 New section: Display winner message if game is over
    if game_over:
        if winner == "Draw":
            result_text = SMALL_FONT.render("It's a Draw!", True, NEON_ORANGE)
        else:
            result_text = SMALL_FONT.render(f"{winner} Wins!", True, NEON_ORANGE)
        SCREEN.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, 45))

    # Draw the grid
    for i in range(1, 3):
        pygame.draw.line(SCREEN, GLOW, (0, i * 200 + TOP_MARGIN), (WIDTH, i * 200 + TOP_MARGIN), 5)
        pygame.draw.line(SCREEN, GLOW, (i * 200, TOP_MARGIN), (i * 200, TOP_MARGIN + GRID_SIZE), 5)

    # Draw X and O in cells
    for i, mark in enumerate(board):
        row = i // 3
        col = i % 3
        if mark != " ":
            text = FONT.render(mark, True, NEON_ORANGE)
            rect = text.get_rect(center=(col * 200 + 100, row * 200 + 100 + TOP_MARGIN))
            SCREEN.blit(text, rect)

    draw_particles()


def check_winner():
    global game_over, winner
    combos = [(0,1,2), (3,4,5), (6,7,8),
              (0,3,6), (1,4,7), (2,5,8),
              (0,4,8), (2,4,6)]
    for a, b, c in combos:
        if board[a] == board[b] == board[c] and board[a] != " ":
            game_over = True
            winner = board[a]
            scores[winner] += 1
            for i in (a, b, c):
                col = i % 3
                row = i // 3
                spawn_particles(col * 200 + 100, row * 200 + 100)
            save_scores()
            return
    if " " not in board:
        game_over = True
        winner = "Draw"
        scores["Draws"] += 1
        save_scores()

def reset_game():
    global board, current_player, game_over, winner, particles
    board = [" " for _ in range(9)]
    current_player = "X"
    game_over = False
    winner = None
    particles = []

def handle_click(pos):
    global current_player, game_over
    x, y = pos
    if y < TOP_MARGIN or game_over:
        return
    row = (y - TOP_MARGIN) // 200
    col = x // 200
    idx = row * 3 + col
    if board[idx] == " ":
        board[idx] = current_player
        check_winner()
        if not game_over:
            current_player = "O" if current_player == "X" else "X"

def cpu_move():
    global current_player
    for i in range(9):
        if board[i] == " ":
            temp = board[:]
            temp[i] = current_player
            if winner_check(temp, current_player):
                board[i] = current_player
                check_winner()
                current_player = "X"
                return
    opponent = "X"
    for i in range(9):
        if board[i] == " ":
            temp = board[:]
            temp[i] = opponent
            if winner_check(temp, opponent):
                board[i] = current_player
                check_winner()
                current_player = "X"
                return
    while True:
        move = random.randint(0, 8)
        if board[move] == " ":
            board[move] = current_player
            check_winner()
            current_player = "X"
            break

def winner_check(b, p):
    combos = [(0,1,2), (3,4,5), (6,7,8),
              (0,3,6), (1,4,7), (2,5,8),
              (0,4,8), (2,4,6)]
    return any(b[a] == b[b_] == b[c] == p for a, b_, c in combos)

# Main Loop
running = True
while running:
    if menu_active:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = "PVP"
                    menu_active = False
                    reset_game()
                elif event.key == pygame.K_2:
                    mode = "PVC"
                    menu_active = False
                    reset_game()
                elif event.key == pygame.K_q:
                    running = False
        continue

    draw_board()
    if not game_over and mode == "PVC" and current_player == "O":
        pygame.time.delay(500)
        cpu_move()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            handle_click(pygame.mouse.get_pos())
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                menu_active = True
            if event.key == pygame.K_RETURN and game_over:
                reset_game()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
