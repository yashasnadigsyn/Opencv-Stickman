import pygame
import cv2
import random, time, os
import mediapipe as mp
from math import sqrt

# color codes
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# loading assets
SWORD_WIDTH, SWORD_HEIGHT = 100, 100
SWORD_IMAGE = pygame.transform.rotate(
    pygame.image.load(os.path.join("Assets", "fantasy-sword.png")),
    90)
LEFT_SWORD = pygame.transform.scale(SWORD_IMAGE, (SWORD_WIDTH, SWORD_HEIGHT))
RIGHT_SWORD = pygame.transform.scale(
    pygame.transform.flip(SWORD_IMAGE, True, False),
    (SWORD_WIDTH, SWORD_HEIGHT))

BOSS_WIDTH, BOSS_HEIGHT = 200, 200
BOSS = pygame.transform.scale(
    pygame.image.load(os.path.join("Assets", "dragon-boss.png")),
    (BOSS_WIDTH, BOSS_HEIGHT))
INITIAL_BOSS_SPEED = 10
BOSS_SPEED = INITIAL_BOSS_SPEED
BOSS_INITIAL_HEALTH = 10
BOSS_HEALTH = BOSS_INITIAL_HEALTH


DEVIL_WIDTH, DEVIL_HEIGHT = 120, 120
DEVIL_IMAGE = pygame.image.load(os.path.join("Assets", "devil.png"))
DEVIL = pygame.transform.scale(
    DEVIL_IMAGE,
    (DEVIL_WIDTH, DEVIL_HEIGHT))
INITIAL_DEVIL_SPEED = 7
DEVIL_SPEED = INITIAL_DEVIL_SPEED
MAX_DEVIL_SPEED = DEVIL_SPEED + 30


HEART_FULL_X, HEART_FULL_Y = 10,10
PLAYER_HEALTH_FULL = pygame.image.load(os.path.join("Assets", "heartfull.png"))
PLAYER_HEALTH = pygame.transform.scale(PLAYER_HEALTH_FULL, (90, 90))


# custom pygame events
DEVIL_HIT = pygame.USEREVENT + 1
DEVIL_MISS = pygame.USEREVENT + 2
BOSS_HIT = pygame.USEREVENT + 3
BOSS_HIT_PLAYER = pygame.USEREVENT + 4
BOSS_REVERSE_DIRECTION = pygame.USEREVENT + 5

# initialize pygame
pygame.init()
pygame.font.init()
# create pygame window
WIDTH, HEIGHT = 1280, 720
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman-Mediapipe")
pygame.display.toggle_fullscreen() # go fullscreen
pygame.mouse.set_visible(False) # hide mouse
# Initialize Clock for FPS
FPS = 30
clock = pygame.time.Clock()
# initialize pygame font
FONT = pygame.font.Font(os.path.join("Assets", "font", "OpenSans-VariableFont_wdth_wght.ttf"), 30)
SCOREFONT = pygame.font.Font(os.path.join("Assets", "font", "OpenSans-VariableFont_wdth_wght.ttf"), 20)

with open("story.txt", "r") as f:
    story_text = f.read().split('\n')
story_pages = [FONT.render(page, 1, WHITE) for page in story_text]

# music
pygame.mixer.init()
pygame.mixer.music.load(os.path.join("Assets", "music", "The-Black-Waltz__Scott-Buckley.mp3"))
pygame.mixer.music.play()

# game over screen
GAME_OVER = pygame.transform.scale(
    pygame.image.load(os.path.join("Assets", "game_over.png")),
    (WIDTH, HEIGHT)
)


# mediapipe module load for pose
mpPose = mp.solutions.pose
pose = mpPose.Pose()

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # width
cap.set(4, 720)  # height

# various vars
colorforstickman = (7, 242, 207)

score = 0 # game score

health = 5 # miss the devils 3 times and its game over

BOSS_TRIGGER_SCORE = 20 # at every increment of 20 in score, boss level is triggered


def distance(x1, y1, x2, y2):
    # returns integer distance between two points
    return int( sqrt((x2 - x1)**2 + (y2 - y1)**2) )

leftwrist_x, leftwrist_y = 0, 0 # making these global because they're needed for swords AND player body collision rects
rightwrist_x, rightwrist_y = 0, 0
middleshoulder_x, middleshoulder_y = 0, 0 # these are required for the player body collision rects
nose_x, nose_y = 0, 0
lefthip_x, lefthip_y = 0, 0
def draw_stickman(): # tracks movements and draws stickman
    global leftwrist_x, leftwrist_y
    global rightwrist_x, rightwrist_y
    global middleshoulder_x, middleshoulder_y
    global nose_x, nose_y
    global lefthip_x, lefthip_y

    # pose tracking
    success, image = cap.read()
    image = cv2.flip(image, 1)
    imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)
    h,w,c = image.shape
    image = cv2.rectangle(image, (0,0), (w,h), (0,0,0), -1)

    # drawing stickman
    if results.pose_landmarks:
        for id, lm in enumerate(results.pose_landmarks.landmark):
            h,w,c = image.shape

            if int(id) == 11: #11 is left shoulder
                leftshoulder_x, leftshoulder_y = int(lm.x * w), int(lm.y * h)
            if int(id) == 12: #12 is right shoulder
                rightshoulder_x, rightshoulder_y = int(lm.x * w), int(lm.y * h)
            if int(id) == 23: #23 is left hip
                lefthip_x, lefthip_y = int(lm.x * w), int(lm.y * h)
            if int(id) == 24: #24 is right hip
                righthip_x, righthip_y = int(lm.x * w), int(lm.y * h)
            if int(id) == 15: #15 is left wrist
                leftwrist_x, leftwrist_y = int(lm.x * w), int(lm.y * h)
            if int(id) == 16: #16 is right wrist
                rightwrist_x, rightwrist_y = int(lm.x * w), int(lm.y * h)
            if int(id) == 27: #27 is left ankle
                leftankle_x, leftankle_y = int(lm.x * w), int(lm.y * h)
            if int(id) == 28: #28 is right ankle
                rightankle_x, rightankle_y = int(lm.x * w), int(lm.y * h)
            if int(id) == 0: #0 is nose
                nose_x, nose_y = int(lm.x * w), int(lm.y * h)
            
        #the next lines till 'if' condition is just connecting the points to make a stick figure
        middleshoulder_x = int(leftshoulder_x + rightshoulder_x)//2
        middleshoulder_y = int(leftshoulder_y + rightshoulder_y) // 2
        pygame.draw.circle(window, colorforstickman, (middleshoulder_x, middleshoulder_y), 5)

        middlehip_x = int(lefthip_x + righthip_x)//2
        middlehip_y = int(lefthip_y + righthip_y) // 2

        pygame.draw.circle(window, colorforstickman, (middlehip_x, middlehip_y), 5)

        pygame.draw.circle(window, colorforstickman, (leftwrist_x, leftwrist_y), 5)
        pygame.draw.circle(window, colorforstickman, (rightwrist_x, rightwrist_y), 5)
        pygame.draw.circle(window, colorforstickman, (leftankle_x, leftankle_y), 5)
        pygame.draw.circle(window, colorforstickman, (rightankle_x, rightankle_y), 5)

        # arms
        pygame.draw.line(window, colorforstickman, (middleshoulder_x, middleshoulder_y), (rightwrist_x, rightwrist_y), 2)
        pygame.draw.line(window, colorforstickman, (middleshoulder_x, middleshoulder_y), (leftwrist_x, leftwrist_y), 2)

        pygame.draw.line(window, colorforstickman, (middleshoulder_x, middleshoulder_y), (middlehip_x, middlehip_y), 2)

        pygame.draw.line(window, colorforstickman, (middlehip_x, middlehip_y), (leftankle_x, leftankle_y))
        pygame.draw.line(window, colorforstickman, (middlehip_x, middlehip_y), (rightankle_x, rightankle_y))
        pygame.draw.line(window, colorforstickman, (middleshoulder_x, middleshoulder_y), (nose_x, nose_y+50), 2)

        pygame.draw.circle(window, colorforstickman, (nose_x, nose_y), 50, 2) # face
        pygame.draw.circle(window, RED, (rightwrist_x, rightwrist_y), 10) # right hand
        pygame.draw.circle(window, RED, (leftwrist_x, leftwrist_y), 10) # left hand


def draw_window(left_sword, right_sword, devil, devil_right, boss_level=False):
    # draw health hearts
    global health, score

    heart_padding_x = 0
    for i in range(health):
        window.blit(PLAYER_HEALTH, (HEART_FULL_X + heart_padding_x, HEART_FULL_Y))
        heart_padding_x += 40
    
    # draw score
    score_text = SCOREFONT.render(f"Score: {score}", 1, WHITE)
    window.blit( score_text, (WIDTH - score_text.get_width() - 10, 10) )

    # draw stickman
    draw_stickman()

    # draw swords
    left_sword.x = leftwrist_x - 10
    left_sword.y = leftwrist_y - SWORD_HEIGHT + 10
    right_sword.x = rightwrist_x - SWORD_WIDTH + 10
    right_sword.y = rightwrist_y - SWORD_HEIGHT + 10
    window.blit(LEFT_SWORD, (left_sword.x, left_sword.y))
    window.blit(RIGHT_SWORD, (right_sword.x, right_sword.y))

    if boss_level:
        # draw boss
        pass
    else:
        # draw devil
        if devil_right:
            devil.x += DEVIL_SPEED
        else:
            devil.x -= DEVIL_SPEED
        window.blit(DEVIL, (devil.x, devil.y))


def devil_collision_detect(devil, left_sword, right_sword, boss_level):
    # player's body collision vars
    global nose_x, nose_y
    global middleshoulder_x, middleshoulder_y

    # checking if devil collides with either sword
    if devil.colliderect(left_sword) or devil.colliderect(right_sword):
        if boss_level:
            pygame.event.post(
                pygame.event.Event(BOSS_HIT)
            )
        else:
            pygame.event.post(
                pygame.event.Event(DEVIL_HIT)
            )
    
    # checking if devil goes off the screen
    if boss_level:
        if devil.x > WIDTH or devil.x < -BOSS_WIDTH:
            pygame.event.post(
                pygame.event.Event(BOSS_REVERSE_DIRECTION)
            )
    else:
        if devil.x > WIDTH or devil.x < -DEVIL_WIDTH:
            pygame.event.post(
                pygame.event.Event(DEVIL_MISS)
            )

    # devil collision with player's face, arms or neck
    # face
    face = pygame.Rect(nose_x - 50, nose_y - 50, 100, 100)

    if devil.colliderect(face):
        if boss_level:
            pygame.event.post(
                pygame.event.Event(BOSS_HIT_PLAYER)
            )
        else:
            pygame.event.post(
                pygame.event.Event(DEVIL_MISS) # can be used because DEVIL_MISS reduces health and respawns a devil
            )
    
    # neck and arms
    hit_neck_or_arms = devil.clipline((nose_x, nose_y), (middleshoulder_x, middleshoulder_y)) or devil.clipline((middleshoulder_x, middleshoulder_y), (leftwrist_x, leftwrist_y)) or devil.clipline((middleshoulder_x, middleshoulder_y), (rightwrist_x, rightwrist_y))

    if hit_neck_or_arms:
        if boss_level:
            pygame.event.post(
                pygame.event.Event(BOSS_HIT_PLAYER)
            )
        else:
            pygame.event.post(
                pygame.event.Event(DEVIL_MISS)
            )
    


def main():
    global score, health
    global DEVIL_SPEED, MAX_DEVIL_SPEED, INITIAL_DEVIL_SPEED
    global BOSS_WIDTH, BOSS_HEIGHT, BOSS_SPEED, BOSS_INITIAL_HEALTH, BOSS_HEALTH
    global nose_x, nose_y
    global story_pages

    # story screen
    page = 0
    tellstory = True
    while(tellstory):

        if page == len(story_pages):
            window.fill((0,0,0))
            break

        window.fill((0,0,0))

        window.blit(story_pages[page], (100, HEIGHT//2 - story_pages[page].get_height()))
        pygame.display.update()

        time.sleep(3.5)
        page += 1

    # main game loop
    draw_stickman()

    left_sword = pygame.Rect(leftwrist_x, leftwrist_y - SWORD_HEIGHT, SWORD_WIDTH, SWORD_HEIGHT)
    right_sword = pygame.Rect(rightwrist_x - SWORD_WIDTH, rightwrist_y - SWORD_HEIGHT, SWORD_WIDTH, SWORD_HEIGHT)

    devil = pygame.Rect(0, 350, DEVIL_WIDTH, DEVIL_HEIGHT)
    devil.x = -DEVIL_WIDTH
    devil_right = True # to track if devil is moving right or left

    boss_level = True # to track if on boss level
    boss = pygame.Rect(0, 20, BOSS_WIDTH, BOSS_HEIGHT)
    boss.x = -BOSS_WIDTH
    boss.y = 0
    boss_right = True

    running = True
    while (running):
        clock.tick(FPS)

        # handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start = False
                pygame.quit()

            if event.type == pygame.KEYDOWN: # press Q to force quit game
                if event.key == pygame.K_q:
                    running = False
            
            if event.type == DEVIL_HIT: # handle devil hit sword event
                if random.randint(0,1):
                    devil.x = -DEVIL_WIDTH
                    devil_right = True
                else:
                    devil.x = WIDTH
                    devil_right = False
        
                devil.y = random.randrange(0, 351)

                score += 1
                DEVIL_SPEED += 2 # increase devil speed with every collision
            
            if event.type == DEVIL_MISS: # same as DEVIL_HIT, but reduce health only
                health -= 1

                if random.randint(0,1):
                    devil.x = -DEVIL_WIDTH
                    devil_right = True
                else:
                    devil.x = WIDTH
                    devil_right = False
        
                devil.y = random.randrange(0, 351)

                DEVIL_SPEED += 2 # increase devil speed with every collision
            
            if event.type == BOSS_HIT:
                boss.x = random.randrange(0, WIDTH - BOSS_WIDTH)
                BOSS_HEALTH -= 1
                BOSS_SPEED += 2

                if BOSS_HEALTH <= 0:
                    boss_level = False

                    boss.y = 0

                    BOSS_HEALTH = BOSS_INITIAL_HEALTH + (score % BOSS_TRIGGER_SCORE)
                    BOSS_SPEED = INITIAL_BOSS_SPEED + (score % BOSS_TRIGGER_SCORE)

                    score += 1

                    if health + 2 > 5:
                        health = 5
                    else:
                        health += 2
            
            if event.type == BOSS_HIT_PLAYER:
                boss.x = random.randrange(0, WIDTH - BOSS_WIDTH)
                BOSS_SPEED += 1
                health -= 2
            
            if event.type == BOSS_REVERSE_DIRECTION:
                pass # handled manually below. TODO: remove this event later

        window.fill((0,0,0)) # clearing the pygame display
    
        # draws the whole game window
        draw_window(left_sword, right_sword, devil, devil_right, boss_level)

        # check if boss level reached
        if score % BOSS_TRIGGER_SCORE == 0:
            if score == 0:
                boss_level = False
            else:
                boss_level = True

        # boss level or normal devils
        if boss_level:
            devil_collision_detect(boss, left_sword, right_sword, boss_level)
        else:
            # detect collisions with the devil and post HIT or MISS events
            devil_collision_detect(devil, left_sword, right_sword, boss_level)

            if DEVIL_SPEED >= MAX_DEVIL_SPEED: # if devil speed reaches max devil speed, boss level is trigered
                INITIAL_DEVIL_SPEED += 2 # increase game hardness by incrementing initial devil speed
                DEVIL_SPEED = INITIAL_DEVIL_SPEED
        
        # handling boss drawing here
        if boss_level:
            # right-left and gradual downward movement
            if boss.x > WIDTH:
                boss_right = False
                boss.y += BOSS_HEIGHT//2
                BOSS_SPEED += 1
            elif boss.x < -BOSS_WIDTH:
                boss_right = True
                boss.y += BOSS_HEIGHT//2
                BOSS_SPEED += 1

            # collisions are handled above
            
            # detect if boss goes vertically out of the screen, triggering game over
            if boss.y > HEIGHT:
                break

            if boss_right:
                boss.x += BOSS_SPEED
            else:
                boss.x -= BOSS_SPEED

            window.blit(BOSS, (boss.x, boss.y))
            bosshealth = FONT.render(f"Boss Health: {BOSS_HEALTH}", 1, WHITE)
            window.blit( bosshealth, (WIDTH - bosshealth.get_width() - 10, 40) )

        pygame.display.update() # update the actual display
        
        if health <= 0:
            break
    
    # GAME OVER screen
    window.fill((0,0,0))
    window.blit(GAME_OVER, (0,0))
    pygame.display.update()
    time.sleep(5)


if __name__ == "__main__":
    main()