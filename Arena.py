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
from Item import *
from ObjectLists import *
from Platforms import *
from Projectiles import *
from Sprites import *
from HUD import *


highscore = 0
score = 0
running = True
cycles = 0

scoreFont = pygame.font.SysFont('ocraextended', 26)
scoreText = scoreFont.render("Score: %s" % score, True, (0,0,255))
highscoreText = scoreFont.render("High Score: %s" % highscore, True, (0,0,255))

#START MUSICS
pygame.mixer.music.load("sounds/Dungeon.ogg")
pygame.mixer.music.play(-1)#infinite loop
pygame.mixer.music.set_volume(1.0)

pygame.joystick.init()
joysticks = []
xspeed = []
jumping = []
players1 = pygame.sprite.Group(Player(1))
players2 = pygame.sprite.Group(Player(2))
players3 = pygame.sprite.Group(Player(3))
players4 = pygame.sprite.Group(Player(4))
totalplayers = [players1,players2,players3,players4]
players = []

for i in range(0,pygame.joystick.get_count()):
	joysticks.append(pygame.joystick.Joystick(i))
	joysticks[i].init()
	xspeed.append(0)
	jumping.append(False)
	players.append(totalplayers[i])

#Add keyboard players
if len(players) < 4:
	keyboard_player1 = len(players)
	players.append(totalplayers[keyboard_player1]) #If no players, add one player
	xspeed.append(0)
	jumping.append(False)

if len(players) < 4:
	keyboard_player2 = len(players)
	players.append(totalplayers[keyboard_player2]) #add a second keyboard player
	xspeed.append(0)
	jumping.append(False)

items = pygame.sprite.Group()
itemSpawn = 10*FPS
itemdeSpawn = 3*FPS
itemSpawned = False
itemTimer = 0

#MAIN GAME LOOP
while running:
	clock.tick(FPS)
	
	if random.randint(0,itemSpawn)==itemSpawn:
		items.add(Medkit((random.randint(width/2-width/4,width/2+width/4),\
		random.randint(height/2-height/4,height/2+height/4))))
		itemSpawned = True
	if itemSpawned:
		itemTimer+=1
	if itemTimer == itemdeSpawn:
		itemSpawned = False
		itemTimer = 0
		for i in items:
			i.kill()
		
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
					newp = platform(pos)
					platforms.add(newp)
		
			#Keyboard Player 1
			elif event.key == K_w:
				jumping[keyboard_player1] = True
		
			elif event.key == K_a:
				xspeed[keyboard_player1] = -1
			
			elif event.key == K_d:
				xspeed[keyboard_player1] = 1
		
			elif event.key == K_SPACE:
				for m in players[keyboard_player1]:
					m.shoot(players,BULLET_DAMAGE,m.xdirection*(BULLET_SPEED))
				guns.play(shoot)
			
			elif event.key == K_LSHIFT:
				for m in players[keyboard_player1]:
					m.throw(players)
		
			#Keyboard Player 2
			elif event.key == K_UP:
				jumping[keyboard_player2] = True
		
			elif event.key == K_LEFT:
				xspeed[keyboard_player2] = -1
			
			elif event.key == K_RIGHT:
				xspeed[keyboard_player2] = 1
		
			elif event.key == K_SLASH:
				for m in players[keyboard_player2]:
					m.shoot(players,BULLET_DAMAGE,m.xdirection*(5+abs(m.x_vel)+m.max_speed_x))
				guns.play(shoot)
			
			elif event.key == K_PERIOD:
				for m in players[keyboard_player2]:
					m.throw(players)
			
		elif event.type == KEYUP:
		
			#Keyboard Player 1
			if event.key == K_a or event.key == K_d:
				xspeed[keyboard_player1]=0		
			if event.key == K_w:
				jumping[keyboard_player1] = False
			if event.key == K_LSHIFT:
				for m in players[keyboard_player1]:
					try:
						m.grenade.cooking = False
					except:
						break
		
			#Keyboard Player 2
			if event.key == K_LEFT or event.key == K_RIGHT:
				xspeed[keyboard_player2]=0
			if event.key == K_UP:
				jumping[keyboard_player2]=False
			if event.key == K_PERIOD:
				for m in players[keyboard_player2]:
					try:
						m.grenade.cooking = False
					except:
						break
			
			
		#QUIT
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
	
		#JOYSTICK CONTROLS
		elif event.type == JOYBUTTONDOWN:
			for controller in enumerate(joysticks):
				i = controller[0]
				jumping[i] = controller[1].get_button(jumpbutton)
				if event.button == firebuttonright:#***#finish converting controls
					for m in players[i]:
						m.shoot(players,BULLET_DAMAGE,m.xdirection*(5+abs(m.x_vel)+m.max_speed_x))
					guns.play(shoot)
				elif event.button == firebuttonleft:
					for m in players[i]:
						m.throw(players)
			
			if event.button == quitbutton:
				pygame.quit()
				sys.exit()
			
		elif event.type == JOYBUTTONUP:
			for controller in enumerate(joysticks):
				i = controller[0]
				jumping[i] = controller[1].get_button(jumpbutton)
				for m in players[i]:
					if event.button == firebuttonleft:
						m.throw(players)
					
		elif event.type == JOYAXISMOTION:
			for controller in enumerate(joysticks):
				i = controller[0]
				xspeed[i] = controller[1].get_axis(0)
				
		elif event.type == MOUSEBUTTONDOWN:
			newp = platform(event.pos)
			platforms.add(newp)
			screen.blit(newp.image,newp.rect)

	for controller in enumerate(joysticks):
		i = controller[0]
		if abs(xspeed[i]) <= xtolerance:#prevents micro-movements
			xspeed[i]=0
	
	HUD.fill((0,0,0))
	
	for player in enumerate(players):
		i=player[0]
		player[1].update(xspeed[i],jumping[i])
	
	platforms.update()

	screen.blit(background_image, (0,0))
	#Draw players
	for player in enumerate(players):
		#Check for respawn
		if len(player[1]) == 0:
			player[1].add(Player(player[0]+1))
		for m in player[1]:
			screen.blit(m.image, m.rect)

	#Draw Plaforms
	for p in platforms.sprites():
		screen.blit(p.image,p.rect)
	
	#Draw and Update Bullets
	for b in bullets:
		b.update(platforms,players)
		screen.blit(b.image, b.rect)

	#Update and Draw Grenades
	for g in grenades:
		g.update(platforms,players)
		screen.blit(g.image, g.rect)
		
	for i in items:
		i.update(players)

	screen.blit(scoreText, (0,0))
	screen.blit(highscoreText, (width/2 - highscoreText.get_width()/2, 0))
	pygame.display.update()

	cycles += 1

#Version History

	#1.0 - Bullets
	
	#1.1 - Damage and Health
	
	#1.2 - Bullets face proper direction and have sound

	#1.3 - Added grenades
	
	#1.4 - Grenades bounce (but not enough)
	
	#1.5 - Grenades have friction
	
	#1.6 - Grenade and player collisions fixed
	
	#2.0 - players respawn properly, fixed multiple bullet damage bug, bullet no longer hits the shooter automatically, grenades explode and do damage, fixed bullet collision bug, grenade speed influenced by movement speed, fixed grenades right and left collisions, fixed player infinite jumping bug, grenade cooking enabled

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
		#Explosion Sprites - CodeH4x0r - http://s296.photobucket.com/albums/mm182/CodeH4x0r/?action=view&current=explosion17.png

	#Code
		#sprite_sheet_loader based on work from hammythepig - http://stackoverflow.com/questions/10560446/how-do-you-select-a-sprite-image-from-a-sprite-sheet-in-python
