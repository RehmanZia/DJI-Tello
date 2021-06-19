import pygame
import json
import math

"""
how many pixel = actual distance in cm
70px = 360cm --> 360/70 = MAP_SIZE_COEFF
"""
MAP_SIZE_COEFF = 1.5
width=720
height=720
pygame.init()
screen = pygame.display.set_mode([720,720])
screen.fill((255,255,255))
running = True
ic=(255,255,255)
ac=(240,230,230)

path_direction=[]
path_dist_cm = []
path_dist_px = []
path_angle = []
waypoints = []

class Background(pygame.sprite.Sprite):
    def __init__(self, image, location, scale):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image)
        self.image = pygame.transform.rotozoom(self.image, 0, scale)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location



def text_objects(text,font):
    textSurface = font.render(text,True, (0,0,0))
    return textSurface,textSurface.get_rect()
def draw_grid():

    row=col=10
    row_width=width//row
    col_height=height//col

    x=70
    y=0
    for i in range(row):
        x+=row_width
        pygame.draw.line(screen,pygame.Color("Grey"),(x,0),(x,height))


    for i in range(col):
        y+=col_height
        pygame.draw.line(screen, pygame.Color("Grey"), (140,y), ((width+100),y))



def get_dist_btw_pos(pos0, pos1):
    """
    Get distance between 2 mouse position.
    """
    x = abs(pos0[0] - pos1[0])
    y = abs(pos0[1] - pos1[1])
    dist_px = math.hypot(x, y)
    dist_cm = dist_px * MAP_SIZE_COEFF
    return int(dist_cm), int(dist_px)

def button(msg,x,y,w,h,ic,ac,action=None):
    click = pygame.mouse.get_pressed()
    mouse = pygame.mouse.get_pos()
    if x+w>mouse[0]>x and y+h>mouse[1]>y:
        pygame.draw.rect(screen, ac, (x, y, w, h))
        if click[0]==True and action!=None:
            if action=="Straight":
                path_direction.append(2)
            elif action=="Right":
                path_direction.append(1)
            elif action=="Left":
                path_direction.append(0)
            elif action=="Save":
                pass
            elif action=="Quit":
                pygame.quit()
                quit()

    else:
        pygame.draw.rect(screen, ic, (x, y, w, h))
    smallText = pygame.font.Font("freesansbold.ttf",20)
    textSurf , textReact = text_objects(msg,smallText)
    textReact.center = ((x+(w/2)),(y+(h/2)) )
    screen.blit(textSurf,textReact)
def get_angle_btw_line(pos0, pos1, posref):
    """
    Get angle between two lines respective to 'posref'
    NOTE: using dot product calculation.
    """
    ax = posref[0] - pos0[0]
    ay = posref[1] - pos0[1]
    bx = posref[0] - pos1[0]
    by = posref[1] - pos1[1]
    # Get dot product of pos0 and pos1.
    _dot = (ax * bx) + (ay * by)
    # Get magnitude of pos0 and pos1.
    _magA = math.sqrt(ax**2 + ay**2)
    _magB = math.sqrt(bx**2 + by**2)
    _rad = math.acos(_dot / (_magA * _magB))
    # Angle in degrees.
    angle = (_rad * 180) / math.pi
    return int(angle)

"""
Main capturing mouse program.
"""
# Load background image.
#bground = Background('image.png', [0, 0], 1.6)
#screen.blit(bground.image, bground.rect)

path_wp = []
index = 0
x_start = 140
y_start = 0
while running:
    draw_grid()
    click = pygame.mouse.get_pressed()
    mouse = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if mouse[0]>x_start:
            if click[0]==1:
                path_wp.append(mouse)
                #print(mouse)
                if index > 0:
                    if mouse[0]>x_start:
                        pygame.draw.line(screen, (255, 0, 0), path_wp[index-1], mouse, 3)
                index += 1
            elif click[0]==0:
                pass
    # (x postion,y position,width,height)
    #print(click)
    button("Straight", 20, 120, 100, 50, ic, ac,"Straight")
    button("Right", 20, 190, 100, 50, ic, ac,"Right")
    button("Left", 20, 260, 100, 50, ic, ac,"Left")
    button("Save", 20, 330, 100, 50, ic, ac,"Save")
    button("Quit", 20, 400, 100, 50, ic, ac,"Quit")


    pygame.display.update()

"""
Compute the waypoints (distance and angle).
"""
# Append first pos ref. (dummy)
path_wp.insert(0, (path_wp[0][0], path_wp[0][1] - 10))
for index in range(len(path_wp)):
    # Skip the first and second index.
    if index > 1:
        dist_cm, dist_px = get_dist_btw_pos(path_wp[index-1], path_wp[index])
        path_dist_cm.append(dist_cm)
        path_dist_px.append(dist_px)

    # Skip the first and last index.
    if index > 0 and index < (len(path_wp) - 1):
        angle = get_angle_btw_line(path_wp[index-1], path_wp[index+1], path_wp[index])
        path_angle.append(angle)

# Print out the information.
print('path_wp: {}'.format(path_direction))
print('path_wp: {}'.format(path_wp))
print('dist_cm: {}'.format(path_dist_cm))
print('dist_px: {}'.format(path_dist_px))
print('dist_angle: {}'.format(path_angle))

"""
Save waypoints into JSON file.
"""
for index in range(len(path_dist_cm)):
    waypoints.append({
        "direction":path_direction[index],
        "dist_cm": path_dist_cm[index],
        "dist_px": path_dist_px[index],
        "angle_deg": path_angle[index]
    })

# Save to JSON file.


f = open('waypoint.json', 'w+')
path_wp.pop(0)
json.dump({
    "wp": waypoints,
    "pos": path_wp
    }, f, indent=4)
f.close()
