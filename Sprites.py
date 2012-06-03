from Helpers import *
from Constants import *
import pygame, random, sys, glob, pickle

init()

class bill(pygame.sprite.Sprite):
	def __init__(self, *groups):
		directions = [-1, 1]
		pygame.sprite.Sprite.__init__(self)

		size = random.random()

		if size < .025:
			self.image = megaBill_image
		elif size < .1:
			self.image = bigBill_image
		else:
			self.image = bill_image
		self.rect = self.image.get_rect()

		self.direction = random.choice(directions)
		self.y_dir = 0
		self.y_vel = 0

		hh = random.random()

		if hh < .30:
			h = random.randint((height-1*height/6), (height))
		elif hh < .55:
			h = random.randint((height-2*height/6), (height-1*height/6))
		elif hh < .75:
			h = random.randint((height-3*height/6), (height-2*height/6))
		elif hh <= .90:
			h = random.randint((height-4*height/6), (height-3*height/6))
		else:
			h = random.randint((height-5*height/6), (height-4*height/6))

		if h + self.rect.height > height:
			h = height - self.rect.height

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

		self.x_vel = 0
		self.y_vel = 0
		self.x_accell = 0
		self.y_accell = GRAVITY

		self.moving_sprites = self.sprite_options[2:]

		self.step = 0
		self.image_tempo = 6.0
		self.jump_frames = 0
		self.jumped = True

		self.combo = 0

	def update(self):
		global UP, DOWN, RIGHT, LEFT, height, width

		#Determine x direction and acceleration
		if LEFT and RIGHT:
			pass
		elif LEFT:
			self.xdirection = -1
			self.x_accell = -1*self.accell
		elif RIGHT:
			self.xdirection = 1
			self.x_accell = self.accell
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