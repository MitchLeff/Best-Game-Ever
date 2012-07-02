#!/usr/bin/python
#
#Shooting Test Arena by Peter Kennedy
#
#License - All rights reserved, copyright Mitch Leff and Peter Kennedy
#
#Version = '2.0'

#IMPORTS
import pygame, random, sys, glob, pickle, sprite_sheet_loader
from pygame.locals import *
from glob import glob#glob allows use of wildcard for reading filenames

from sprite_sheet_loader import *
from Constants import *
from ObjectLists import *
#from Platforms import *
from Projectiles import *
from Sprites import *
from Controller import *
from Helpers import *
from Camera import *
from HUD import *
from Collision import *
from Menu import *
screen = pygame.display.set_mode(size)#,pygame.FULLSCREEN)

highscore = 0
score = 0
running = True
cycles = 0

scoreFont = pygame.font.SysFont('ocraextended', 26)
scoreText = scoreFont.render("Score: %s" % score, True, (0,0,255))
highscoreText = scoreFont.render("High Score: %s" % highscore, True, (0,0,255))

#START MUSICS
pygame.mixer.music.load("sounds/Crystal Mix %.mp3")
pygame.mixer.music.play(-1)#infinite loop
pygame.mixer.music.set_volume(1.0)

pygame.joystick.init()

#Get all active controllers
controllers = []
for i in range(pygame.joystick.get_count()):
	temp_controller = Joystick(i)
	controllers.append(temp_controller)

#Add default Keyboard player
controllers.append(Keyboard(K_n, K_j, K_b, K_h, K_g, K_k, K_y, K_o, K_LSHIFT, K_LCTRL, K_a, K_d, K_w, K_s))

#Make a player for each controller
players = pygame.sprite.Group()
for i in enumerate(controllers):
	players.add(Player(PLAYER_SPRITE_OPTIONS[i[0]%4], i[1], i[0]))

#Create camera
camera = Camera(players.sprites()[0], (width,height-HUDSIZE), background_image.get_size())

#Test Moving Platforms
mp1 = MovingPlatform( [[100,400], [300,400]], [1,0])
mp2 = MovingPlatform( [[500,900], [300,1000]], [2,0])
mp3 = MovingPlatform( [[500,800], [700,1000]], [4,0])
mp4 = MovingPlatform( [[900,700], [700,1000]], [8,0])
mp5 = MovingPlatform( [[100,300], [levelWidth - 100,300]], [20,0])
platforms.add(mp1)
#platforms.add(mp2)
#platforms.add(mp3)
#platforms.add(mp4)
platforms.add(mp5)


#Initialize collision grid
collisionGrid = createGrid(GRID_SQUARE_LENGTH)

def menu():
	startButton = StartGame((width/2-100,height/2))
	buttons = [startButton]
	mainMenu = Menu(buttons)
	MENU = True
	while MENU:
		for event in pygame.event.get():
			if (event.type==MOUSEBUTTONDOWN):
				for button in mainMenu.buttons:
					if button.clicked(event.pos):
						return#each button must return True so that a new loop can start
			elif (event.type==QUIT):
				pygame.quit()
				sys.exit()
		mainMenu.update()
		pygame.display.update()

menu()

currentPlayer = 0
while running:
	clock.tick(FPS)
	HUD.fill((0,0,0))
	for event in pygame.event.get():
		if event.type == KEYDOWN:
			pressed = pygame.key.get_pressed()
			if event.key == K_ESCAPE:
				running = False

			#Toggle debug mode
			elif event.key == K_BACKQUOTE:
				if DEBUG == False:
					DEBUG = True
					print "Debug Mode Enabled."
				elif DEBUG == True:
					DEBUG = False
					print "Debug Mode Disabled."

			#Adjust Music Volume
			elif event.key == K_PAGEUP:
				volumeChange(0.2)
			elif event.key == K_PAGEDOWN:
				volumeChange(-0.2)

			#SAVE PLATFORMS
			elif event.key == K_1:
				saved_platforms = []
				for p in platforms:
					saved_platforms.append(p.rect.midbottom)#cannot pickle Surface objects; must take list of positions
				saveLevel(saved_platforms,raw_input("What level name to save as? "))

			#LOAD PLATFORMS
			elif event.key == K_2:
				del platforms
				platform_pos = chooseLevel()
				platforms = pygame.sprite.Group()
				for pos in platform_pos:
					newp = Platform(pos)
					platforms.add(newp)

		#QUIT
		elif event.type == QUIT:
			pygame.quit()
			sys.exit()

		elif event.type == MOUSEBUTTONDOWN:
			newp = Platform(camera.mod2(event.pos))
			platforms.add(newp)

	for player in players.sprites():
		actions = player.update(players.sprites(), platforms.sprites())
		if isinstance(actions, int):
			newPlayer = Player(PLAYER_SPRITE_OPTIONS[actions%4], controllers[actions], actions)
			players.add(newPlayer)
			camera.mainPlayer = newPlayer

		elif isinstance(actions, dict):
			if actions['Bullet']:
				bullets.add(actions['Bullet'])
			if actions['Grenade']:
				grenades.add(actions['Grenade'])

	platforms.update(camera)

	#Draw Background
	screen.blit(background_image, (-1*camera.pos[0], -1*camera.pos[1]))

	#Draw Players
	for p in players.sprites():
		screen.blit(p.image, camera.mod(p.rect))

	#Draw Platforms
	for p in platforms.sprites():
		if p.on_screen:
			screen.blit(p.image,camera.mod(p.rect))

	#Draw and Update Bullets
	for b in bullets:
		b.update(platforms,players)
		screen.blit(b.image, camera.mod(b.rect))

	#Update and Draw Grenades
	for g in grenades:
		g.update(platforms,players)
		screen.blit(g.image, camera.mod(g.rect))

	collidableSprites = platforms.sprites() + players.sprites() + grenades.sprites() + bullets.sprites()
	for sprite in collidableSprites:
		collisionGrid = updateGrid(sprite, collisionGrid)
	checkForCollisions(collisionGrid)

	for row in collisionGrid:
		for square in row:
			square.draw(screen, camera)


	#Update Camera
	camera.update()

	screen.blit(scoreText, (0,0))
	screen.blit(highscoreText, (width/2 - highscoreText.get_width()/2, 0))

	screen.blit(HUD, (0,height-HUDSIZE))
	pygame.display.update()

	cycles += 1

	if DEBUG:
		print clock.get_fps()

#BUGS:

	#*1* keyboard movement a little unresponsive (left-right war)

#TO ADD:

	#One melee and one range ability
	#Different classes
	#Camera scrolling

#OPTIMIZATIONS:

	#Make grenades not bounce up and down when velocity is 0
	#Make grenade explosions only do damage once, but at any point in time

#Attributions:

	#Sounds
		#Laser Sound - http://www.freesound.org/people/THE_bizniss/sounds/39459/
			#- THE_bizniss CC Sample+ 1.0
		#Hurt Sound - http://www.freesound.org/people/thecheeseman/sounds/44429/
			#- thecheeseman CC Attribution 3.0
		#Explosion Sound - PD, Media College

	#Images

	#Code
