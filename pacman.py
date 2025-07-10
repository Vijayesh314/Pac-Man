import os
os.environ["SDL_VIDEO_FULLSCREEN_DISPLAY"] = "0"
os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
os.environ["SDL_VIDEO_FULLSCREEN"] = "1"

import pgzrun
from pgzero.actor import Actor
from pgzero.rect import Rect
from pgzero.keyboard import keyboard
from tkinter import messagebox
from random import randint
import time
import sys

#Dimensions of screen
HEIGHT = 1500
WIDTH = 1500

game_over = False
vulnerable = False
lives = 3
score = 0

#Define Pac Man
pac = Actor("pac.png")
pac.pos = (randint(200, 1300), randint(200, 1300))

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

#Define collectible
pellets = []
for i in range(100):
    pellet = Actor("pellet.png")
    pellet.pos = (randint(200, 900), randint(200, 900))
    pellets.append(pellet)

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

def add_word(word, x0, y0, walls, block=50, gap=70):
    for i, ch in enumerate(word):
        pattern = letters[ch]
        for row, line in enumerate(pattern):
            for col, bit in enumerate(line):
                if bit == "1":
                    x = x0 + i*(5*block + gap) + col*block
                    y = y0 + row*block
                    walls.append(Rect((x, y), (block, block)))

walls = []
#Top Row SHIP
add_word("S", x0=150, y0=175, walls=walls)
add_word("H", x0=450, y0=50, walls=walls)
add_word("I", x0=800, y0=150, walls=walls)
add_word("P", x0=1100, y0=75, walls=walls)
#Bottom Row WRECK
add_word("W", x0=50, y0=600, walls=walls)
add_word("R", x0=350, y0=550, walls=walls)
add_word("E", x0=650, y0=650, walls=walls)
add_word("C", x0=950, y0=575, walls=walls)
add_word("K", x0=1250, y0=630, walls=walls)

def draw():
    screen.fill((0, 0, 0))
    #Pac appears on screen
    pac.draw()
    for pellet in pellets:
        pellet.draw()
    for ghost in ghosts:
        ghost.draw()
    for wall in walls:
        screen.draw.filled_rect(wall, (0, 0, 255))
    screen.draw.text("Score: " + str(score), center=(100,50), color="white",fontsize=60)
    screen.draw.text("Lives: " + str(lives), center=(100,100), color="white",fontsize=60)

def update():
    global game_over, lives, score, vulnerable
    oldx, oldy = pac.x, pac.y
    
    #Left Arrow key pressed makes pac go left, change image to left-facing
    if keyboard.left or keyboard.a:
        pac.angle = 180
        pac.x=pac.x-4
    #Right Arrow key pressed makes pac go right
    elif keyboard.right or keyboard.d:
        pac.angle = 0
        pac.x=pac.x+4
    #Up Arrow key pressed makes pac go up, change image to up-facing
    elif keyboard.up or keyboard.w:
        pac.angle = 90
        pac.y=pac.y-4
    #Down Arrow key pressed makes pac go down, change image to down-facing
    elif keyboard.down or keyboard.s:
        pac.angle = 270
        pac.y=pac.y+4

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
                randomize(ghost)            
            else:
                #If pac collides with ghost, 1 life is lost
                lives -= 1
                #If pac collides with ghost thrice, the game is over
                if lives == 0:
                    game_over = True
                    messagebox.showinfo("Game Over", f"Final score: {score}")
                    sys.exit()
                #Game resests if pac collides with ghost
                else:
                    pac.pos = (100, 100)
                    for ghost in ghosts:
                        ghost.pos = (randint(600, 900), randint(100, 700))
                    messagebox.showinfo("Warning", f"You have {lives} lives left!")
                    time.sleep(1)

    for wall in walls:
        if pac.colliderect(wall):
            pac.x, pac.y = oldx, oldy
            break
    
    #If pac collides with pellet, score increases by 10 the pellet is placed randomly on screen
    for pellet in pellets:
        if pac.colliderect(pellet):
            score += 10
            pellets.remove(pellet)
        
def time_up():
    global game_over
    game_over = True

#Schedule the time up event after 60 seconds
clock.schedule_unique(time_up, 60)  
pgzrun.go()
