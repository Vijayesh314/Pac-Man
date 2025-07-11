import os
os.environ["SDL_VIDEO_FULLSCREEN_DISPLAY"] = "0"
os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
os.environ["SDL_VIDEO_FULLSCREEN"] = "1"

import pgzrun
from pgzero.actor import Actor
from pgzero.rect import Rect
from tkinter import messagebox
from random import randint
import time
import sys

#Dimensions of screen
HEIGHT = 1500
WIDTH = 1500

vulnerable = False
lives = 3
score = 0
direction = None

#Define Pac Man
pac = Actor("pac.png")
pac.pos = (100, 400)

#Define ghosts
pink = Actor("pinkright.png")
pink.base_image = "pink"
blue = Actor("blueright.png")
blue.base_image = "blue"
red = Actor("redright.png")
red.base_image = "red"
orange = Actor("orangeright.png")
orange.base_image = "orange"
ghosts = [pink, blue, red, orange]
for ghost in ghosts:
    ghost.pos = (randint(600, 900), randint(100, 700))

letters = {
    "S": ["01111",
          "10000",
          "01110",
          "00001",
          "11110"],
    "H": ["10001",
          "10001",
          "11111",
          "10001",
          "10001"],
    "I": ["11111",
          "00100",
          "00100",
          "00100",
          "11111"],
    "P": ["11110",
          "10001",
          "11110",
          "10000",
          "10000"],
    "W":["10001",
         "10001",
         "10101",
         "10101",
         "01010"],
    "R":["11110",
         "10001",
         "11110",
         "10100",
         "10010"],
    "E":["11111",
         "10000",
         "11111",
         "10000",
         "11111"],
    "C":["01111",
         "10000",
         "10000",
         "10000",
         "01111"],
    "K":["10001",
         "10010",
         "11100",
         "10010",
         "10001"],
    "D":["11110",
         "10001",
         "10001",
         "10001",
         "11110"]
}

def addword(word, x0, y0, walls, block=50, gap=70):
    for i, ch in enumerate(word):
        pattern = letters[ch]
        for row, line in enumerate(pattern):
            for col, bit in enumerate(line):
                if bit == "1":
                    x = x0 + i*(5*block + gap) + col*block
                    y = y0 + row*block
                    walls.append({"rect": Rect((x, y), (block, block)), "base_y": y})

walls = []
#Top Row SHIP
addword("S", x0=150, y0=175, walls=walls)
addword("H", x0=450, y0=50, walls=walls)
addword("I", x0=800, y0=150, walls=walls)
addword("P", x0=1100, y0=75, walls=walls)
#Bottom Row WRECK
addword("W", x0=50, y0=600, walls=walls)
addword("R", x0=350, y0=550, walls=walls)
addword("E", x0=650, y0=650, walls=walls)
addword("C", x0=950, y0=575, walls=walls)
addword("K", x0=1250, y0=630, walls=walls)

#Define collectible
pellets = []
for i in range(100):
    pellet = Actor("pellet.png")
    pellets.append(pellet)

for pellet in pellets:
    collision_detected = True
    while collision_detected:
        pellet.pos = (randint(200, 900), randint(200, 900))
        collision_detected = False
        for wall in walls:
            if pellet.colliderect(wall["rect"]):
                collision_detected = True
                break

def on_key_down(key):
    global direction
    if key == keys.LEFT or key == keys.A:
        direction = "left"
        pac.angle = 180
    elif key == keys.RIGHT or key == keys.D:
        direction = "right"
        pac.angle = 0
    elif key == keys.UP or key == keys.W:
        direction = "up"
        pac.angle = 90
    elif key == keys.DOWN or key == keys.S:
        direction = "down"
        pac.angle = 270

def draw():
    screen.fill((0, 0, 0))
    #Pac appears on screen
    pac.draw()
    for pellet in pellets:
        pellet.draw()
    for ghost in ghosts:
        ghost.draw()
    for wall in walls:
        screen.draw.filled_rect(wall["rect"], (0, 0, 255))
    screen.draw.text("Score: " + str(score), center=(100,50), color="white",fontsize=60)
    screen.draw.text("Lives: " + str(lives), center=(100,100), color="white",fontsize=60)

def update():
    global lives, score, vulnerable, direction
    oldx, oldy = pac.x, pac.y
    
    if direction == "left":
        pac.x -= 4
    elif direction == "right":
        pac.x += 4
    elif direction == "up":
        pac.y -= 4
    elif direction == "down":
        pac.y += 4

    for ghost in ghosts:
        #Move ghost right if it's left of pac
        if ghost.x < pac.x:
            ghost.x += 1
        #Move ghost left if it's right of pac, change image to left-facing
        elif ghost.x > pac.x:
            ghost.x -= 1
            ghost.image = ghost.base_image + "left.png"
        #Move ghost down if its above pac, change image to down-facing
        if ghost.y < pac.y:
            ghost.y += 1
            ghost.image = ghost.base_image + "down.png"
        #Move ghost up if its below pac, change image to up-facing
        elif ghost.y > pac.y:
            ghost.y -= 1
            ghost.image = ghost.base_image + "up.png"

        for other in ghosts:
            if ghost != other:
                distance = ghost.distance_to(other)
                if distance < 128:
                    # Move slightly away to maintain distance
                    if ghost.x < other.x:
                        ghost.x -= 1
                    else:
                        ghost.x += 1
                    if ghost.y < other.y:
                        ghost.y -= 1
                    else:
                        ghost.y += 1

    for ghost in ghosts:
        #Conditionals of ghosts moving towards pac
        if pac.colliderect(ghost):
            if vulnerable:
                score += 200
                #randomize(ghost)            
            else:
                #If pac collides with ghost, 1 life is lost
                lives -= 1
                #If pac collides with ghost thrice, the game is over
                if lives == 0:
                    messagebox.showinfo("Game Over", f"Final score: {score}")
                    sys.exit()
                #Game resests if pac collides with ghost
                else:
                    pac.pos = (100, 100)
                    for ghost in ghosts:
                        ghost.pos = (randint(600, 900), randint(100, 700))
                    messagebox.showinfo("Warning", f"You have {lives} lives left!")
                    direction = None
                    time.sleep(1)

    for wall in walls:
        if pac.colliderect(wall["rect"]):
            pac.x, pac.y = oldx, oldy
            break
    
    if (pac.x == 1492 or pac.x == 8) or (pac.y == 1492 or pac.y == 8):
        pac.x, pac.y = oldx, oldy

    #If pac collides with pellet, score increases by 10 the pellet is placed randomly on screen
    for pellet in pellets:
        if pac.colliderect(pellet):
            score += 10
            pellets.remove(pellet)
            if not pellets:
                messagebox.showinfo("Game Over", "Congratulations. You have beat the game.")
                sys.exit()
        
pgzrun.go()
