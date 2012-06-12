import pygame, random
from Constants import *
from HUD import *
from Item import *
from ObjectLists import *
from Projectiles import *

class Player(pygame.sprite.Sprite):
	def __init__(self,playerNum):
		pygame.sprite.Sprite.__init__(self)
		
		self.sprite_options = PLAYER_SPRITE_OPTIONS
		self.imgNum = random.randint(0,3)
		self.image = self.sprite_options[self.imgNum]
		self.rightImage = self.image
		self.leftImage = pygame.transform.flip(self.image, True, False)
		self.rect = self.image.get_rect()
		self.rect.midbottom = [width/2, height-HUDSIZE]
		
		self.playerNum = playerNum
		
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
		self.maxHealth = 100
		self.combo = 0
		
		self.healthBar = HealthBar(self)
		
		self.currentItems = []
		self.inventory = Inventory(self)
		
	def update(self,xspeed=0,UP=False):
		global DOWN, RIGHT, LEFT, height, width, platforms
		#Determine x direction and acceleration 
		#Joystack compatible
		if self.health <= 0:
			sfx.play(die_sound)
			self.kill()
			
		self.healthBar.update()
		self.inventory.update()
			
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
		if self.rect.bottom >= height-HUDSIZE:
			self.rect.bottom = height-HUDSIZE
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

