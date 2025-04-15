import pgzrun
from random import randint
from tkinter import Tk, messagebox, simpledialog
import time
import sys

game_over = False
lives = 3
score = 0

#Dimensions of screen
HEIGHT = 900
WIDTH = 900

root = Tk() 
root.withdraw()

#Define Pac Man
pac=Actor("pacright.png")
pac.pos = (100,300)

#Define collectible
pellet=Actor("pellet.png")

#User is introduced to the game
messagebox.showinfo("Welcome to Pacman", "Collect the pellet and avoid the ghosts!")

#User chooses the number of ghosts following pac
num = simpledialog.askinteger("Input", "How many ghosts do you want?", minvalue=1, maxvalue=4)
ghosts = []
#Create ghosts based on user input
for i in range(num):
    ghost = Actor("ghost.png")
    #Random starting position of ghosts
    ghost.pos = (randint(600, 900), randint(100, 700))
    ghosts.append(ghost)

def draw():
    screen.fill("black")
    #Pac appears on screen
    pac.draw()
    pellet.draw()
    for ghost in ghosts:
        ghost.draw()
    screen.draw.text("Score: " + str(score), center=(100,50), color="white",fontsize=60)
    screen.draw.text("Lives: " + str(lives), center=(100,100), color="white",fontsize=60)

def place_pellet(p):
    p.x=randint(20, (WIDTH-20))
    p.y=randint(20, (HEIGHT-20))

def update():
    global game_over, lives, score
    #Left Arrow key pressed makes pac go left
    if keyboard.left or keyboard.a:
        pac.x=pac.x-4
    #Right Arrow key pressed makes pac go right
    elif keyboard.right or keyboard.d:
        pac.x=pac.x+4
    #Up Arrow key pressed makes pac go up
    elif keyboard.up or keyboard.w:
        pac.y=pac.y-4
    #Down Arrow key pressed makes pac go down
    elif keyboard.down or keyboard.s:
        pac.y=pac.y+4

    for ghost in ghosts:
        #Move ghost right if it's left of pac
        if ghost.x < pac.x:
            ghost.x += 1  
        #Move ghost left if it's right of pac
        elif ghost.x > pac.x:
            ghost.x -= 1
        #Move ghost down if its above pac
        if ghost.y < pac.y:
            ghost.y += 1
        #Move ghost up if its below pac
        elif ghost.y > pac.y:
            ghost.y -= 1

    for ghost in ghosts:
        #Conditionals of ghosts moving towards pac
        if pac.colliderect(ghost):
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
    
    #If pac collides with pellet, score increases by 10 the pellet is placed randomly on screen
    if pac.colliderect(pellet):
        score += 10
        place_pellet(pellet)

def time_up():
    global game_over
    game_over = True

#Schedule the time up event after 60 seconds
clock.schedule(time_up, 60)  

place_pellet(pellet)
pgzrun.go()
