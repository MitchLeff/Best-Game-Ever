#!/usr/bin/python
#
#Shooting Test Arena by Peter Kennedy
#
#License - All rights reserved, copyright Mitch Leff and Peter Kennedy
#
#Version = '1.0'

#CONSTANTS
FPS = 60
GRAVITY = .8
MIN_SPEED = 2
MAX_SPEED = 4
DEATH_TIMER = 40
FLOATING_TEXT_LIFESPAN = 70
MAX_SPEED_X = 9
MAX_SPEED_Y = 15

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

die_sound = pygame.mixer.Sound("sounds/die.wav")
jump_sound = pygame.mixer.Sound("sounds/jump.wav")
stomp_sound = pygame.mixer.Sound("sounds/stomp.wav")
shoot = pygame.mixer.Sound("sounds/shoot.wav")

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

#BULLET IMAGES
bullet_img = (pygame.image.load("images/bullet.png").convert_alpha())
BULLET_SPRITE_OPTIONS = [bullet_img]

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
	def __init__(self,pos,damage=5,xvel=200):
	
		#SPRITE
		pygame.sprite.Sprite.__init__(self)
		self.sprite_options = BULLET_SPRITE_OPTIONS
		self.image = self.sprite_options[0]
		self.rect = self.image.get_rect()
		self.rect.left,self.rect.top = pos
		
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
			abs(p.rect.y-self.rect.y)<= self.collisionCheckDist+self.rect.height:
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
		return self.collided
		
class projectile(pygame.sprite.Sprite):
	def __init__(self,x_vel,y_vel,elasticity = 0.8):
		pygame.sprite.Sprite.__init__(self)
		self.x_vel = xvel
		self.y_vel = yvel
		self.elasticity = elasticity
		
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
		
		self.combo = 0
		
	def update(self,xspeed=0,UP=False):
		global DOWN, RIGHT, LEFT, height, width, platforms
		#Determine x direction and acceleration 
		#Joystack compatible
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
			if abs(p.rect.x-m.rect.x)<= self.collisionCheckDist+p.rect.width and abs(p.rect.y-m.rect.y)<= self.collisionCheckDist+p.rect.height:
				if pygame.sprite.collide_mask(p, m):
						if self.rect.left <= p.rect.right and self.rect.right >= p.rect.left:
							
							#Top collision
							if self.rect.bottom <= p.rect.top+p.rect.height/2 and\
							self.rect.bottom >= p.rect.top:
								print "Collide top"
								self.y_vel = 0
								self.jumped = False
								self.jump_frames = 0
								self.rect.bottom = p.rect.top
								self.collided = True
							
							#Bottom collision
							elif self.rect.top >= p.rect.bottom-p.rect.height/2 and\
							self.rect.top <= p.rect.bottom:
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
								print "Collide right"
								self.x_vel = 0
								self.jumped = True
								self.jump_frames = 0
								self.rect.left = p.rect.right+1
								self.collided = True
							
							#Left Collision
							elif self.rect.right >= p.rect.left and\
							self.rect.right <= p.rect.left+10:
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
		elif self.xdirection<0:
			direction = self.rect.left	
		shot = bullet((direction,self.rect.top+self.rect.height/2),dmg,speed)
		bullets.add(shot)
			
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
#pygame.mixer.music.play(-1)#infinite loop

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
	
if len(players) == 0:
	players.append(totalplayers[0]) #If no players, add one player
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
			elif event.key == K_w:
				jumping[0] = True
			
			elif event.key == K_a:
				xspeed[0] = -1
				
			elif event.key == K_d:
				xspeed[0] = 1
			
			elif event.key == K_SPACE:
				for m in marios1:
					m.shoot(5,m.xdirection*5)
				shoot.play()
				
		elif event.type == KEYUP and (event.key == K_a or event.key == K_d):
			xspeed[0]=0
				
		elif event.type == KEYUP and (event.key == K_w):
			jumping[0] = False
				
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
				shoot.play()
			elif event.button == firebuttonright:
				for m in marios1:
					m.shoot(5,5)
				shoot.play()
				
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
		screen.blit(b.image, b.rect)
		b.update()

	screen.blit(scoreText, (0,0))
	screen.blit(highscoreText, (width/2 - highscoreText.get_width()/2, 0))
	pygame.display.update()
	
	cycles += 1

#Bugs:

	#Bullets only die on top half of platforms --> check collision code, probably same problem as mario jump-ducking

#TO ADD:

	#One melee and one range ability
	#Different classes
	#Camera scrolling
	#Damage and health system
	#HUD
	#Ability to adjust number of players and allow at least 2 on keyboard
	
#Attributions:
	
	#Sounds
		#Laser sound - http://www.freesound.org/people/THE_bizniss/sounds/39459/
	
	#Images
	
	#Code
