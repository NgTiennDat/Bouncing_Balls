import pygame
import numpy as np
import math
import random

class Ball:
    def __init__(self, position, velocity):
        self.pos = np.array(position, dtype=np.float64)
        self.v = np.array(velocity, dtype=np.float64)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.is_in = True

def is_ball_in_arc(ball_pos, CIRCLE_CENTER, start_angle, end_angle):
    dx = ball_pos[0] - CIRCLE_CENTER[0]
    dy = ball_pos[1] - CIRCLE_CENTER[1]
    ball_angle = math.atan2(dy, dx)
    start_angle = start_angle % (2 * math.pi)
    end_angle = end_angle % (2 * math.pi)
    if start_angle > end_angle:
        end_angle += 2 * math.pi
    if start_angle <= ball_angle <= end_angle or (start_angle <= ball_angle + 2 * math.pi <= end_angle):
        return True

def draw_arc(window, center, radius, start_angle, end_angle):
    p1 = center + (radius + 1000) * np.array([math.cos(start_angle), math.sin(start_angle)])
    p2 = center + (radius + 1000) * np.array([math.cos(end_angle), math.sin(end_angle)])

    pygame.draw.polygon(window, BLACK, [center, p1, p2], 0)

pygame.init()
pygame.mixer.init()

bounce_sound = pygame.mixer.Sound("bounce.mp3")
remove_sound = pygame.mixer.Sound("remove.mp3")

WIDTH = 1000
HEIGHT = 1000
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Balls")
clock = pygame.time.Clock()
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
CIRCLE_CENTER = np.array([WIDTH / 2, HEIGHT / 2], dtype=np.float64)
CIRCLE_RADIUS = 150
BALL_RADIUS = 5
ball_pos = np.array([WIDTH / 2, HEIGHT / 2 - 130], dtype=np.float64)
GRAVITY = 0.2
ball_vel = np.array([0,0], dtype=np.float64)
arc_degrees = 60
start_angle = math.radians(-arc_degrees/2)
end_angle = math.radians(arc_degrees/2)
spinning_speed = 0.01
balls = [Ball(ball_pos, ball_vel)]
score = 0
font = pygame.font.SysFont("Arial", 36)
start_time = pygame.time.get_ticks()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    start_angle += spinning_speed
    end_angle += spinning_speed

    current_time = (pygame.time.get_ticks() - start_time) // 1000
    if current_time % 3 == 0 and current_time > 0:
        spinning_speed += 0.0001
        arc_degrees = max(10, arc_degrees - 0.1)
        start_angle = start_angle
        end_angle = start_angle + math.radians(arc_degrees)

    if arc_degrees <= 10:
        window.fill(BLACK)
        game_over_text = font.render("Game Over!", True, RED)
        score_text = font.render(f"Score: {score}", True, ORANGE)
        window.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
        window.blit(score_text, (WIDTH // 2 - 100, HEIGHT // 2 + 10))
        pygame.display.flip()
        pygame.time.delay(3000)  # Dừng màn hình trong 3 giây
        running = False
        break

    for ball in balls:
        if(ball.pos[1] > HEIGHT or ball.pos[0] < 0 or ball.pos[0] > WIDTH or ball.pos[1] < 0):
            balls.remove(ball)
            balls.append(Ball(position=[WIDTH // 2, HEIGHT // 2 - 120], velocity=[random.uniform(-4,4), random.uniform(-1,1)]))
            balls.append(Ball(position=[WIDTH // 2, HEIGHT // 2 - 120], velocity=[random.uniform(-4,4), random.uniform(-1,1)]))
        ball.v[1] += GRAVITY
        ball.pos[0] += ball.v[0]
        ball.pos[1] += ball.v[1]
        dist = np.linalg.norm(ball.pos - CIRCLE_CENTER)

        if dist + BALL_RADIUS > CIRCLE_RADIUS:
            if is_ball_in_arc(ball.pos, CIRCLE_CENTER, start_angle, end_angle):
                score = score + 1
                ball.is_in = False
            if ball.is_in:
                d = ball.pos - CIRCLE_CENTER
                d_unit = d/np.linalg.norm(d)
                ball.pos = CIRCLE_CENTER + (CIRCLE_RADIUS - BALL_RADIUS) * d_unit
                t = np.array([-d[1], d[0]], dtype=np.float64)
                proj_v_t = (np.dot(ball.v, t)/np.dot(t, t)) * t
                ball.v = 2 * proj_v_t - ball.v
                ball.v += t * spinning_speed # v = rw (w: spinning speed)
                pygame.mixer.Sound.play(bounce_sound)

    window.fill(BLACK)
    pygame.draw.circle(window, ORANGE, CIRCLE_CENTER, CIRCLE_RADIUS, 3)
    draw_arc(window, CIRCLE_CENTER, CIRCLE_RADIUS, start_angle, end_angle)
    for ball in balls:
        pygame.draw.circle(window, ball.color, ball.pos, BALL_RADIUS)

    score_text = font.render(str(score), True, ORANGE)
    window.blit(score_text, (700, 0))

    time_text = font.render(str(current_time), True, ORANGE)
    window.blit(time_text, (0, 0))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()