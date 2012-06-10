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
from Platforms import *
from Projectiles import *

class Player(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		
		self.sprite_options = PLAYER_SPRITE_OPTIONS
		self.imgNum = random.randint(0,3)
		self.image = self.sprite_options[self.imgNum]
		self.rightImage = self.image
		self.leftImage = pygame.transform.flip(self.image, True, False)
		self.rect = self.image.get_rect()
		self.rect.midbottom = [width/2, height]
		
		self.max_speed_x = MAX_SPEED_X
		self.max_speed_y = MAX_SPEED_Y
		
		self.accell = 1.0
		
		self.natural_accell = self.accell/2
		
		self.xdirection = 1
		self.ydirection = 0

		self.xspeed = 0
		self.yspeed = 0		
		self.x_vel = 0
		self.y_vel = 0
		self.x_accell = 0
		self.y_accell = GRAVITY
		
		self.moving_sprites = self.sprite_options[2:]
		
		self.step = 0
		self.image_tempo = 6.0
		self.jump_frames = 0
		self.jumped = True
		self.jumping = False
		self.collided = False
		self.collisionCheckDist = max(self.rect.height,self.rect.width)
		
		self.health=100.0
		self.combo = 0
		
	def update(self,xspeed=0,UP=False):
		global DOWN, RIGHT, LEFT, height, width, platforms
		#Determine x direction and acceleration 
		#Joystack compatible
		if self.health <= 0:
			sfx.play(die_sound)
			self.kill()
			
			
		self.xspeed=xspeed
		if self.xspeed!=0:
			self.xdirection = self.xspeed
			self.x_accell = self.xspeed*self.accell
		else:
			self.x_accell = 0
			
		if UP and self.jump_frames <= 10 and not self.jumped:
			if self.jump_frames == 0 and self.combo == 0:
				sfx.play(jump_sound)
			self.y_vel = -10
			self.jump_frames += 1

		self.x_vel += self.x_accell
		self.y_vel += self.y_accell
		
		#Check for deceleration
		if self.x_accell == 0:
			
			if self.x_vel <= self.natural_accell and self.x_vel >= -1*self.natural_accell:
				self.x_vel = 0
			elif self.x_vel < 0:
				self.x_vel += self.natural_accell
			elif self.x_vel > 0:
				self.x_vel -= self.natural_accell
		
		#Check Max Speed
		if self.x_vel >= self.max_speed_x:
			self.x_vel = self.max_speed_x
		elif self.x_vel <= -1*self.max_speed_x:
			self.x_vel = -1*self.max_speed_x
		if self.y_vel >= self.max_speed_y:
			self.y_vel = self.max_speed_y
		elif self.y_vel <= -1*self.max_speed_y:
			self.y_vel = -1*self.max_speed_y
		
		#Update position
		if (self.x_vel<0):
			for i in range(abs(int(self.x_vel))):
				self.rect.left += -1
				if self.collisioncheck():
					break 
		elif (self.x_vel>0):
			for i in range(int(self.x_vel)):
				self.rect.left += 1
				if self.collisioncheck():
					break
		if (self.y_vel<0):
			for i in range(abs(int(self.y_vel))):
				self.rect.top += -1
				if self.collisioncheck():
					break
		elif (self.y_vel>0):
			for i in range(int(self.y_vel)):
				self.rect.top += 1
				if self.collisioncheck():
					break
		#Set Image
		"""if self.jump_frames != 0: #Jump image if jumped
			self.image = self.sprite_options[1]
			self.step = 0"""
		if self.x_vel == 0:
			self.image = self.sprite_options[self.imgNum]
			self.step = 0
		"""else:
			self.image = self.moving_sprites[int(self.step) % len(self.moving_sprites)]
			self.step += 1.0/self.image_tempo"""
		#Check to flip for going left
		if self.xdirection == -1:
			self.image = self.leftImage
		else:
			self.image = self.rightImage
		
	def collisioncheck(self):
		self.collided = False
		if self.rect.bottom >= height:
			self.rect.bottom = height
			self.jump_frames = 0
			self.jumped = False
			self.combo = 0
		if self.rect.left < 0:
			self.rect.left = 0
			self.x_vel = 0
			self.x_accell = 0
		elif self.rect.right >= width:
			self.rect.right = width
			self.x_vel = 0
			self.x_accell = 0
			
		#PLATFORM COLLISIONS
		for p in platforms:
			if abs(p.rect.left-self.rect.x) <= self.collisionCheckDist+p.rect.width and abs(p.rect.y-self.rect.y)<= self.collisionCheckDist+p.rect.height:
			#if pygame.sprite.collide_rect(p, self):
				if pygame.sprite.collide_mask(p, self):
						if self.rect.left <= p.rect.right and self.rect.right >= p.rect.left:
							
							#Top collision
							if self.rect.bottom <= p.rect.top+p.rect.height/2 and\
							self.rect.bottom >= p.rect.top:
								if DEBUG:
									print "Collide top"
								self.y_vel = 0
								self.jumped = False
								self.jump_frames = 0
								self.rect.bottom = p.rect.top
								self.collided = True
							
							#Bottom collision
							elif self.rect.top >= p.rect.bottom-p.rect.height/2 and\
							self.rect.top <= p.rect.bottom:
								if DEBUG:
									print "Collide bottom"
								self.y_vel = 0
								self.jumped = True
								self.jump_frames = 0
								self.rect.top = p.rect.bottom
								self.collided = True
						
						if self.rect.bottom >= p.rect.top+stair_tolerance and\
						self.rect.top <= p.rect.bottom:
							
							#Right Collision
							if self.rect.left <= p.rect.right and\
							self.rect.left >= p.rect.right-10:
								if DEBUG:
									print "Collide right"
								self.x_vel = 0
								self.jumped = True
								self.jump_frames = 0
								self.rect.left = p.rect.right+1
								self.collided = True
							
							#Left Collision
							elif self.rect.right >= p.rect.left and\
							self.rect.right <= p.rect.left+10:
								if DEBUG:
									print "Collide left"
								self.x_vel = 0
								self.jumped = True
								self.jump_frames = 0
								self.rect.right = p.rect.left-1
								self.collided = True
		return self.collided
		
	def shoot(self,players,dmg,speed):
		if self.xdirection>0:#facing right
			direction = self.rect.right+self.max_speed_x+10#ensure bullet doesn't hit player while running
			bullet_dir = 1
		elif self.xdirection<0:#facing left
			direction = self.rect.left-self.max_speed_x-10
			bullet_dir = -1
		shot = bullet(players,bullet_dir,(direction,self.rect.top+self.rect.height/2),dmg,speed)
		bullets.add(shot)
		
	def throw(self,players):
		if self.xdirection>0:#facing right
			direction = self.rect.right
			grenade_dir = 1
		elif self.xdirection<0:
			direction = self.rect.left
			grenade_dir = -1
		item = grenade(players,grenade_dir,(direction,self.rect.top+self.rect.height/2),\
		abs(self.x_vel)+GRENADE_VELOCITY,GRENADE_VELOCITY)
		self.grenade = item
		item.player = self
		grenades.add(item)
		if DEBUG:
			print item.rect.midbottom

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
players1 = pygame.sprite.Group(Player())
players2 = pygame.sprite.Group(Player())
players3 = pygame.sprite.Group(Player())
players4 = pygame.sprite.Group(Player())
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

#MAIN GAME LOOP
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

	for player in enumerate(players):
		i=player[0]
		player[1].update(xspeed[i],jumping[i])
	
	platforms.update()

	screen.blit(background_image, (0,0))
	#Draw players
	for player in players:
		#Check for respawn
		if len(player) == 0:
			player.add(Player())
		for m in player:
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
	#Damage and health system
	#HUD
	
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
