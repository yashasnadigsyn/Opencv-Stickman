import pygame
import cv2
import random, time, os
import mediapipe as mp
import numpy

# color codes
RED = (255, 0, 0)

# loading assets
SWORD_WIDTH, SWORD_HEIGHT = 100, 100
SWORD_IMAGE = pygame.image.load(os.path.join("Assets", "sword.png"))

LEFT_SWORD = pygame.transform.scale(SWORD_IMAGE, (SWORD_WIDTH, SWORD_HEIGHT))
RIGHT_SWORD = pygame.transform.scale(
    pygame.transform.flip(SWORD_IMAGE, True, False),
    (SWORD_WIDTH, SWORD_HEIGHT))


DEVIL_WIDTH, DEVIL_HEIGHT = 120, 120
DEVIL_IMAGE = pygame.image.load(os.path.join("Assets", "devil.png"))
DEVIL = pygame.transform.scale(
    DEVIL_IMAGE,
    (DEVIL_WIDTH, DEVIL_HEIGHT))
DEVIL_SPEED = 7

# initialize pygame
pygame.init()
# create pygame window
WIDTH, HEIGHT = 1280, 720
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman-Mediapipe")
pygame.display.toggle_fullscreen()
# Initialize Clock for FPS
FPS = 30
clock = pygame.time.Clock()

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


leftwrist_x, leftwrist_y = 0, 0 # making these global because they're needed for swords
rightwrist_x, rightwrist_y = 0, 0
def draw_stickman():
    global leftwrist_x, leftwrist_y
    global rightwrist_x, rightwrist_y

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

        pygame.draw.line(window, colorforstickman, (middleshoulder_x, middleshoulder_y), (rightwrist_x, rightwrist_y), 2)
        pygame.draw.line(window, colorforstickman, (middleshoulder_x, middleshoulder_y), (leftwrist_x, leftwrist_y), 2)
        pygame.draw.line(window, colorforstickman, (middleshoulder_x, middleshoulder_y), (middlehip_x, middlehip_y), 2)

        pygame.draw.line(window, colorforstickman, (middlehip_x, middlehip_y), (leftankle_x, leftankle_y))
        pygame.draw.line(window, colorforstickman, (middlehip_x, middlehip_y), (rightankle_x, rightankle_y))
        pygame.draw.line(window, colorforstickman, (middleshoulder_x, middleshoulder_y), (nose_x, nose_y+50), 2)

        pygame.draw.circle(window, colorforstickman, (nose_x, nose_y), 50, 2) # face
        pygame.draw.circle(window, RED, (rightwrist_x, rightwrist_y), 10) # right hand
        pygame.draw.circle(window, RED, (leftwrist_x, leftwrist_y), 10) # left hand

def main():
    global score, DEVIL_SPEED

    draw_stickman()

    left_sword = pygame.Rect(leftwrist_x, leftwrist_y - SWORD_HEIGHT, SWORD_WIDTH, SWORD_HEIGHT)
    right_sword = pygame.Rect(rightwrist_x - SWORD_WIDTH, rightwrist_y - SWORD_HEIGHT, SWORD_WIDTH, SWORD_HEIGHT)

    devil = pygame.Rect(0, 350, DEVIL_WIDTH, DEVIL_HEIGHT)
    devil.x = -DEVIL_WIDTH
    devil_right = True # to track if devil is moving right or left

    running = True
    while (running):
        clock.tick(FPS)

        # handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False

        window.fill((0,0,0)) # clearing the pygame display

        # draw stickman
        draw_stickman()

        # draw swords
        left_sword.x = leftwrist_x
        left_sword.y = leftwrist_y - SWORD_HEIGHT
        right_sword.x = rightwrist_x - SWORD_WIDTH
        right_sword.y = rightwrist_y - SWORD_HEIGHT
        window.blit(LEFT_SWORD, (left_sword.x, left_sword.y))
        window.blit(RIGHT_SWORD, (right_sword.x, right_sword.y))

        # draw devil
        if devil_right:
            devil.x += DEVIL_SPEED
        else:
            devil.x -= DEVIL_SPEED
        window.blit(DEVIL, (devil.x, devil.y))

        pygame.display.update() # update the actual display
    
        # handle collision with devil
        if devil.colliderect(left_sword) or devil.colliderect(right_sword) or devil.x > WIDTH or devil.x < -DEVIL_WIDTH:
            if random.randint(0,1):
                devil.x = -DEVIL_WIDTH
                devil_right = True
            else:
                devil.x = WIDTH
                devil_right = False
            
            devil.y = random.randrange(0, 351)

            score += 1
            DEVIL_SPEED += 3 # increase devil speed with every collision

if __name__ == "__main__":
    main()