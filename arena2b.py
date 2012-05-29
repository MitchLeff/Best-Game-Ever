#!/usr/bin/python
#
#Multiplayer Test Arena by Mitch Leff and Peter Kennedy
#
#License - All rights reserved, copyright Mitch Leff and Peter Kennedy
#
#Version = '1.5'

#Shit got changed
#CONSTANTS
FPS = 60
GRAVITY = .8
MIN_SPEED = 2
MAX_SPEED = 4
DEATH_TIMER = 40
FLOATING_TEXT_LIFESPAN = 70
MAX_SPEED_X = 7
MAX_SPEED_Y = 15

#IMPORTS
import pygame, random,sys,StringIO
from pygame.locals import *

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

combo0 = pygame.mixer.Sound("sounds/killingspree.wav")
combo1 = pygame.mixer.Sound("sounds/rampage.wav")
combo2 = pygame.mixer.Sound("sounds/unstoppable.wav")
combo3 = pygame.mixer.Sound("sounds/godlike.wav")
combo4 = pygame.mixer.Sound("sounds/holyshit.wav")

#LOAD IMAGES
background_image = (pygame.image.load("images/space.jpg").convert_alpha())

mario_still = (pygame.image.load("images/mario_still.png").convert_alpha())
mario_jump = (pygame.image.load("images/mario_jump.png").convert_alpha())
mario_walk1 = (pygame.image.load("images/mario_walk1.png").convert_alpha())
mario_walk2 = (pygame.image.load("images/mario_walk2.png").convert_alpha())
mario_walk3 = (pygame.image.load("images/mario_walk3.png").convert_alpha())
MARIO_SPRITE_OPTIONS = [mario_still, mario_jump, mario_walk1, mario_walk2, mario_walk3, mario_walk2]

bill_image = pygame.image.load("images/bill.png").convert_alpha()
platform_img = pygame.image.load("images/platform.png").convert_alpha()

width  = 500#max(300,background_image.get_width())
height = 400#max(200,background_image.get_height())
size   = [width, height]
screen = pygame.display.set_mode(size)
background = pygame.Surface(screen.get_size())

class bill(pygame.sprite.Sprite):
	def __init__(self, *groups):
		global fireleft,fireright
		directions = [-1, 1]
		pygame.sprite.Sprite.__init__(self)
		
		self.image = bill_image
		self.rect = self.image.get_rect()
		
		if fireleft:
			self.direction = 1
		elif fireright:
			self.direction = -1
		self.y_dir = 0
		self.y_vel = 0
		
		h = random.randint(height/6 , height-self.image.get_height()/2)
		
		if self.direction == 1:
			self.rect.midright = [0, h]
		elif self.direction == -1:
			self.rect.midleft = [width, h]
			self.image = pygame.transform.flip(self.image, True, False)
		self.speed = random.randint(MIN_SPEED,MAX_SPEED)
		
		for g in groups:
			g.add(self)
		
		self.mode = "fire"
	
	def update(self):
		if self.mode == 'fire':
			self.rect.right += self.speed*self.direction
		elif self.mode == 'die':
			self.y_vel += GRAVITY
			self.rect.top += self.y_vel
		if self.rect.right < -10 or self.rect.left > width+10 or self.rect.top > height + 10:
			self.kill()

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
		
		self.combo = 0
		
	def update(self,xspeed=0,UP=False):
		global DOWN, RIGHT, LEFT, height, width
		
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
			
		if not UP:
			self.jumped = True
		
		#Update velocity
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
		self.rect.top += self.y_vel
		self.rect.left += self.x_vel
		
		#Bounds Check
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
bills = pygame.sprite.Group()
platforms = pygame.sprite.Group()

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
	
xtolerance=0.05
#assign controls to marios1

firebuttonleft = 4
firebuttonright = 5
fireleft = False
fireright = False
jumpbutton = 0
quitbutton = 6#6 is back button

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
	
	for player in enumerate(players):
		i=player[0]
		player[1].update(xspeed[i],jumping[i])
		
	bills.update()
	platforms.update()
	
	actual_pos = players[0].sprites()[0].rect.center
	drawn_pos = (0-players[0].sprites()[0].rect.centerx, 0-players[0].sprites()[0].rect.centery)
	
	print actual_pos
	print drawn_pos
	
	screen.blit(background_image, drawn_pos)
	
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

		for player in players:
			for m in player:
				if pygame.sprite.collide_mask(p, m):
					if m.rect.left <= p.rect.right and m.rect.right >= p.rect.left:
						#Top collision
						if m.rect.bottom <= p.rect.top+10 and\
						m.rect.bottom >= p.rect.top:
							print "Collide top"
							m.y_vel = 0
							m.jumped = False
							m.jump_frames = 0
							m.rect.bottom = p.rect.top+1
						#Bottom collision
						elif m.rect.top >= p.rect.bottom-9 and\
						m.rect.top <= p.rect.bottom:
							print "Collide bottom"
							m.y_vel = 0
							m.jumped = True
							m.jump_frames = 0
							m.rect.top = p.rect.bottom+1
					###New left and right collisions not working --> breaks up and down collisions
					if m.rect.bottom >= p.rect.top and\
					m.rect.top <= p.rect.bottom:
						#Right Collision
						if m.rect.left <= p.rect.right and\
						m.rect.left >= p.rect.right-10:
							print "Collide right"
							m.x_vel = 0
							m.jumped = True
							m.jump_frames = 0
							m.rect.left = p.rect.right+1
						#Left Collision
						elif m.rect.right >= p.rect.left and\
						m.rect.right <= p.rect.left+10:
							print "Collide left"
							m.x_vel = 0
							m.jumped = True
							m.jump_frames = 0
							m.rect.right = p.rect.left-1
					if (m.rect.bottom <= p.rect.bottom+1 and\
					m.rect.bottom > p.rect.top+1):
					#if stuck in middle of platform
						if m.y_vel > 0:#if falling
							print "Collide fix falling"
							m.rect.bottom = p.rect.top+1
						elif m.y_vel <= 0: #if jumping
							print "Collide fix jumping"
							m.rect.top = p.rect.bottom+1

	screen.blit(scoreText, (0,0))
	screen.blit(highscoreText, (width/2 - highscoreText.get_width()/2, 0))
	pygame.display.update()
	
	cycles += 1
	if death_timer > 0:
		death_timer -= 1
		if death_timer <= 0:
			marios1.add(mario())
			marios2.add(mario())
			score = 0
			scoreText = scoreFont.render("Score: %s" % score, True, (0,0,255))

#Version History:

	#1.1 - Added controller movement for one player --> detecting controller axis position causes noticeable lag in game. How to optimize?

	#1.2 - Added controller movement and jumping for two players
	
	#1.3 - Added platforms and collision detection for them (very buggy atm)
	
	#1.4 - Softcoded number of players and joysticks
	
	#1.5 - Better collision detection plus left and right collision detection.

#Bugs:

	#Mario faces does not change direction if movement changes direction without stopping
	#Mario glitches through bottom of platform --> usually on lower platforms, need either A) movement code that loops through increments of 1 to better detect collisons or B) better sandwich detection to prevent mario stuck in platform
		#seems to happen mainly when bouncing off of a higher platform
	
#TO ADD:

	#loop-based movement for easier collision detection?
	#better collision detection
	#One melee and one range ability
	#Different classes
