from Helpers import *
from sprite_sheet_loader import *
import pygame, random, sys, glob, pickle

init()

FPS = 60
GRAVITY = .8
MIN_SPEED = 2
MAX_SPEED = 4
DEATH_TIMER = 40
FLOATING_TEXT_LIFESPAN = 70
MAX_SPEED_X = 9
MAX_SPEED_Y = 15
BULLET_SPEED = 10
BULLET_DAMAGE = 10.0
GRENADE_DAMAGE = 80.0
GRENADE_VELOCITY = 10.0
DEBUG = True

#Make Clock
clock = pygame.time.Clock()

#LOAD SOUNDS
sfx = pygame.mixer.Channel(0)
announcer = pygame.mixer.Channel(1)
guns = pygame.mixer.Channel(2)

die_sound = pygame.mixer.Sound("sounds/die.wav")
jump_sound = pygame.mixer.Sound("sounds/jump.wav")
stomp_sound = pygame.mixer.Sound("sounds/stomp.wav")
shoot = pygame.mixer.Sound("sounds/shoot.wav")
hurt = pygame.mixer.Sound("sounds/hurt.wav")
explosion = pygame.mixer.Sound("sounds/explosion.wav")

combo0 = pygame.mixer.Sound("sounds/killingspree.wav")
combo1 = pygame.mixer.Sound("sounds/rampage.wav")
combo2 = pygame.mixer.Sound("sounds/unstoppable.wav")
combo3 = pygame.mixer.Sound("sounds/godlike.wav")
combo4 = pygame.mixer.Sound("sounds/holyshit.wav")

#LOAD IMAGES
background_image = (pygame.image.load("images/coachBig.png").convert_alpha())

mario_still = (pygame.image.load("images/mario_still.png").convert_alpha())
mario_jump = (pygame.image.load("images/mario_jump.png").convert_alpha())
mario_walk1 = (pygame.image.load("images/mario_walk1.png").convert_alpha())
mario_walk2 = (pygame.image.load("images/mario_walk2.png").convert_alpha())
mario_walk3 = (pygame.image.load("images/mario_walk3.png").convert_alpha())
MARIO_SPRITE_OPTIONS = [mario_still, mario_jump, mario_walk1, mario_walk2, mario_walk3, mario_walk2]

#WEAPON IMAGES
bullet_img = (pygame.image.load("images/bullet.png").convert_alpha())
BULLET_SPRITE_OPTIONS = [bullet_img]

grenade_img = (pygame.image.load("images/grenade.png").convert_alpha())
explosion_sprites = sprite_sheet((64,64),"images/explosion_sprites.png")
GRENADE_SPRITE_OPTIONS = [grenade_img,explosion_sprites]

bill_image = pygame.image.load("images/bill.png").convert_alpha()
platform_img = pygame.image.load("images/platform.png").convert_alpha()

width  = max(200,background_image.get_width())
height = max(300,background_image.get_height())
size   = [width, height]
screen = pygame.display.set_mode(size)
background = pygame.Surface(screen.get_size())

highscore = 0
score = 0
running = True
cycles = 0
death_timer = 0

scoreFont = pygame.font.SysFont('ocraextended', 26)
scoreText = scoreFont.render("Score: %s" % score, True, (0,0,255))
highscoreText = scoreFont.render("High Score: %s" % highscore, True, (0,0,255))
	
xtolerance=0.05 #joystick movements must be greater than this (prevents micro movements)
stair_tolerance = 8 #how many pixels a sprite can run up (like stairs _--__--)

firebuttonleft = 4
firebuttonright = 5
fireleft = False
fireright = False
jumpbutton = 0
quitbutton = 6#6 is back button
