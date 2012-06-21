import pygame, random
from Constants import *
from HUD import *
from Item import *
from Projectiles import *


#Collision class should return type of collision and object collided with
#How to make this run only once for the entire movement?
class Collision():
	def __init__(self,collidingObject):
		self.collidingObject = collidingObject
		self.collidedWith = [] #array of objects with which the collidingObject collided
		#Relative position of collidingObject to collidable object
		self.above
		self.under
		self.left
		self.right

	def checkAll(self,thePlatforms):
		#Goes through all possible collisions
		self.platforms = thePlatforms
		self.players = players
		#self.enemies = enemies
		self.items = items
		self.collision = False
		if self.collidingObject.isPlayer:
			self.checkVector()
			self.boundsCollision()
			self.platformCollision()
			self.playerCollision()
			#self.enemyCollision() --> no enemies yet
			self.itemCollision()
		return self.collision
	
	def checkVector(self):
		result = self.collidingObject.rect
		#result.top += self.collidingObject.y_vel
		#result.left += self.collidingObject.x_vel
		for p in self.platforms:
			xdistanceFromObject = self.collidingObject.rect.center[0] - p.rect.center[0]
			ydistanceFromObject = self.collidingObject.rect.center[1] - p.rect.center[1]
			closestObject
			if (DEBUG):
				print "Distance from object:",distanceFromObject,\
				"Resultant distance from object:",resultantDistance
				br()
				#self.collision = True
				#return self.collision
	
	def boundsCollision(self):
		#Out-of-Bounds Check --> only affects player and enemy sprites
		if self.collidingObject.rect.bottom >= height-HUDSIZE:
			self.collidingObject.rect.bottom = height-HUDSIZE
			self.collidingObject.jump_frames = 0
			self.collidingObject.jumped = False
			self.collidingObject.combo = 0
		if self.collidingObject.rect.left < 0:
			self.collidingObject.rect.left = 0
			self.collidingObject.x_vel = 0
			self.collidingObject.x_accell = 0
		elif self.collidingObject.rect.right >= width:
			self.collidingObject.rect.right = width
			self.collidingObject.x_vel = 0
			self.collidingObject.x_accell = 0
				
	def platformCollision(self):
		#Returns True if self.collidingObject collides with platform
		for p in self.platforms:
			if pygame.sprite.collide_rect(p, self.collidingObject):
				if pygame.sprite.collide_mask(p, self.collidingObject):
					
					if self.collidingObject.rect.right >= p.rect.left and\
					self.collidingObject.rect.left <= p.rect.right:
						#Top collision
						if self.collidingObject.rect.bottom <= p.rect.top+p.rect.height/2 and\
						self.collidingObject.rect.bottom >= p.rect.top:
							if DEBUG:
								print "Collide top"
							self.collidingObject.y_vel = 0
							self.collidingObject.jumped = False
							self.collidingObject.jump_frames = 0
							self.collidingObject.rect.bottom = p.rect.top
							self.collision = True
						
						#Bottom collision
						elif self.collidingObject.rect.top >= p.rect.bottom-p.rect.height/2 and\
						self.collidingObject.rect.top <= p.rect.bottom:
							if DEBUG:
								print "Collide bottom"
							self.collidingObject.y_vel = 0
							self.collidingObject.jumped = True
							self.collidingObject.jump_frames = 0
							self.collidingObject.rect.top = p.rect.bottom
							self.collision = True
			
					if self.collidingObject.rect.bottom >= p.rect.top+stair_tolerance and\
					self.collidingObject.rect.top <= p.rect.bottom:
						#Right Collision
						if self.collidingObject.rect.left <= p.rect.right and\
						self.collidingObject.rect.left >= p.rect.right-10:
							if DEBUG:
								print "Collide right"
							self.collidingObject.x_vel = 0
							self.collidingObject.jumped = True
							self.collidingObject.jump_frames = 0
							self.collidingObject.rect.left = p.rect.right+1
							self.collision = True
					
						#Left Collision
						elif self.collidingObject.rect.right >= p.rect.left and\
						self.collidingObject.rect.right <= p.rect.left+10:
							if DEBUG:
								print "Collide left"
							self.collidingObject.x_vel = 0
							self.collidingObject.jumped = True
							self.collidingObject.jump_frames = 0
							self.collidingObject.rect.right = p.rect.left-1
							self.collision = True
		#return self.collision
	
	def playerCollision(self):
		#Returns True if self.collidingObject collides with a player
		for player in self.players:
			for m in player:
				if pygame.sprite.collide_rect(m,self.collidingObject):
					if pygame.sprite.collide_mask(m, self.collidingObject):
						self.collision = True
						m.health -= self.damage
						if DEBUG:
							print m.health
						hurt.play()
				#return self.collision
	
	def enemyCollision(self):
		for enemy in self.enemies:
			if pygame.sprite.collide_rect(enemy,self.collidingObject):
				if pygame.sprite.collide_mask(enemy, self.collidingObject):
					self.collision = True
		return self.collision
		
	def itemCollision(self):
		for item in self.items:
			if pygame.sprite.collide_rect(item,self.collidingObject):
				if pygame.sprite.collide_mask(item, self.collidingObject):
					self.collision = True
		#return self.collision
		

#Main class for playable characters, will have a subclass for each playable class (soldier,spy,medic,engi)
class Player(pygame.sprite.Sprite):
	def __init__(self,playerNum):
		self.isPlayer = True
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
		self.collisionHandler = Collision(self)
		
		self.health=100.0
		self.maxHealth = 100
		self.combo = 0
		
		self.healthBar = HealthBar(self)
		
		self.currentItems = []
		self.inventory = Inventory(self)
		
	def update(self,thePlatforms,xspeed=0,UP=False):
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
		
		self.collisionHandler.checkAll(thePlatforms)
		
		"""#Update position
		if (self.x_vel<0):
			for i in range(abs(int(self.x_vel))):
				self.rect.left += -1
				self.collisionHandler.checkAll()
		elif (self.x_vel>0):
			for i in range(int(self.x_vel)):
				self.rect.left += 1
				self.collisionHandler.checkAll()
		if (self.y_vel<0):
			for i in range(abs(int(self.y_vel))):
				self.rect.top += -1
				self.collisionHandler.checkAll()
		elif (self.y_vel>0):
			for i in range(int(self.y_vel)):
				self.rect.top += 1
				self.collisionHandler.checkAll()"""

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

