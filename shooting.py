#!/usr/bin/python
#
#Shooting Test Arena by Peter Kennedy
#
#License - All rights reserved, copyright Mitch Leff and Peter Kennedy
#
#Version = '1.3'

#CONSTANTS
FPS = 60
GRAVITY = .8
MIN_SPEED = 2
MAX_SPEED = 4
DEATH_TIMER = 40
FLOATING_TEXT_LIFESPAN = 70
MAX_SPEED_X = 9
MAX_SPEED_Y = 15
DEBUG = True

#IMPORTS
import pygame, random, sys, glob, pickle
from pygame.locals import *
from glob import glob#glob allows use of wildcard for reading filenames

clock = pygame.time.Clock()
pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.display.set_mode()
pygame.mouse.set_visible(True)
pygame.display.set_caption("Multiplayer Arena Test")

#LOAD SOUNDS
sfx = pygame.mixer.Channel(0)
announcer = pygame.mixer.Channel(1)
guns = pygame.mixer.Channel(2)

die_sound = pygame.mixer.Sound("sounds/die.wav")
jump_sound = pygame.mixer.Sound("sounds/jump.wav")
stomp_sound = pygame.mixer.Sound("sounds/stomp.wav")
shoot = pygame.mixer.Sound("sounds/shoot.wav")
hurt = pygame.mixer.Sound("sounds/hurt.wav")

combo0 = pygame.mixer.Sound("sounds/killingspree.wav")
combo1 = pygame.mixer.Sound("sounds/rampage.wav")
combo2 = pygame.mixer.Sound("sounds/unstoppable.wav")
combo3 = pygame.mixer.Sound("sounds/godlike.wav")
combo4 = pygame.mixer.Sound("sounds/holyshit.wav")

#LOAD IMAGES
background_image = (pygame.image.load("images/coachBig.png").convert_alpha())

#PLAYER IMAGES
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
#explosion = (pygame.image.load("images/explosion.png").convert_alpha())
GRENADE_SPRITE_OPTIONS = [grenade_img]

#ENEMY IMAGES
bill_image = pygame.image.load("images/bill.png").convert_alpha()

#PLATFORM IMAGES
platform_img = pygame.image.load("images/platform.png").convert_alpha()

width  = max(200,background_image.get_width())
height = max(300,background_image.get_height())
size   = [width, height]
screen = pygame.display.set_mode(size)
background = pygame.Surface(screen.get_size())

def br(lines=1):
	for i in range(0,lines):
		print ""
		
def volumeChange(change):
	currentVol = pygame.mixer.music.get_volume()
	currentVol += change
	if currentVol > 1.0:
		currentVol = 1.0
	elif currentVol < 0.0:
		currentVol = 0.0
	pygame.mixer.music.set_volume(currentVol)
	
def saveLevel(currentmap, mapname):
	map = open("maps/"+mapname+".map",'w') #write only means we can create new files
	pickle.dump(currentmap, map)#(object to save, file to save to)
	map.close()
	print "Map saved as:",mapname+".map"
	br()

def loadLevel(mapname):
	try: 
		file = open(mapname,'r')
	except:
		print "No such map: "+mapname
		return
	unpickledmap = pickle.load(file)#load(filename) recreates pickled object
	file.close()
	print "Level '%s"%mapname+"' loaded successfully!"
	br()
	return unpickledmap
	
def chooseLevel():
	options = glob("maps/*.map")#Uses wildcard to make list of all files
	print "Your level options are:"
	for choice in enumerate(options):
		print str(choice[0]+1)+")", choice[1]
	br()
	try:
		choice = input("Which level do you want? ")
	except (NameError,TypeError,SyntaxError):
		print "Invalid choice."
		return chooseLevel()
	return loadLevel(options[choice-1])
	br()

#Base class for bullet-type projectiles
class bullet(pygame.sprite.Sprite):
	def __init__(self,pos,dir=1,damage=10,xvel=200):
	
		#SPRITE
		pygame.sprite.Sprite.__init__(self)
		self.sprite_options = BULLET_SPRITE_OPTIONS
		self.image = self.sprite_options[0]
		self.rect = self.image.get_rect()
		if dir == 1: 
			self.rect.left,self.rect.top = pos
		elif dir == -1:
			self.rect.right,self.rect.top = pos
		
		#MOVEMENT
		self.x_vel = xvel
		self.y_vel = 0
		self.x_accell = 0
		self.y_accell = 0
		self.collided = False
		self.collisionCheckDist = max(self.rect.height,self.rect.width)
		
		#PARAMETERS
		self.damage = damage
		
	def update(self):

		self.x_vel += self.x_accell
		self.y_vel += self.y_accell
		
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
		if self.collided:
			self.kill()
			return
			
		#Check to flip for going left
		if self.x_vel <= 0:
			self.image = pygame.transform.flip(self.image, True, False)
		
	def collisioncheck(self):
		self.collided = False
		if self.rect.bottom >= height:
			self.rect.bottom = height
			self.collided = True
		if self.rect.left < 0:
			self.rect.left = 0
			self.x_vel = 0
			self.x_accell = 0
			self.collided = True
		elif self.rect.right >= width:
			self.rect.right = width
			self.x_vel = 0
			self.x_accell = 0
			self.collided = True
			
		for p in platforms:
			if abs(p.rect.x-self.rect.x)<= self.collisionCheckDist+p.rect.width and\
			abs(p.rect.y-self.rect.y)<= self.collisionCheckDist+p.rect.height:
				if pygame.sprite.collide_mask(p, self):
						if self.rect.left <= p.rect.right and self.rect.right >= p.rect.left:
							#Top collision
							if self.rect.bottom <= p.rect.top+p.rect.height/2 and\
							self.rect.bottom >= p.rect.top:
								self.y_vel = 0
								self.jumped = False
								self.jump_frames = 0
								self.rect.bottom = p.rect.top
								self.collided = True
							#Bottom collision
							elif self.rect.top >= p.rect.bottom-p.rect.height/2 and\
							self.rect.top <= p.rect.bottom:
								self.y_vel = 0
								self.jumped = True
								self.jump_frames = 0
								self.rect.top = p.rect.bottom
								self.collided = True
						
						if self.rect.bottom >= p.rect.top and\
						self.rect.top <= p.rect.bottom:
							#Right Collision
							if self.rect.left <= p.rect.right and\
							self.rect.left >= p.rect.right-10:
								self.x_vel = 0
								self.jumped = True
								self.jump_frames = 0
								self.rect.left = p.rect.right+1
								self.collided = True
							#Left Collision
							elif self.rect.right >= p.rect.left and\
							self.rect.right <= p.rect.left+10:
								self.x_vel = 0
								self.jumped = True
								self.jump_frames = 0
								self.rect.right = p.rect.left-1
								self.collided = True
		for player in players:
			for m in player:
					#*4*
					if abs(m.rect.x-self.rect.x)<= self.collisionCheckDist+m.rect.width and\
					abs(m.rect.y-self.rect.y)<= self.collisionCheckDist+m.rect.height:
						if pygame.sprite.collide_mask(m, self):
							m.health -= self.damage
							if DEBUG:
								print m.health
							hurt.play()
							self.kill()
							return
		
class grenade(pygame.sprite.Sprite):
	def __init__(self,dir,pos,x_vel=10,y_vel=10,elasticity = 0.8):
		pygame.sprite.Sprite.__init__(self)
		self.sprite_options = GRENADE_SPRITE_OPTIONS
		self.image = self.sprite_options[0]
		self.rect = self.image.get_rect()
		if dir == -1:
			self.rect.right,self.rect.top = pos
		elif dir == 1:
			self.rect.left,self.rect.top = pos

		self.max_speed_x = MAX_SPEED_X
		self.max_speed_y = MAX_SPEED_Y
		
		self.accell = 0.1
		
		self.natural_accell = self.accell/2
		
		self.x_vel = dir*x_vel
		self.y_vel = -y_vel
		self.xdirection = 1
		self.ydirection = 0	
		self.x_accell = 0
		self.y_accell = GRAVITY
		self.elasticity = elasticity
		
		self.collided = False
		self.collisionCheckDist = max(self.rect.height,self.rect.width)
		
	def update(self,xspeed=0,UP=False):
		global DOWN, RIGHT, LEFT, height, width, platforms
		
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
			
		#Check to flip for going left
		if self.xdirection == -1:
			self.image = pygame.transform.flip(self.image, True, False)
		
	def collisioncheck(self):
		self.collided = False
		if self.rect.bottom >= height:
			self.rect.bottom = height
			self.bounce("vert")

		if self.rect.left < 0:
			self.bounce("horiz")
			
		elif self.rect.right >= width:
			self.bounce("horiz")
			
		#PLATFORM COLLISIONS
		#*6*
		for p in platforms:
			if abs(p.rect.x-self.rect.x)<= self.collisionCheckDist+p.rect.width and abs(p.rect.y-self.rect.y)<= self.collisionCheckDist+p.rect.height:#Check this code
				if pygame.sprite.collide_mask(p, m):
						if self.rect.left <= p.rect.right and self.rect.right >= p.rect.left:
							
							#Top collision
							if self.rect.bottom <= p.rect.top+p.rect.height/2 and\
							self.rect.bottom >= p.rect.top:
								if DEBUG:
									print "Collide top"
								#self.rect.bottom = p.rect.top
								self.collided = True
								self.bounce("vert")
							
							#Bottom collision
							elif self.rect.top >= p.rect.bottom-p.rect.height/2 and\
							self.rect.top <= p.rect.bottom:
								if DEBUG:
									print "Collide bottom"
								#self.rect.top = p.rect.bottom
								self.collided = True
								self.bounce("vert")
						
						if self.rect.bottom >= p.rect.top+stair_tolerance and\
						self.rect.top <= p.rect.bottom:
							
							#Right Collision
							if self.rect.left <= p.rect.right and\
							self.rect.left >= p.rect.right-10:
								if DEBUG:
									print "Collide right"
								#self.rect.left = p.rect.right+1
								self.collided = True
								self.bounce("horiz")
							
							#Left Collision
							elif self.rect.right >= p.rect.left and\
							self.rect.right <= p.rect.left+10:
								if DEBUG:
									print "Collide left"
								#self.rect.right = p.rect.left-1
								self.collided = True
								self.bounce("horiz")
		return self.collided
		
	def bounce(self,bounce_dir):
		if bounce_dir=="vert":
			self.y_vel *= -self.elasticity
		if bounce_dir=="horiz":
			self.x_vel *= -self.elasticity#*5*
		
class mario(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		
		self.sprite_options = MARIO_SPRITE_OPTIONS
		self.image = self.sprite_options[0]
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
		
		self.health=100
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
		if self.jump_frames != 0: #Jump image if jumped
			self.image = self.sprite_options[1]
			self.step = 0
		elif self.x_vel == 0:
			self.image = self.sprite_options[0]
			self.step = 0
		else:
			self.image = self.moving_sprites[int(self.step) % len(self.moving_sprites)]
			self.step += 1.0/self.image_tempo
		#Check to flip for going left
		if self.xdirection == -1:
			self.image = pygame.transform.flip(self.image, True, False)
		
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
			if abs(p.rect.x-self.rect.x)<= self.collisionCheckDist+p.rect.width and abs(p.rect.y-self.rect.y)<= self.collisionCheckDist+p.rect.height:
				if pygame.sprite.collide_mask(p, m):
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
		
	def shoot(self,dmg,speed):
		global bullets
		if self.xdirection>0:#facing right
			direction = self.rect.right
			bullet_dir = 1
		elif self.xdirection<0:
			direction = self.rect.left
			bullet_dir = -1
		shot = bullet((direction,self.rect.top+self.rect.height/2),bullet_dir,dmg,speed)
		bullets.add(shot)
		
	def throw(self):
		global grenades
		if self.xdirection>0:#facing right
			direction = self.rect.right
			grenade_dir = 1
		elif self.xdirection<0:
			direction = self.rect.left
			grenade_dir = -1
		item = grenade(grenade_dir,(direction,self.rect.top+self.rect.height/2),abs(self.x_vel)+10,abs(self.y_vel)+10)
		grenades.add(item)
		if DEBUG:
			print item.rect.midbottom
			
pointFont = pygame.font.SysFont('ocraextended',24)
class point(pygame.sprite.Sprite):
	def __init__(self, n, pos):
		pygame.sprite.Sprite.__init__(self)
		self.life = FLOATING_TEXT_LIFESPAN
		self.pos = pos
		self.n = n
		self.text = pointFont.render("+%s" % self.n, True, (0,255,0))
	
	def update(self):
		self.life -= 1
		if self.life <= 0:
			self.kill()
			
class platform(pygame.sprite.Sprite):
	def __init__(self,pos):
		pygame.sprite.Sprite.__init__(self)
		self.image = platform_img
		self.rect = self.image.get_rect()
		self.rect.midbottom = pos	

points = pygame.sprite.Group()
platforms = pygame.sprite.Group()
bullets = pygame.sprite.Group()
grenades = pygame.sprite.Group()

highscore = 0
score = 0
running = True
cycles = 0
death_timer = 0

scoreFont = pygame.font.SysFont('ocraextended', 26)
scoreText = scoreFont.render("Score: %s" % score, True, (0,0,255))
highscoreText = scoreFont.render("High Score: %s" % highscore, True, (0,0,255))

#START MUSICS
pygame.mixer.music.load("sounds/Five Armies.mp3")
pygame.mixer.music.play(-1)#infinite loop
pygame.mixer.music.set_volume(0)

#Load Joysticks
pygame.joystick.init()
joysticks = []
xspeed = []
jumping = []
marios1 = pygame.sprite.Group(mario())
marios2 = pygame.sprite.Group(mario())
marios3 = pygame.sprite.Group(mario())
marios4 = pygame.sprite.Group(mario())
totalplayers = [marios1,marios2,marios3,marios4]
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
	players.append(totalplayers[keyboard_player1])
	xspeed.append(0)
	jumping.append(False)
	
if len(players) < 4:
	keyboard_player2 = len(players)
	players.append(totalplayers[keyboard_player2]) #If no players, add one player
	xspeed.append(0)
	jumping.append(False)
	
xtolerance=0.05
stair_tolerance = 8 #how many pixels a sprite can run up (like stairs _--__--)
#assign controls to marios1

#CONTROL VARIABLES
firebuttonleft = 4
firebuttonright = 5
fireleft = False
fireright = False
jumpbutton = 0
quitbutton = 6#6 is back button

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
					m.shoot(10,m.xdirection*5)
				guns.play(shoot)
				
			elif event.key == K_LSHIFT:
				for m in players[keyboard_player1]:
					m.throw()
			
			#Keyboard Player 2
			elif event.key == K_UP:
				jumping[keyboard_player2] = True
			
			elif event.key == K_LEFT:
				xspeed[keyboard_player2] = -1
				
			elif event.key == K_RIGHT:
				xspeed[keyboard_player2] = 1
			
			elif event.key == K_SLASH:
				for m in players[keyboard_player2]:
					m.shoot(10,m.xdirection*5)#10 is dmg
				guns.play(shoot)
				
		elif event.type == KEYUP:
			
			#Keyboard Player 1
			if event.key == K_a or event.key == K_d:
				xspeed[keyboard_player1]=0		
			elif event.key == K_w:
				jumping[keyboard_player1] = False
			
			#Keyboard Player 2
			if event.key == K_LEFT or K_RIGHT:
				xspeed[keyboard_player2]=0
			elif event.key == K_UP:
				jumping[keyboard_player2]=False
				
		#QUIT
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		
		#JOYSTICK CONTROLS
		elif event.type == JOYBUTTONDOWN:
			for controller in enumerate(joysticks):
				i = controller[0]
				jumping[i] = controller[1].get_button(jumpbutton)
				
			if event.button == quitbutton:
				pygame.quit()
				sys.exit()
			elif event.button == firebuttonleft:
				for m in marios1:
					m.shoot(5,-5)
				guns.play(shoot)
			elif event.button == firebuttonright:
				for m in marios1:
					m.shoot(5,5)
				guns.play(shoot)
				
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
		if abs(xspeed[i]) <= xtolerance:#if x is too close to zero
			xspeed[i]=0
	#End new joystick code (1.1)
	
	for player in enumerate(players):
		i=player[0]
		player[1].update(xspeed[i],jumping[i])
		
	platforms.update()
	
	screen.blit(background_image, (0,0))
	
	#Draw Marios
	for player in players:
		for m in player:
			screen.blit(m.image, m.rect)
	
	#Draw Plaforms
	for p in platforms.sprites():
		screen.blit(p.image,p.rect)
		
	#Draw and Update Bullets
	for b in bullets:
		b.update()
		screen.blit(b.image, b.rect)

	#Update and Draw Grenades
	for g in grenades:
		g.update()
		screen.blit(g.image, g.rect)

	screen.blit(scoreText, (0,0))
	screen.blit(highscoreText, (width/2 - highscoreText.get_width()/2, 0))
	pygame.display.update()
	
	cycles += 1

#Version History

	#1.0 - Bullets
	
	#1.1 - 

	#1.3 - Added grenades

#Bugs:

	#*1* keyboard_player1 has no platform collision detection
	#*2* Bullets only die on top half of platforms --> check collision code, probably same problem as mario jump-ducking
	#*3* keyboard_player2 has infinite jump loop
	#*4* each bullet hits player 4 times --> temp fix only hit for 1/4 of damage
	#*5* Grenade slides, doesn't bounce --> be sure to negate y_accell, instead of y_vel, override gravity, but (maybe multiply by 1+ elasticity instead)
	#*6* Collisions with platforms broken for grenades --> same code as mario
	#*7* 

#TO ADD:

	#One melee and one range ability
	#Different classes
	#Camera scrolling
	#Damage and health system
	#HUD
	#Ability to adjust number of players and allow at least 2 on keyboard
	
#Attributions:
	
	#Sounds
		#Laser Sound - http://www.freesound.org/people/THE_bizniss/sounds/39459/ 
			#- THE_bizniss CC Sample+ 1.0
		#Hurt Sound - http://www.freesound.org/people/thecheeseman/sounds/44429/ 
			#- thecheeseman CC Attribution 3.0
		
	#Images

	#Code
