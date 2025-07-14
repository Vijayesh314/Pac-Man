import os
os.environ["SDL_VIDEO_FULLSCREEN_DISPLAY"] = "0"
os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
os.environ["SDL_VIDEO_FULLSCREEN"] = "1"

import pgzrun
from pgzero.actor import Actor
from pgzero.rect import Rect
from pgzero.clock import schedule_unique
from tkinter import messagebox
from random import randint
import sys

#Dimensions of screen
HEIGHT = 1500
WIDTH = 1500
tilesize = 50

cooldown = False
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
ghostscore = {"red" : 200, "pink": 400, "blue": 800, "orange": 1600}
for ghost in ghosts:
    ghost.frightened = False
    ghost.eaten = False
    ghost.home_pos = (randint(600, 900), randint(100, 700))
    ghost.pos = ghost.home_pos

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
         "10001"]
}

wall_tiles = set()
walls = []
def addletter(letter, x0, y0, walls, block=tilesize, gap=70):
    for i, ch in enumerate(letter):
        pattern = letters[ch]
        for row, line in enumerate(pattern):
            for col, bit in enumerate(line):
                if bit == "1":
                    x = x0 + i * (5*block + gap) + col * block
                    y = y0 + row * block
                    rect = Rect((x, y), (block, block))
                    walls.append({"rect": rect})
                    tilex = x // tilesize
                    tiley = y // tilesize
                    wall_tiles.add((tilex, tiley))

#Top Row SHIP
addletter("S", x0=150, y0=175, walls=walls)
addletter("H", x0=450, y0=50, walls=walls)
addletter("I", x0=800, y0=150, walls=walls)
addletter("P", x0=1100, y0=75, walls=walls)
#Bottom Row WRECK
addletter("W", x0=50, y0=600, walls=walls)
addletter("R", x0=350, y0=550, walls=walls)
addletter("E", x0=650, y0=650, walls=walls)
addletter("C", x0=950, y0=575, walls=walls)
addletter("K", x0=1250, y0=630, walls=walls)

#Define pellets
pellets = []
tiles_x = WIDTH // tilesize
tiles_y = HEIGHT // tilesize
for tx in range(tiles_x):
    for ty in range(tiles_y):
        if (tx, ty) not in wall_tiles:
            pellet = Actor("pellet.png")
            pellet.pos = (tx * tilesize + tilesize // 2, ty * tilesize + tilesize //2)
            pellets.append(pellet)

powerpellets = []
powertiles = [(208, 494), (1160, 486), (774, 77), (1416, 372), (30, 540), (860, 42)]
for x, y in powertiles:
    pellet = Actor("power.png")
    pellet.pos = (x, y)
    powerpellets.append(pellet)

def reset():
    global direction
    pac.pos = (100, 400)
    messagebox.showinfo("Warning", f"You have {lives} lives left!")
    direction = None
    for ghost in ghosts:
        if not ghost.eaten:
            ghost.pos = ghost.home_pos

def end_game():
    messagebox.showinfo("Game Over", f"Final score: {score}")
    sys.exit()

def cooldownreset():
    global cooldown
    cooldown = False

def triggervulnerable():
    for ghost in ghosts:
        if not ghost.eaten:
            ghost.frightened = True
            ghost.image = "vulnerable.png"
    schedule_unique(endvulnerable, 10.0)

def endvulnerable():
    for ghost in ghosts:
        if not ghost.eaten:
            ghost.frightened = False
            ghost.image = ghost.base_image + "right.png"

def update_ghosts():
    for ghost in ghosts:
        if ghost.eaten:
            if ghost.x < ghost.home_pos[0]:
                try_move(ghost, 1, 0)
            elif ghost.x > ghost.home_pos[0]:
                try_move(ghost, -1, 0)
            if ghost.y < ghost.home_pos[1]:
                try_move(ghost, 0, 1)
            elif ghost.y > ghost.home_pos[1]:
                try_move(ghost, 0, -1)
            if (int(ghost.x), int(ghost.y)) == ghost.home_pos:
                ghost.eaten = False
                ghost.image = ghost.base_image + "right.png"
            
def moveghost(ghost):
    if ghost.eaten:
        return
    ogx, ogy = ghost.x, ghost.y
    
    if ghost.frightened:
        if ghost.x < pac.x:
            try_move(ghost, -1, 0)
        elif ghost.x > pac.x:
            try_move(ghost, 1, 0)
    else:
        if ghost.x < pac.x:
            try_move(ghost, 1, 0)
        elif ghost.x > pac.x:
            try_move(ghost, -1, 0)
    
    if ghost.frightened:
        if ghost.y < pac.y:
            try_move(ghost, 0, -1)
        elif ghost.y > pac.y:
            try_move(ghost, 0, 1)
    else:
        if ghost.y < pac.y:
            try_move(ghost, 0, 1)
        elif ghost.y > pac.y:
            try_move(ghost, 0, -1)

    for other in ghosts:
        if other is ghost:
            continue
        if abs(ghost.x - other.x) < tilesize and abs(ghost.y - other.y) < tilesize:
            if ghost.x < other.x:
                try_move(ghost, -1, 0)
            else:
                try_move(ghost, 1, 0)
            if ghost.y < other.y:
                try_move(ghost, 0, -1)
            else:
                try_move(ghost, 0, 1)
            break
    dx, dy = ghost.x - ogx, ghost.y - ogy
    if ghost.frightened:
        ghost.image = "vulnerable.png"
    else:
        if dx > 0:
            ghost.image = ghost.base_image + "right.png"
        elif dx < 0:
            ghost.image = ghost.base_image + "left.png"
        elif dy > 0:
            ghost.image = ghost.base_image + "down.png"
        elif dy < 0:
            ghost.image = ghost.base_image + "up.png"

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

def try_move(ghost, dx, dy):
    oldx = ghost.x
    oldy = ghost.y
    ghost.x += dx
    ghost.y += dy
    tx = int(ghost.x) // tilesize
    ty = int(ghost.y) // tilesize
    if (tx, ty) in wall_tiles:
        ghost.x = oldx
        ghost.y = oldy
        return False
    return True

def draw():
    screen.fill((0, 0, 0))
    #Pac appears on screen
    pac.draw()
    for pellet in pellets:
        pellet.draw()
    for power in powerpellets:
        power.draw()
    for ghost in ghosts:
        ghost.draw()
    for wall in walls:
        screen.draw.filled_rect(wall["rect"], (0, 0, 255))
    screen.draw.text("Score: " + str(score), center=(100,50), color="white",fontsize=60)
    screen.draw.text("Lives: " + str(lives), center=(100,100), color="white",fontsize=60)

def update():
    global lives, score, cooldown
    update_ghosts()

    oldpx = pac.x
    oldpy = pac.y
    speed = 3
    dx = dy = 0
    if direction == "left":
        dx = -speed
    elif direction == "right":
        dx = speed
    elif direction == "up":
        dy = -speed
    elif direction == "down":
        dy = speed
    
    next_tx = int(pac.x + dx) // tilesize
    next_ty = int(pac.y + dy) // tilesize
    if (next_tx, next_ty) not in wall_tiles:
        pac.x += dx
        pac.y += dy
    
    for ghost in ghosts:
        moveghost(ghost)
    for ghost in ghosts:
        if pac.colliderect(ghost) and not cooldown:
            cooldown = True
            schedule_unique(cooldownreset, 1.0)
            if ghost.frightened and not ghost.eaten:
                score += ghostscore[ghost.base_image]
                ghost.eaten = True
                ghost.frightened = False
                #ghost.pos = ghost.home_pos
            elif not ghost.eaten:
                lives -= 1
                if lives <= 0:
                    schedule_unique(end_game, 0.1)
                else:
                    schedule_unique(reset, 0.1)
    for wall in walls:
        if pac.colliderect(wall["rect"]):
            pac.x = oldpx
            pac.y = oldpy
            break
    
    if not (0 <= pac.x <= WIDTH and 0 <= pac.y <= HEIGHT):
        pac.x = oldpx
        pac.y = oldpy

    for pellet in list(pellets):
        if pac.colliderect(pellet):
            score += 10
            pellets.remove(pellet)
            break
    
    for power in list(powerpellets):
        if pac.colliderect(power):
            score += 50
            powerpellets.remove(power)
            triggervulnerable()
            break

pgzrun.go()
