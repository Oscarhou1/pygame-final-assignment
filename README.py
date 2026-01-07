# Pygame Project
## This is where you will submit your project

1. Complete the project plan BEFORE coding begins
2. You are required to commit and push your changes to your repository minimum at the *end of every class that you work on your assignment* with your current code **even if you have not completed it**
3. If you have additional resources such as images, organize them into folders.
import pygame
import random
from pathlib import Path

pygame.init()
pygame.mixer.init()
# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60
ASSET_DIR = Path(".")  # change to Path("assets") if you keep images in an assets folder
HIGHSCORE_FILE = ASSET_DIR / "highscore.txt"

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 80, 80)
BLUE = (80, 80, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
pygame.mixer.music.load("game-music-loop-7-145285 (1).mp3")
pygame.mixer.music.play(-1)  # -1 = loop forever

# --- Helper functions for highscore ---
def get_highscore():
    try:
        if not HIGHSCORE_FILE.exists():
            HIGHSCORE_FILE.write_text("0")
            return 0
        return int(HIGHSCORE_FILE.read_text().strip() or 0)
    except Exception:
        return 0

def save_highscore(score):
    try:
        if score > get_highscore():
            HIGHSCORE_FILE.write_text(str(score))
    except Exception:
        pass

# --- Setup window ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Easy Shooter (Refactor)")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small = pygame.font.SysFont(None, 28)

# Load background if available, else solid fill
bg_path = ASSET_DIR / "backgroundmy.jpg"
if bg_path.exists():
    bg_img = pygame.image.load(bg_path).convert()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
else:
    bg_img = None

# --- Game objects (procedural, no classes) ---

def init_player():
    """Return a player dict with image, rect and state."""
    # Attempt to load a tower image. Place 'gun tower.png' in ASSET_DIR or same folder as script.
    tower_path = ASSET_DIR / "gun tower.png"
    if tower_path.exists():
        try:
            img = pygame.image.load(tower_path).convert_alpha()
            # user scaled to 120x120 in their last paste — keep that size
            img = pygame.transform.scale(img, (120, 120))
        except Exception:
            img = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.rect(img, GREEN, (0, 0, 60, 60))
    else:
        img = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.rect(img, GREEN, (0, 0, 60, 60))

    rect = img.get_rect(midbottom=(WIDTH // 2, HEIGHT - 20))
    return {
        "image": img,
        "rect": rect,
        "shoot_delay": 12,
        "shoot_timer": 0,
        "lives": 5,
        "bombs": 3,
        "double_until": 0,
        "shield_until": 0,
    }

def player_update(player):
    mx, _ = pygame.mouse.get_pos()
    player["rect"].centerx = mx
    player["rect"].clamp_ip(screen.get_rect())
    player["shoot_timer"] += 1

def player_can_shoot(player):
    return player["shoot_timer"] > player["shoot_delay"]

def player_shoot(player):
    player["shoot_timer"] = 0
    new_bullets = []
    # center bullet
    b_surf = pygame.Surface((10, 18))
    b_surf.fill(YELLOW)
    b_rect = b_surf.get_rect(midbottom=(player["rect"].centerx, player["rect"].top))
    new_bullets.append({"image": b_surf, "rect": b_rect, "speed": -10})
    # double-shot if active
    if pygame.time.get_ticks() < player["double_until"]:
        left_bsurf = pygame.Surface((10, 18))
        left_bsurf.fill(YELLOW)
        r1 = left_bsurf.get_rect(midbottom=(player["rect"].centerx - 18, player["rect"].top))
        right_bsurf = pygame.Surface((10, 18))
        right_bsurf.fill(YELLOW)
        r2 = right_bsurf.get_rect(midbottom=(player["rect"].centerx + 18, player["rect"].top))
        new_bullets.append({"image": left_bsurf, "rect": r1, "speed": -10})
        new_bullets.append({"image": right_bsurf, "rect": r2, "speed": -10})
    return new_bullets

def player_has_shield(player):
    return pygame.time.get_ticks() < player["shield_until"]

def player_activate_power(player, kind, duration_ms=5000):
    now = pygame.time.get_ticks()
    if kind == "double":
        player["double_until"] = max(player["double_until"], now + duration_ms)
    elif kind == "shield":
        player["shield_until"] = max(player["shield_until"], now + duration_ms)
    elif kind == "life":
        player["lives"] += 1

def make_enemy(x, y, size=60, is_boss=False):
    surf = pygame.Surface((size, size))
    surf.fill(RED if not is_boss else (200, 50, 50))
    rect = surf.get_rect(topleft=(x, y))
    return {
        "image": surf,
        "rect": rect,
        "speed_y": 2 if not is_boss else 1,
        "health": 1 if not is_boss else 50,
        "is_boss": is_boss,
        "dir": 1,
        "move_timer": 0,
        "size": size,
    }

def update_enemy(en):
    if en["is_boss"]:
        if en["rect"].top < 40:
            en["rect"].y += 2
        else:
            en["rect"].x += en["dir"] * 3
            if en["rect"].left <= 0 or en["rect"].right >= WIDTH:
                en["dir"] *= -1
    else:
        en["rect"].y += en["speed_y"]

def make_powerup(x, y, kind):
    surf = pygame.Surface((30, 30))
    if kind == "double":
        surf.fill((180, 30, 180))
    elif kind == "shield":
        surf.fill(BLUE)
    else:
        surf.fill((30, 200, 30))
    rect = surf.get_rect(topleft=(x, y))
    return {"image": surf, "rect": rect, "kind": kind, "speed": 3}

# --- Collections (replacing sprite groups) ---
player = init_player()
bullets = []   # list of bullet dicts
enemies = []   # list of enemy dicts
powerups = []  # list of powerup dicts

# Game state
score = 0
boss_active = False
boss_spawned = False

# --- Menus / Screens ---
def draw_text(surf, txt, fnt, color, x, y):
    surf.blit(fnt.render(txt, True, color), (x, y))

def menu_screen():
    while True:
        clock.tick(FPS)
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill(BLACK)
        draw_text(screen, "ULTIMATE EASY SHOOTER", font, WHITE, 140, 180)
        draw_text(screen, "Mouse to Move  |  Auto Shoot  |  B = Bomb", small, WHITE, 220, 250)
        draw_text(screen, "Press ENTER to Start", small, WHITE, 300, 300)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                return True

def game_over_screen(final_score):
    save_highscore(final_score)
    while True:
        clock.tick(FPS)
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill(BLACK)
        draw_text(screen, "GAME OVER", font, WHITE, 310, 200)
        draw_text(screen, f"Final Score: {final_score}", small, WHITE, 340, 270)
        draw_text(screen, "Press ENTER for Menu", small, WHITE, 300, 320)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                return True

# --- Main game logic ---
def run_game():
    global score, boss_active, boss_spawned, player, bullets, enemies, powerups
    score = 0
    boss_active = boss_spawned = False

    # reset collections and player state
    bullets = []
    enemies = []
    powerups = []
    player = init_player()

    running = True
    spawn_event = pygame.USEREVENT + 1
    pygame.time.set_timer(spawn_event, 700)  # spawn attempt every 700ms

    while running:
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return False
            if e.type == spawn_event:
                # spawn enemies if not boss
                if not boss_active and random.randint(1, 4) == 1:
                    x = random.randint(0, WIDTH - 60)
                    en = make_enemy(x, -60)
                    enemies.append(en)
                # random chance to spawn a bigger enemy sometimes
                if not boss_active and random.randint(1, 30) == 1:
                    x = random.randint(0, WIDTH - 120)
                    en = make_enemy(x, -120, size=100)
                    enemies.append(en)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_b and player["bombs"] > 0:
                    player["bombs"] -= 1
                    # bomb effect: remove all non-boss enemies
                    killed = [en for en in enemies if not en["is_boss"]]
                    for en in killed:
                        enemies.remove(en)
                        score += 1
            if e.type == pygame.MOUSEBUTTONDOWN:
                # optional: use mouse to place or trigger something
                pass

        # spawn boss when score threshold reached
        if score >= 30 and not boss_spawned:
            boss = make_enemy(WIDTH//2 - 200, -120, size=400, is_boss=True)
            enemies.append(boss)
            boss_active = boss_spawned = True

        # Player auto-shoot
        player_update(player)
        if player_can_shoot(player):
            new_b = player_shoot(player)
            bullets.extend(new_b)

        # Update bullets
        for b in list(bullets):
            b["rect"].y += b["speed"]
            if b["rect"].bottom < 0:
                bullets.remove(b)

        # Update enemies
        for en in list(enemies):
            update_enemy(en)
            if not en["is_boss"] and en["rect"].top > HEIGHT:
                enemies.remove(en)
                if not player_has_shield(player):
                    player["lives"] -= 1

        # Update powerups
        for p in list(powerups):
            p["rect"].y += p["speed"]
            if p["rect"].top > HEIGHT:
                powerups.remove(p)

        # Collisions: bullets -> enemies
        bullets_to_remove = set()
        enemies_to_remove = set()
        for b in list(bullets):
            for en in list(enemies):
                if b["rect"].colliderect(en["rect"]):
                    bullets_to_remove.add(id(b))  # use id to identify object
                    # reduce enemy health
                    en["health"] -= 1
                    if en["health"] <= 0:
                        # drop chance for powerup
                        if not en["is_boss"] and random.randint(1, 5) == 1:
                            kind = random.choice(["double", "shield", "life"])
                            p = make_powerup(en["rect"].x, en["rect"].y, kind)
                            powerups.append(p)
                        # reward
                        if en["is_boss"]:
                            score += 20
                            boss_active = False
                        else:
                            score += 1
                        enemies_to_remove.add(id(en))
        # remove flagged bullets/enemies
        # we used id() so now find items by id
        bullets[:] = [b for b in bullets if id(b) not in bullets_to_remove]
        enemies[:] = [en for en in enemies if id(en) not in enemies_to_remove]

        # Collisions: player <-> enemies
        for en in list(enemies):
            if player["rect"].colliderect(en["rect"]):
                # remove enemy
                try:
                    enemies.remove(en)
                except ValueError:
                    pass
                if player_has_shield(player):
                    # shield absorbs hit
                    pass
                else:
                    player["lives"] -= 1

        # Collisions: player <-> powerups
        for p in list(powerups):
            if player["rect"].colliderect(p["rect"]):
                try:
                    powerups.remove(p)
                except ValueError:
                    pass
                player_activate_power(player, p["kind"], duration_ms=7000)

        # Draw background
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill((12, 12, 30))

        # Draw sprites: enemies, powerups, bullets, player
        for en in enemies:
            screen.blit(en["image"], en["rect"])
        for p in powerups:
            screen.blit(p["image"], p["rect"])
        for b in bullets:
            screen.blit(b["image"], b["rect"])
        # player
        screen.blit(player["image"], player["rect"])

        # Draw shield visual if active
        if player_has_shield(player):
            pygame.draw.circle(screen, BLUE, player["rect"].center, 40, 3)

        # UI
        draw_text(screen, f"Score: {score}", small, WHITE, 10, 10)
        draw_text(screen, f"Lives: {player['lives']}", small, WHITE, 10, 35)
        draw_text(screen, f"Bombs: {player['bombs']}", small, WHITE, 10, 60)
        draw_text(screen, f"High: {get_highscore()}", small, WHITE, 650, 10)

        pygame.display.flip()

        # Check game over
        if player["lives"] <= 0:
            return game_over_screen(score)

    return True

# --- Main loop ---
def main():
    pygame.mouse.set_visible(True)
    while True:
        start = menu_screen()
        if not start:
            break
        cont = run_game()
        if not cont:
            break

if __name__ == "__main__":
    main()
