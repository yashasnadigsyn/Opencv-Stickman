import pygame, cv2, random, time
import numpy as np
import mediapipe as mp

#mediapipe module load for pose
mpPose = mp.solutions.pose
pose = mpPose.Pose()

# Initialize
pygame.init()
pygame.font.init()
text_font = pygame.font.SysFont('Comic Sans MS', 200)
gameover = text_font.render('GAME OVER', False, (255,0,0))
text_font_for_health = pygame.font.SysFont('Comic Sans MS', 60)

#score
score = 0
#score_condition_not_shown = 0 #we need this to track for every 100 score and resets after every final boss defeat but score does not reset since it is endless

#hardness
hardness = 0

#condition for score after 100
moving = 0

#speed
speed = 10

#levels (ik even though its endless game, lets add levels)
level = 1

#speed for final boss also increases after every level
speedforfinalboss = 10

#to not get error
rightwrist_x, rightwrist_y, leftwrist_x, leftwrist_y = 0,0,0,0
middleshoulder_x, middleshoulder_y = 1280, 720
middlehip_x, middlehip_y, nose_x, nose_y = 1280, 720, 1280, 720
#a list of colors for stickman and getting random for the player to choose
stickmancolors = [(255,0,255), (7, 242, 207), (228, 28, 235), (0,255,255)]
colorforstickman = random.choice(stickmancolors)

# Create Window/Display
width, height = 1280, 720
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Stickman-Mediapipe")
 
# Initialize Clock for FPS
fps = 30
clock = pygame.time.Clock()
 
# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # width
cap.set(4, 720)  # height

#health for final boss
health = 200

#width side for condition
width_side = True

#importing small demon and finalboss images
imgDevil = pygame.image.load('devil.png')
imgDevil = pygame.transform.scale(imgDevil, (100,100))
rectDevil = imgDevil.get_rect()
rectDevil.x, rectDevil.y = 0,500
imgFinalBoss = pygame.image.load('finalboss.png')
imgFinalBoss = pygame.transform.scale(imgFinalBoss, (500,700))
rectFinalBoss = imgFinalBoss.get_rect()
rectFinalBoss.x, rectFinalBoss.y = -100,50

# Main loop
start = True
while start:
    # Get Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            start = False
            pygame.quit()

    #logic for devil's side.. for every even level devil come from another side
    if moving == 0 and level%2 != 0:
        width_side = False
        rectDevil.x += speed
        if rectDevil.x > width or rectDevil.x < 0:
            rectDevil.x = 0
            rectDevil.y = random.randint(100,int(h)-100)
            rectFinalBoss.x, rectFinalBoss.y = width+10, height+10

    if moving == 0 and level%2 == 0:
        width_side = True
        rectDevil.x -= speed
        if rectDevil.x < 0 or rectDevil.x > width:
            rectDevil.x = width + 10
            rectDevil.y = random.randint(100, int(h)-100)
            rectFinalBoss.x, rectFinalBoss.y = width+10, height+10

    # OpenCV
    success, image = cap.read()
    image = cv2.flip(image, 1)
    imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)
    h,w,c = image.shape
    image = cv2.rectangle(image, (0,0), (w,h), (0,0,0), -1)
    cv2.putText(image, f"Score: {score}", (30,50), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,255), 1)
    if moving == 0:
        cv2.putText(image, f"Level: {level}", ((1280//2)-200, 60), cv2.FONT_HERSHEY_PLAIN, 3, (255,255,255), 1)
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
            middleshoulder_x, middleshoulder_y = int(leftshoulder_x + rightshoulder_x)//2, int(leftshoulder_y+rightshoulder_y) // 2
            cv2.circle(image, (middleshoulder_x, middleshoulder_y), 5, colorforstickman, cv2.FILLED)
            middlehip_x, middlehip_y = int(lefthip_x + righthip_x)//2, int(lefthip_y+righthip_y) // 2
            cv2.circle(image, (middlehip_x, middlehip_y), 5, colorforstickman, cv2.FILLED)
            cv2.circle(image, (leftwrist_x, leftwrist_y), 5, colorforstickman, cv2.FILLED)
            cv2.circle(image, (rightwrist_x, rightwrist_y), 5, colorforstickman, cv2.FILLED)
            cv2.circle(image, (leftankle_x, leftankle_y), 5, colorforstickman, cv2.FILLED)
            cv2.circle(image, (rightankle_x, rightankle_y), 5, colorforstickman, cv2.FILLED)
            #cv2.circle(image, (nose_x, nose_y), 5, (255,0,0), cv2.FILLED)
            image = cv2.line(image, (middleshoulder_x, middleshoulder_y), (rightwrist_x, rightwrist_y), colorforstickman, 3)
            image = cv2.line(image, (middleshoulder_x, middleshoulder_y), (leftwrist_x, leftwrist_y), colorforstickman, 3)
            image = cv2.line(image, (middleshoulder_x, middleshoulder_y), (middlehip_x, middlehip_y), colorforstickman, 3)
            image = cv2.line(image, (middlehip_x, middlehip_y), (leftankle_x, leftankle_y), colorforstickman, 3)
            image = cv2.line(image, (middlehip_x, middlehip_y), (rightankle_x, rightankle_y), colorforstickman, 3)
            image = cv2.line(image, (middleshoulder_x, middleshoulder_y), (nose_x, nose_y+50), colorforstickman, 3)
            image = cv2.circle(image, (nose_x, nose_y), 50, colorforstickman, 3)
            image = cv2.circle(image, (rightwrist_x, rightwrist_y), 10, (255,0,0), -1)
            imgRGB = cv2.circle(image, (leftwrist_x, leftwrist_y), 10, (255,0,0), -1)
    imgRGB = np.rot90(imgRGB)
    frame = pygame.surfarray.make_surface(imgRGB).convert()
    frame = pygame.transform.flip(frame, True, False)
    window.blit(frame, (0, 0))
    window.blit(imgDevil, rectDevil)
    
    #damage devil here with fire
    if rectDevil.collidepoint(rightwrist_x, rightwrist_y) or rectDevil.collidepoint(leftwrist_x, leftwrist_y):
        rectDevil.x = 0
        rectDevil.y = random.randint(100, int(h)-100)
        score += 5

    #logic if devil passes our nose_x and is below the nose_y, then absolutely it should have touched stickman
    if moving == 0 and width_side == False:
        if rectDevil.x > nose_x and rectDevil.y > nose_y:
            image = cv2.rectangle(image, (0,0), (w,h), (0,0,0), -1)
            moving = 2
            ctime = time.time()
    
    #my problem is here
    if moving == 0 and width_side == True:
        if rectDevil.x < nose_x and rectDevil.y > nose_y:
            image = cv2.rectangle(image, (0,0), (w,h), (0,0,0), -1)
            moving = 2
            ctime = time.time()

    #gameover screen
    if moving == 2:
        window.blit(gameover, (200,300))
        etime = time.time()
        if etime-ctime > 2:
            exit()
    
    #finalboss logic
    if moving == 1:
        window.blit(imgFinalBoss, rectFinalBoss)
        rectFinalBoss.x += speedforfinalboss
        healthshow = text_font_for_health.render(f'Health: {health}', False, (255,255,255))
        window.blit(healthshow, (30,50))
        if rectFinalBoss.collidepoint(rightwrist_x, rightwrist_y) or rectFinalBoss.collidepoint(leftwrist_x, leftwrist_y):
            health = health-10
            if health == 0:
                rectFinalBoss.x, rectFinalBoss.y = width, height
                score += 50
                moving = 0
                health = 200
                speed += 8
                level += 1
        if rectFinalBoss.collidepoint(middleshoulder_x, middleshoulder_y) or rectFinalBoss.collidepoint(middlehip_x, middlehip_y):
            moving = 2
            ctime = time.time()

    
    if score != 0 and score%20==0 and moving==0:
        rectDevil.x, rectDevil.y = width+100, height+100
        rectFinalBoss.x, rectFinalBoss.y = -100, 50
        moving = 1

    # Update Display
    pygame.display.update()
    # Set FPS
    clock.tick(fps)