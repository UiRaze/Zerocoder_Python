
import pygame
import random

pygame.init()

screenx = 800
screeny = 600
screen = pygame.display.set_mode((screenx, screeny))
pygame.display.set_caption("animations")

black = (0, 0, 0)

clock = pygame.time.Clock()

fps = 60

dogframes = [pygame.transform.scale(pygame.image.load("234.png"),(70, 70)), pygame.transform.scale(pygame.image.load("234.png"),(70, 70))]
obstacle = (pygame.image.load("234.png"))
obstacle = pygame.transform.scale(obstacle, (80, 80))
obstacles = []
for i in range(5):
    obstacles.append({"x": random.randint(0,685), "y": 500})

font = pygame.font.Font(None, 36)

score = 0

dogx = screenx // 2
dogy = screeny - 100
dogspeed = 4

obstaclespeed = 5

frame_index = 0
animation_speed = 60

frame_timer = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a] and dogx > 0:
        dogx -= dogspeed
    if keys[pygame.K_d] and dogx + 100 < screenx:
     dogx += dogspeed

    frame_index = 1
    frame_timer += clock.get_time()
    if frame_timer >= 1000 // animation_speed:
        frame_index = 0
        frame_timer = 0

    for i in obstacles:
     i["x"] -= obstaclespeed
    if i["x"] < 0:
        i["y"] = screeny - 100
        i["x"] = random.randint(0, 800)
        score += 1



    screen.fill(black)
    current_frame = dogframes[frame_index]
    screen.blit(current_frame, (dogx, dogy))

    for i in obstacles:
        screen.blit(obstacle, (i["x"], i["y"]))

    for i in obstacles:
     if dogx < i["x"] + 70 and dogx + 70 > i["x"] and dogy < i["y"] + 70 and dogy + 140 > i["y"]:
        running = False

    score_text = font.render(f"score: {score}", True, (255,255,255))
    screen.blit(score_text,( 10, 10))


    clock.tick(fps)
    pygame.display.flip()