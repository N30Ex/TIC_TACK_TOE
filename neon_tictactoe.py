import pygame
import sys
import random
import json
import os

# --- Init ---
pygame.init()
WIDTH, HEIGHT = 600, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🕹️ Neon Arcade Tic-Tac-Toe")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
NEON_ORANGE = (255, 165, 0)
GLOW = (255, 140, 0)
WHITE = (255, 255, 255)
FPS = 60

# Fonts
FONT = pygame.font.SysFont("Courier", 60, bold=True)
SMALL_FONT = pygame.font.SysFont("Courier", 30, bold=True)

# Sound and Music
try:
    pygame.mixer.music.load("arcade_theme.mp3")
    pygame.mixer.music.play(-1)
except:
    pass

try:
    click_sound = pygame.mixer.Sound("click.wav")
    win_sound = pygame.mixer.Sound("win.wav")
except:
    click_sound = None
    win_sound = None

# Scores
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

# Main menu
menu_active = True

def draw_menu():
    SCREEN.fill(BLACK)
    title = FONT.render("Neon Tic-Tac-Toe", True, NEON_ORANGE)
    SCREEN.blit(title, (WIDTH//2 - title.get_width()//2, 150))

    pvp = SMALL_FONT.render("1. Player vs Player", True, WHITE)
    pvc = SMALL_FONT.render("2. Player vs CPU", True, WHITE)
    quit_game = SMALL_FONT.render("Q. Quit", True, WHITE)

    SCREEN.blit(pvp, (WIDTH//2 - pvp.get_width()//2, 300))
    SCREEN.blit(pvc, (WIDTH//2 - pvc.get_width()//2, 350))
    SCREEN.blit(quit_game, (WIDTH//2 - quit_game.get_width()//2, 400))

    pygame.display.flip()

def draw_particles():
    for p in particles:
        pygame.draw.circle(SCREEN, NEON_ORANGE, (int(p["x"]), int(p["y"])), p["r"])
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["r"] = max(0, p["r"] - 0.1)
    particles[:] = [p for p in particles if p["r"] > 0]

def spawn_particles(x, y):
    for _ in range(20):
        particles.append({
            "x": x, "y": y,
            "vx": random.uniform(-2, 2),
            "vy": random.uniform(-2, 2),
            "r": random.randint(2, 5)
        })

def draw_board():
    SCREEN.fill(BLACK)

    for i in range(1, 3):
        pygame.draw.line(SCREEN, GLOW, (0, i * 200 + 100), (600, i * 200 + 100), 5)
        pygame.draw.line(SCREEN, GLOW, (i * 200, 100), (i * 200, 700), 5)

    for i, val in enumerate(board):
        x = (i % 3) * 200 + 100
        y = (i // 3) * 200 + 200
        if val != " ":
            text = FONT.render(val, True, NEON_ORANGE)
            SCREEN.blit(text, (x - text.get_width()//2, y - text.get_height()//2))

    score_text = SMALL_FONT.render(f"X:{scores['X']}  O:{scores['O']}  Draws:{scores['Draws']}", True, WHITE)
    SCREEN.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 580))

    if game_over:
        msg = f"{winner} wins!" if winner else "Draw!"
    else:
        msg = f"{current_player}'s Turn"
    status = SMALL_FONT.render(msg, True, WHITE)
    SCREEN.blit(status, (WIDTH//2 - status.get_width()//2, 650))

    draw_particles()

def check_winner():
    global winner, game_over
    combos = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),
              (1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b,c in combos:
        if board[a] == board[b] == board[c] != " ":
            winner = board[a]
            game_over = True
            scores[winner] += 1
            save_scores()
            spawn_particles(300, 400)
            if win_sound: win_sound.play()
            return
    if " " not in board:
        game_over = True
        scores["Draws"] += 1
        save_scores()

def reset_game():
    global board, current_player, game_over, winner
    board = [" " for _ in range(9)]
    current_player = "X"
    game_over = False
    winner = None

def handle_click(pos):
    global current_player
    if game_over:
        return
    x, y = pos
    if y < 100: return
    row = (y - 100) // 200
    col = x // 200
    idx = row * 3 + col
    if board[idx] == " ":
        board[idx] = current_player
        if click_sound: click_sound.play()
        check_winner()
        if not game_over:
            current_player = "O" if current_player == "X" else "X"

def cpu_move():
    empty = [i for i, v in enumerate(board) if v == " "]
    for move in empty:
        copy = board[:]
        copy[move] = "O"
        if winner_check(copy, "O"):
            return move
    for move in empty:
        copy = board[:]
        copy[move] = "X"
        if winner_check(copy, "X"):
            return move
    return random.choice(empty)

def winner_check(b, p):
    return any(b[a] == b[b_] == b[c] == p for a,b_,c in [
        (0,1,2),(3,4,5),(6,7,8),(0,3,6),
        (1,4,7),(2,5,8),(0,4,8),(2,4,6)
    ])

# --- Game Loop ---
running = True
while running:
    clock.tick(FPS)
    if menu_active:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
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
    else:
        draw_board()
        pygame.display.flip()

        if mode == "PVC" and current_player == "O" and not game_over:
            pygame.time.wait(500)
            move = cpu_move()
            board[move] = "O"
            if click_sound: click_sound.play()
            check_winner()
            if not game_over:
                current_player = "X"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(event.pos)
            elif event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_RETURN:
                    reset_game()
            elif event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_ESCAPE:
                    menu_active = True

pygame.quit()
sys.exit()
