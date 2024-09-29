import pygame, random, time
from pygame.locals import *

#VARIABLES
SCREEN_WIDHT = 400
SCREEN_HEIGHT = 600
SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15

GROUND_WIDHT = 2 * SCREEN_WIDHT
GROUND_HEIGHT= 100

PIPE_WIDHT = 80
PIPE_HEIGHT = 500

PIPE_GAP = 200

boost = 'assets/audio/delorean_aud.wav' #'Delorean' engine boost sound from freesound.org
hit = 'assets/audio/delorean-end.wav'  #'Delorean' crashing sound
background = 'assets/audio/backgroundmusic.wav'

pygame.mixer.init()
pygame.mixer.music.load(background)
pygame.mixer.music.play(-1)  # Loop the background music

class Bird(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images =  [pygame.image.load('assets/sprites/delorean.png').convert_alpha(),
                        pygame.image.load('assets/sprites/delorean2.png').convert_alpha()]

        self.speed = SPEED

        self.current_image = 0
        self.image = pygame.image.load('assets/sprites/delorean.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDHT / 15
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):
        self.current_image = (self.current_image + 1) % 2 #alternate between images
        self.image = self.images[self.current_image]
        self.speed += GRAVITY

        #UPDATE HEIGHT
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

    def begin(self):
        self.current_image = (self.current_image + 1) % 2 #pick one of two starter images
        self.image = self.images[self.current_image]

class Vortex(pygame.sprite.Sprite):

    def __init__(self, xpos, ypos):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('assets/sprites/vortex.gif').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDHT, PIPE_GAP + 50))

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = ypos

        self.mask = pygame.mask.from_surface(self.image)
        self.passed = False

    def update(self):
        self.rect[0] -= GAME_SPEED

class VortexBarrier(pygame.sprite.Sprite):

    def __init__(self, xpos, ypos, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((PIPE_WIDHT, height))
        self.image.set_alpha(0)  # Make it invisible
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = ypos
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= GAME_SPEED

class Ground(pygame.sprite.Sprite):
    
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDHT, GROUND_HEIGHT))

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):
        self.rect[0] -= GAME_SPEED

def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_vortex_with_barriers(xpos):
    ypos = random.randint(100, 300)
    vortex = Vortex(xpos, ypos)
    barrier_above = VortexBarrier(xpos, 0, ypos)
    barrier_below = VortexBarrier(xpos, ypos + PIPE_GAP, SCREEN_HEIGHT - (ypos + PIPE_GAP))
    return vortex, barrier_above, barrier_below

def game_over_screen(screen, score):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Game Over! Score: {score}", True, (255, 255, 255))
    text_rect = text.get_rect(center=(SCREEN_WIDHT/2, SCREEN_HEIGHT/2))
    restart_text = font.render("Press SPACE to restart", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDHT/2, SCREEN_HEIGHT/2 + 50))
    
    screen.blit(text, text_rect)
    screen.blit(restart_text, restart_rect)
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return False
            if event.type == KEYDOWN and event.key == K_SPACE:
                return True

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
    pygame.display.set_caption('SFU FallHacks 2024: Faster than light')

    BACKGROUND = pygame.image.load('assets/sprites/background-present.png')
    BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDHT, SCREEN_HEIGHT))
    BEGIN_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()

    clock = pygame.time.Clock()

    while True:
        bird_group = pygame.sprite.Group()
        bird = Bird()
        bird_group.add(bird)

        ground_group = pygame.sprite.Group()
        for i in range(2):
            ground = Ground(GROUND_WIDHT * i)
            ground_group.add(ground)

        vortex_group = pygame.sprite.Group()
        barrier_group = pygame.sprite.Group()

        for i in range(2):
            vortex, barrier_above, barrier_below = get_random_vortex_with_barriers(SCREEN_WIDHT * i + 800)
            vortex_group.add(vortex)
            barrier_group.add(barrier_above)
            barrier_group.add(barrier_below)

        begin = True
        score = 0

        while begin:
            clock.tick(15)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return
                if event.type == KEYDOWN:
                    if event.key == K_SPACE or event.key == K_UP:
                        bird.bump()
                        pygame.mixer.Sound(boost).play()
                        begin = False

            screen.blit(BACKGROUND, (0, 0))
            screen.blit(BEGIN_IMAGE, (50, 100))

            if is_off_screen(ground_group.sprites()[0]):
                ground_group.remove(ground_group.sprites()[0])
                new_ground = Ground(GROUND_WIDHT - 20)
                ground_group.add(new_ground)

            bird.begin()
            ground_group.update()

            bird_group.draw(screen)
            ground_group.draw(screen)

            pygame.display.update()

        while True:
            clock.tick(15)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return
                if event.type == KEYDOWN:
                    if event.key == K_SPACE or event.key == K_UP:
                        bird.bump()
                        pygame.mixer.Sound(boost).play()

            screen.blit(BACKGROUND, (0, 0))

            if is_off_screen(ground_group.sprites()[0]):
                ground_group.remove(ground_group.sprites()[0])
                new_ground = Ground(GROUND_WIDHT - 20)
                ground_group.add(new_ground)

            if is_off_screen(vortex_group.sprites()[0]):
                vortex_group.remove(vortex_group.sprites()[0])
                barrier_group.remove(barrier_group.sprites()[0])
                barrier_group.remove(barrier_group.sprites()[0])

                vortex, barrier_above, barrier_below = get_random_vortex_with_barriers(SCREEN_WIDHT * 2)
                vortex_group.add(vortex)
                barrier_group.add(barrier_above)
                barrier_group.add(barrier_below)

            bird_group.update()
            ground_group.update()
            vortex_group.update()
            barrier_group.update()

            bird_group.draw(screen)
            vortex_group.draw(screen)
            ground_group.draw(screen)

            # Update score when passing through a vortex
            for vortex in vortex_group:
                if vortex.rect.right < bird.rect.left and not vortex.passed:
                    score += 1
                    vortex.passed = True

            # Display score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))

            pygame.display.update()

            if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
                    pygame.sprite.groupcollide(bird_group, barrier_group, False, False, pygame.sprite.collide_mask)):
                pygame.mixer.Sound(hit).play()
                time.sleep(1)
                if not game_over_screen(screen, score):
                    return
                break

if __name__ == "__main__":
    main()