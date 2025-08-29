from pygame import *
import socket
import json
from threading import Thread

mixer.init()
sound_wall = mixer.Sound("pop.wav")
sound_paddle = mixer.Sound("pop.wav")


# --- Налаштування ---
WIDTH, HEIGHT = 800, 600
init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")

# --- Сервер ---
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 1222))
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass

def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break

# --- Шрифти ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 36)

# --- Гра ---
game_over = False
winner = None
you_winner = None
my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()

# --- Фон та об'єкти ---
def draw_background():
    screen.fill((25, 25, 25))
    # центральна пунктирна лінія
    for y in range(0, HEIGHT, 40):
        draw.rect(screen, (80, 80, 80), (WIDTH // 2 - 5, y, 10, 20))

def draw_paddle(x, y, color, glow_color):
    paddle = Rect(x, y, 20, 100)
    draw.rect(screen, color, paddle, border_radius=10)
    draw.rect(screen, glow_color, paddle.inflate(8, 8), 3, border_radius=12)

def draw_ball(x, y):
    draw.circle(screen, (255, 255, 200), (x, y), 10)
    draw.circle(screen, (255, 255, 150), (x, y), 18, 2)

# --- Основний цикл ---
while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

    if "countdown" in game_state and game_state["countdown"] > 0:
        screen.fill((0, 0, 0))
        countdown_text = font.Font(None, 72).render(str(game_state["countdown"]), True, (255, 255, 255))
        screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
        display.update()
        continue

    if "winner" in game_state and game_state["winner"] is not None:
        screen.fill((20, 20, 20))
        if you_winner is None:
            you_winner = (game_state["winner"] == my_id)

        text = "Ти переміг!" if you_winner else "Пощастить наступним разом!"
        win_text = font_win.render(text, True, (255, 215, 0))
        text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_text, text_rect)

        restart_text = font_win.render('К - рестарт', True, (255, 215, 0))
        text_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        screen.blit(restart_text, text_rect)

        display.update()
        continue

    if game_state:
        draw_background()

        # Ракетки
        draw_paddle(20, game_state['paddles']['0'], (0, 200, 100), (0, 120, 60))
        draw_paddle(WIDTH - 40, game_state['paddles']['1'], (200, 100, 255), (120, 60, 150))

        # М'ячик
        draw_ball(game_state['ball']['x'], game_state['ball']['y'])

        # Рахунок
        score_text = font_main.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}", True, (255, 255, 255))
        text_rect = score_text.get_rect(center=(WIDTH // 2, 40))
        screen.blit(score_text, text_rect)
        if game_state['sound_event']:
            if game_state['sound_event'] == 'wall_hit':
                sound_wall.play()
            if game_state['sound_event'] == 'platform_hit':
                sound_paddle.play()


    else:
        wating_text = font_main.render(f"Очікування гравців...", True, (255, 255, 255))
        text_rect = wating_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(wating_text, text_rect)

    display.update()
    clock.tick(60)

    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")
