#Main arena file for running Arena Levels

#!/usr/bin/python
#
#Multiplayer Test Arena by Mitch Leff and Peter Kennedy
#
#License - All rights reserved, copyright Mitch Leff and Peter Kennedy
#
#Version = '1.9'

#CONSTANTS
from Constants import *
from Sprites import *
from Helpers import *
from Controller import *

#IMPORTS
import pygame, random, sys, glob, pickle
from pygame.locals import *
from glob import glob#glob allows use of wildcard for reading filenames

#Initialization of pygame modules
init()

#START MUSICS
pygame.mixer.music.load("sounds/Five Armies.mp3")
#pygame.mixer.music.play(-1)#infinite loop

#MAKE SPRITE GROUPS
players = pygame.sprite.Group()
points = pygame.sprite.Group()
bills = pygame.sprite.Group()
platforms = pygame.sprite.Group()

#Load Joysticks
pygame.joystick.init()
joysticks = []

#ADD A PLAYER FOR EVERY JOYSTICK
for i in range(0,pygame.joystick.get_count()):
	joysticks.append(Joystick(i))
	players.add(Player())

#Add a keyboard player
if len(players.sprites()) < 4:
	players.add(Player())
	
while running:
	clock.tick(FPS)

	pressed = pygame.key.get_pressed()
		
	DOWN = pressed[274]
	RIGHT = pressed[275]
	LEFT = pressed[276]
	Yax = 1
	Xax = 0
	
	for event in pygame.event.get():
		if event.type == KEYDOWN:
			pressed = pygame.key.get_pressed()
			if event.key == K_ESCAPE:
				running = False
			elif event.key == K_1:
			#Save all platform positions in map
				saved_platforms = []
				for p in platforms:
					saved_platforms.append(p.rect.midbottom)#cannot pickle Surface objects; must take list of positions
				saveLevel(saved_platforms,raw_input("What level name to save as? "))
			elif event.key == K_2:
			#Load all platform positions in map
				del platforms
				platform_pos = chooseLevel()
				platforms = pygame.sprite.Group()
				for pos in platform_pos:
					newp = platform(pos)
					platforms.add(newp)
					
			#Keyboard Player 1
			elif event.key == K_w:
				jumping[keyboard_player1] = True
			
			elif event.key == K_a:
				xspeed[keyboard_player1] = -1
				
			elif event.key == K_d:
				xspeed[keyboard_player1] = 1			
			
		elif event.type == KEYUP:
			
			#Keyboard Player 1
			if event.key == K_a or event.key == K_d:
				xspeed[keyboard_player1]=0		
			elif event.key == K_w:
				jumping[keyboard_player1] = False

		if event.type == QUIT:
			pygame.quit()
			sys.exit()
			
			
		elif event.type == JOYBUTTONDOWN:
			for controller in enumerate(joysticks):
				i = controller[0]
				jumping[i] = controller[1].get_button(jumpbutton)
				
			if event.button == quitbutton:
				pygame.quit()
				sys.exit()
			elif event.button == firebuttonleft:
				fireleft = True
				bills.add(bill())
				fireleft = False
			elif event.button == firebuttonright:
				fireright = True
				bills.add(bill())
				fireright = False
				
		elif event.type == JOYBUTTONUP:
			for controller in enumerate(joysticks):
				i = controller[0]
				jumping[i] = controller[1].get_button(jumpbutton)
					
		elif event.type == MOUSEBUTTONDOWN:
			newp = platform(event.pos)
			platforms.add(newp)
			screen.blit(newp.image,newp.rect)

	for controller in enumerate(joysticks):
		i = controller[0]
		xspeed[i] = controller[1].get_axis(Xax)#prints unnecessary debug info
		if abs(xspeed[i]) <= xtolerance:#if x is too close to zero
			xspeed[i]=0
	#End new joystick code (1.1)
	
	players.update()	
	bills.update()
	platforms.update()
	
	screen.blit(background_image, (0,0))
	
	#Draw marios
	for player in players:
		for m in player:
			screen.blit(m.image, m.rect)
	
	#Bill collision detection
	for b in bills.sprites():
		screen.blit(b.image, b.rect)
		
		for player in players:
			for m in player:
				if pygame.sprite.collide_mask(b, m) and b.mode == 'fire':
					#Bill Stomp
					if m.rect.bottom < b.rect.top + m.y_vel + m.rect.height/2:
						sfx.play(stomp_sound)
						b.mode = 'die'
						b.y_vel = -8
						b.image = pygame.transform.flip(b.image,False, True)
						m.jump_frames = 1
						m.combo += 1
						score += m.combo
						if score > highscore:
							highscore = score
							highscoreText = scoreFont.render("High Score: %s" % highscore, True, (0,0,255))
						m.y_vel = -6
						points.add(point(m.combo, b.rect.center))
						#Announcer Combo Sounds
						if m.combo == 3:
							announcer.play(combo0)
						elif m.combo == 6:
							announcer.play(combo1)
						elif m.combo == 9:
							announcer.play(combo2)
						elif m.combo == 12:
							announcer.play(combo3)
						elif m.combo >= 15:
							announcer.play(combo4)
					else:
						m.kill()
						sfx.play(die_sound)
						death_timer = DEATH_TIMER

		#Platform collision detection
	for p in platforms.sprites():
		screen.blit(p.image,p.rect)

	screen.blit(scoreText, (0,0))
	screen.blit(highscoreText, (width/2 - highscoreText.get_width()/2, 0))
	pygame.display.update()
	
	cycles += 1
	if death_timer > 0:
		death_timer -= 1
		if death_timer <= 0:
			marios.add(Player())
			marios.add(Player())
			score = 0
			scoreText = scoreFont.render("Score: %s" % score, True, (0,0,255))

#Version History:

	#1.1 - Added controller movement for one player --> detecting controller axis position causes noticeable lag in game. How to optimize?

	#1.2 - Added controller movement and jumping for two players
	
	#1.3 - Added platforms and collision detection for them (very buggy atm)
	
	#1.4 - Softcoded number of players and joysticks
	
	#1.5 - Better collision detection plus left and right collision detection.
	
	#1.6 - Optimized loop movement
	
	#1.7 - Added level saver/loader
	
	#1.8 - Fixed jumping issue
	
	#1.9 - Fixed ducking and stair issue

#Bugs:

	#Up to quad-jumping possible with proper timing
	#Sprite direction defaults to right-facing always
	#Can get stuck on edges of platforms
	#Mario can jump-duck through platforms (best demonstrated on "Maze.map")
	
#TO ADD:

	#One melee and one range ability
	#Different classes
