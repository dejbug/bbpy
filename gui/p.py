from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Example file showing a circle moving on screen
import pygame

# pygame setup
pygame.init()

# print(pygame.font.get_fonts())
defaultFontName = pygame.font.get_default_font()
font = pygame.font.SysFont(defaultFontName, 64)
text = font.render("hello pygame!", True, 'black', None)

screen = pygame.display.set_mode((1280, 720), flags = pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

screen.fill('white')

while running:
    pygame.display.flip()

    e = pygame.event.wait(1000)
    if e.type == pygame.NOEVENT:
        print('no event')
    elif e.type == pygame.QUIT:
        running = False
    elif e.type == pygame.VIDEORESIZE:
        print('resized', screen.get_width(), screen.get_height())
    elif e.type == pygame.KEYDOWN:
        print(e.key)
        if e.key == pygame.K_ESCAPE:
            running = False
        else:
            screen.fill('white')
            text = font.render('hello: ' + str(e.key), True, 'black', None)
            screen.blit(text, (10, 10))

    continue

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            print('resized', screen.get_width(), screen.get_height())

    screen.fill('white')

    pygame.draw.circle(screen, 'red', player_pos, 40)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False

    # text = font.render(, True, 'black', None)


    if keys[pygame.K_w]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_s]:
        player_pos.y += 300 * dt
    if keys[pygame.K_a]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_d]:
        player_pos.x += 300 * dt

    screen.blit(text, (100, 100))

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()