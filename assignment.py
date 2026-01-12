'''
-----------------------------------------------------------------------------
Program Name: (never put your personal name or information on the Internet)
Program Description:

--------------------------------------------------------------------------
References:
(put a link to your reference here but also add a comment in the code below where you used the reference)

-----------------------------------------------------------------------------

Additional Libraries/Extensions:

(put a list of required extensions so that the user knows that they need to download extra features)

---------------------------------------------------------------------------

Known bugs:

(put a list of known bugs here, if you have any)

----------------------------------------------------------------------------


Program Reflection:
I think this project deserves a level XXXXXX because ...

 Level 3 Requirements Met:
• 
•  
•  
•  
•  
• 

Features Added Beyond Level 3 Requirements:
• 
•  
•  
•  
•  
• 
-----------------------------------------------------------------------------
'''
import pygame
import sys

pygame.init()
#hello
WIDTH, HEIGHT = 640, 200
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hearts Health Bar - Demo")
CLOCK = pygame.time.Clock()33

# Configuration
MAX_HEALTH = 5
health = MAX_HEALTH
HEART_SIZE = 48
GAP = 12
MARGIN = 20

FONT = pygame.font.SysFont(None, 22)
BIG_FONT = pygame.font.SysFont(None, 32)

# Colors
BG = (30, 30, 40)
HEART_RED = (220, 30, 60)
HEART_GREY = (120, 120, 120)
TEXT_COLOR = (220, 220, 220)

2
def draw_heart(surface, x, y, size, color, outline=False):
    # radius for the two top circles
    r = size // 4
    left_center = (int(x - r), int(y - r))
    right_center = (int(x + r), int(y - r))

    # polygon points for the bottom part
    p1 = (int(x - size // 2), int(y - r))
    p2 = (int(x + size // 2), int(y - r))
    p3 = (int(x), int(y + size // 2))

    if not outline:
        pygame.draw.circle(surface, color, left_center, r)
        pygame.draw.circle(surface, color, right_center, r)
        pygame.draw.polygon(surface, color, [p1, p2, p3])
    else:
        width = max(2, size // 16)
        pygame.draw.circle(surface, color, left_center, r, width)
        pygame.draw.circle(surface, color, right_center, r, width)
        pygame.draw.polygon(surface, color, [p1, p2, p3], width)


def draw_health_bar(surface, current_health):
    y = HEIGHT // 2
    for i in range(MAX_HEALTH):
        cx = MARGIN + i * (HEART_SIZE + GAP) + HEART_SIZE // 2
        if i < current_health:
            draw_heart(surface, cx, y, HEART_SIZE, HEART_RED, outline=False)
        else:
            # empty heart (outline + dim fill)
            draw_heart(surface, cx, y, HEART_SIZE, HEART_GREY, outline=True)


def draw_ui(surface, current_health):
    # instructions
    lines = [
        "Controls: D = damage, H = heal, R = reset to full, ESC = quit",
        f"Health: {current_health} / {MAX_HEALTH}",
    ]
    y = 10
    for line in lines:
        txt = FONT.render(line, True, TEXT_COLOR)
        surface.blit(txt, (MARGIN, y))
        y += txt.get_height() + 6

    # small title
    title = BIG_FONT.render("Player Health", True, TEXT_COLOR)
    surface.blit(title, (WIDTH - title.get_width() - MARGIN, 10))


def main():
    global health
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    health = max(0, health - 1)
                elif event.key == pygame.K_h:
                    health = min(MAX_HEALTH, health + 1)
                elif event.key == pygame.K_r:
                    health = MAX_HEALTH

        SCREEN.fill(BG)
        draw_ui(SCREEN, health)
        draw_health_bar(SCREEN, health)

        pygame.display.flip()
        CLOCK.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

