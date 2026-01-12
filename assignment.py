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
import random
from config import *


pygame.init()
pygame.mixer.init()


pygame.mixer.music.load(MUSIC_FILE)
pygame.mixer.music.play(-1)

bullet_snd = pygame.mixer.Sound(GUN_SOUND)
bullet_snd.set_volume(0.4)


# screen and fonts
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("Oscar Shooting ")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 48)
small = pygame.font.SysFont(None, 26)

# images (quick load, fallback simple surfaces if not found)
def load_img(name, size=None):
    try:
        img = pygame.image.load(name).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception as e:
        print("can't load image", name, ":", e)
        w,h = size if size else (50,50)
        surf = pygame.Surface((w,h), pygame.SRCALPHA)
        surf.fill((120,120,120,255))
        return surf

bg_img = load_img(BG_FILE, (W,H))
tower_img = load_img(TOWER_FILE, (120,120))
bullet_img = load_img(BULLET_FILE, (24,32))

# ---------------- Player ----------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = tower_img
        self.rect = self.image.get_rect(midbottom=(W//2, H-10))
        self.shoot_delay = 12   # frames between shots
        self.timer = 0
        self.blood = 5          # <-- health shown as "blood"
        self.double_until = 0
        self.shield_until = 0

    def update(self):
        mx, _ = pygame.mouse.get_pos()
        self.rect.centerx = mx
        self.rect.clamp_ip(screen.get_rect())
        self.timer += 1

    def can_shoot(self):
        return self.timer > self.shoot_delay

    def shoot(self):
        self.timer = 0
        # play sound if loaded
        try:
            if bullet_snd:
                bullet_snd.play()
        except:
            pass
        bullets = [Bullet(self.rect.centerx, self.rect.top)]
        # double shot powerup -> make two extra bullets
        if pygame.time.get_ticks() < self.double_until:
            bullets.append(Bullet(self.rect.centerx - 18, self.rect.top))
            bullets.append(Bullet(self.rect.centerx + 18, self.rect.top))
        return bullets

    def activate(self, kind):
        now = pygame.time.get_ticks()
        if kind == "double":
            self.double_until = now + 7000
        elif kind == "shield":
            self.shield_until = now + 7000
        elif kind == "blood":
            self.blood += 1  # +1 blood when collect blood powerup

    @property
    def shield(self):
        return pygame.time.get_ticks() < self.shield_until

# ---------------- Bullet ----------------
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # make a copy so scaling / transforms won't affect original
        self.image = bullet_img.copy()
        self.rect = self.image.get_rect(midbottom=(x,y))
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# ---------------- Enemy ----------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, boss=False):
        super().__init__()
        self.boss = boss
        size = 120 if boss else 60
        self.image = pygame.Surface((size,size))
        # red-ish color
        self.image.fill((180,40,40))
        self.rect = self.image.get_rect(topleft=(x,y))
        self.hp = 40 if boss else 1
        self.dir = 1

    def update(self):
        if self.boss:
            if self.rect.top < 40:
                self.rect.y += 2
            else:
                # boss moves sideways
                self.rect.x += self.dir * 3
                if self.rect.left <= 0 or self.rect.right >= W:
                    self.dir *= -1
        else:
            # basic enemy falls down
            self.rect.y += 3
            if self.rect.top > H:
                self.kill()

# ---------------- Powerup ----------------
class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        super().__init__()
        self.kind = kind
        self.image = pygame.Surface((30,30))
        if kind == "shield":
            self.image.fill(BLUE)
        elif kind == "double":
            self.image.fill((200,200,60))
        else:
            self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x,y))

    def update(self):
        self.rect.y += 3
        if self.rect.top > H:
            self.kill()

# ---------------- draw blood (health) ----------------
def draw_blood(n):
    # draw small red rectangles as "blood" indicators
    for i in range(n):
        x = 10 + i*30
        y = 10
        pygame.draw.rect(screen, RED, (x,y,22,18))
        pygame.draw.rect(screen, BLACK, (x,y,22,18), 2)  # outline

# ---------------- menu (start screen) ----------------
def menu():
    while True:
        screen.blit(bg_img, (0,0))
        title = font.render("Oscar Shooting", True, WHITE)
        screen.blit(title, (W//2 - title.get_width()//2, 180))
        screen.blit(small.render("Move mouse to aim. Click or press SPACE to shoot.", True, WHITE), (120, 270))
        screen.blit(small.render("Press ENTER to Start - ESC to Quit", True, WHITE), (260, 300))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return True
                if e.key == pygame.K_ESCAPE:
                    return False

# ---------------- main game loop ----------------
def game():
    player = Player()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)

    score = 0
    boss_spawned = False

    SPAWN = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN, 700)  # spawn tick

    running = True
    while running:
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return False
            if e.type == SPAWN and not boss_spawned:
                # sometimes spawn an enemy
                if random.randint(1,3) == 1:
                    en = Enemy(random.randint(0, W-60), -60)
                    enemies.add(en)
                    all_sprites.add(en)

        # player controls + shooting
        player.update()
        keys = pygame.key.get_pressed()
        mouse_click = pygame.mouse.get_pressed()[0]
        if (mouse_click or keys[pygame.K_SPACE]) and player.can_shoot():
            for b in player.shoot():
                bullets.add(b)
                all_sprites.add(b)

        bullets.update()
        enemies.update()
        powerups.update()

        # bullet hits enemy
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for en, blist in hits.items():
            en.hp -= len(blist)
            if en.hp <= 0:
                # sometimes drop powerup
                if random.randint(1,5) == 1:
                    kind = random.choice(["double", "shield", "blood"])
                    p = Powerup(en.rect.x, en.rect.y, kind)
                    powerups.add(p)
                    all_sprites.add(p)
                score += 1
                en.kill()

        # spawn boss when score big enough
        if score >= 30 and not boss_spawned:
            boss = Enemy(W//2 - 60, -120, boss=True)
            enemies.add(boss)
            all_sprites.add(boss)
            boss_spawned = True

        # enemy touches player
        collided = pygame.sprite.spritecollide(player, enemies, True)
        for _ in collided:
            if not player.shield:
                player.blood -= 1

        # pick powerup
        for p in pygame.sprite.spritecollide(player, powerups, True):
            player.activate(p.kind)

        # draw everything
        screen.blit(bg_img, (0,0))
        for s in all_sprites:
            screen.blit(s.image, s.rect)

        # show shield around player
        if player.shield:
            pygame.draw.circle(screen, BLUE, player.rect.center, 50, 3)

        draw_blood(player.blood)
        screen.blit(small.render(f"Score: {score}", True, WHITE), (650, 10))

        pygame.display.flip()

        # game over
        if player.blood <= 0:
            # quick game over screen
            go = font.render("Game Over", True, WHITE)
            screen.blit(go, (W//2 - go.get_width()//2, H//2 - 20))
            pygame.display.flip()
            pygame.time.delay(1000)
            return True  # back to menu

    return True

# ---------------- program start ----------------
def main():
    running = True
    while running:
        ok = menu()
        if not ok:
            break
        again = game()
        if not again:
            break

if __name__ == "__main__":
    main()
