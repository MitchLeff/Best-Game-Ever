from Collision import *
from Constants import *
from HUD import *
from ObjectLists import *
import pygame, random, sys, glob, pickle

init()
#All sprites must now have an onCollision(Sprite collidingWith) method that defines how each sprite type reacts to a collision with a different type of object#

#Furthermore, all sprites need a self.type variable defining what type of sprite unless Python has a built-in instanceOf function#
			
class Player(pygame.sprite.Sprite):
	def __init__(self, spritesheet, controller, number):
		pygame.sprite.Sprite.__init__(self)
		
		self.controller = controller
		self.player_number = number
		self.playerNum = 1
		self.type = "player"
		
		self.sprite_options = spritesheet
		self.image = self.sprite_options[0]
		self.rect = self.image.get_rect()
		#Make inside rectangle for collisions --> should subtract gunsize from width and a little from the left as well, currently hardcoded, need a better method
		self.rect = pygame.Rect(self.rect.left+5,self.rect.top,self.rect.width-30,self.rect.height)
		self.rect.midbottom = [width/2, height]
		
		self.max_speed_x = MAX_SPEED_X
		self.max_speed_y = MAX_SPEED_Y
		
		self.acceleration = 1.0
		
		self.natural_acceleration = self.acceleration/2
		
		self.xdirection = 1
		self.ydirection = 0

		self.xspeed = 0
		self.yspeed = 0		
		self.x_vel = 0
		self.y_vel = 0
		self.x_acceleration = 0
		self.y_acceleration = GRAVITY
		
		self.moving_sprites = self.sprite_options
		
		self.step = 0
		self.image_tempo = 6.0
		
		self.jumps_left = 0
		self.jumped = False
		
		self.shooting = False
		self.grenading = False
		self.controlling = False
		self.controllee = 0
		self.grenade = 0
		
		self.collided = False
		self.collisionCheckDist = max(self.rect.height,self.rect.width)
		
		self.maxHealth = 100.0
		self.health = self.maxHealth
		self.healthBar = HealthBar(self)
		self.inventory = Inventory(self)
		self.currentItems = []

		#Collision Detection
		self.squaresImIn = []
		
		#Sounds
		self.hurt_sound = hurt
	
	def resetJumps(self):
		self.jumped = False
		self.jumps_left = 2
	
	def update(self, players, currGrid):
		#Joystick compatible
		
		#Get the state of the controller to determine how to update
		if self.controller != 0:
			state = self.controller.getState()
		
		#Test to see if unit is dead
		if self.health <= 0:
			sfx.play(die_sound)
			self.kill()
			return self.player_number
		
		if self.controller!=0:
			#Get direction being pressed and update accordingly
			self.x_acceleration = state['L_R']*self.acceleration
		
		if self.x_acceleration < 0:
			self.xdirection = -1
		elif self.x_acceleration > 0:
			self.xdirection = 1
		
		if self.controller!=0:
			if state['U_D'] == -1 and self.jumps_left > 0 and not self.jumped:
				sfx.play(jump_sound)
				self.y_vel = -18
				self.jumped = True
				self.jumps_left -= 1
			if state['U_D'] != -1:
				self.jumped = False

		self.x_vel += self.x_acceleration
		self.y_vel += self.y_acceleration
		
		#Check for deceleration
		if self.x_acceleration == 0:
			
			if self.x_vel <= self.natural_acceleration and self.x_vel >= -1*self.natural_acceleration:
				self.x_vel = 0
			elif self.x_vel < 0:
				self.x_vel += self.natural_acceleration
			elif self.x_vel > 0:
				self.x_vel -= self.natural_acceleration
		
		#Check Max Speed
		if self.x_vel >= self.max_speed_x:
			self.x_vel = self.max_speed_x
		elif self.x_vel <= -1*self.max_speed_x:
			self.x_vel = -1*self.max_speed_x
		if self.y_vel >= self.max_speed_y:
			self.y_vel = self.max_speed_y
		elif self.y_vel <= -1*self.max_speed_y:
			self.y_vel = -1*self.max_speed_y
		
		self.collisionExclusions = [self.grenade]
		#Update position one pixel at a time, checking for collisions each pixel to prevent noclip
		if (self.x_vel<0):
			for i in range(abs(int(self.x_vel))):
				self.rect.left += -1
				if checkForCollisions(currGrid,self,self.collisionExclusions):
					break
		elif (self.x_vel>0):
			for i in range(int(self.x_vel)):
				self.rect.left += 1
				if checkForCollisions(currGrid,self,self.collisionExclusions):
					break
		if (self.y_vel<0):
			for i in range(abs(int(self.y_vel))):
				self.rect.top += -1
				if checkForCollisions(currGrid,self,self.collisionExclusions):
					break
		elif (self.y_vel>0):
			for i in range(int(self.y_vel)):
				self.rect.top += 1
				if checkForCollisions(currGrid,self,self.collisionExclusions):
					break
					
		self.setImage()
		
		#Check if out of bounds
		if self.rect.bottom >= levelHeight:
			self.rect.bottom = levelHeight
			self.resetJumps()
		if self.rect.left < 0:
			self.rect.left = 0
			self.x_vel = 0
			self.x_acceleration = 0
		elif self.rect.right >= levelWidth:
			self.rect.right = levelWidth
			self.x_vel = 0
			self.x_acceleration = 0
		
		if self.controller != 0:
			#Perform other actions
			actions = {'Bullet':None, 'Grenade':None, 'MindControl':None}
			if state['A'] and not self.shooting:
				self.shooting = True
				actions['Bullet'] = self.shoot(players,BULLET_DAMAGE,self.xdirection*(BULLET_SPEED))
			elif not state['A']:
				self.shooting = False
		
			if state['B'] and not self.grenading:
				self.grenading = True
				self.grenade = self.throw(players)
				actions['Grenade'] = self.grenade
			elif not state['B']:
				try:
					self.grenade.cooking = False
				except:
					pass
				self.grenading = False
		
			if state['X']:
				self.shooting = True
				actions['MindControl']  = self.mindControl(players)
			elif not state['X']:
				self.shooting = False
			
		self.inventory.update()
		self.healthBar.update()
		
		if self.controller != 0:
			return actions
		
	def setImage(self):
		#Set Image
		if self.x_vel == 0:
			self.image = self.sprite_options[0]
			self.step = 0
		else:
			self.image = self.moving_sprites[int(self.step) % len(self.moving_sprites)]
			self.step += 1.0/self.image_tempo
		#Check to flip for going left
		if self.xdirection == -1:
			self.image = pygame.transform.flip(self.image, True, False)
			#reverse collision rectangle for reversed image

	
	def onCollision(self, collidingWith):
		"""This method is triggered when a collision is detected. Its parameters are the two objects colliding, and this method determines what happens to the player based on the collision type"""
		if collidingWith.type == "platform":
			if self.rect.left <= collidingWith.rect.right and self.rect.right >= collidingWith.rect.left:
				
				#Top collision
				if self.rect.bottom <= collidingWith.rect.top+collidingWith.rect.height/2 and\
				self.rect.bottom >= collidingWith.rect.top:
					if DEBUG:
						print "Collide top"
					#If platform is a moving platform, move player with platform
					#however, platform does not collide every frame that you are on it. Therefore, speed is only half what it should be
					try:#if colliding with a moving platform, player should move without loops because the loops mess with the proper speed
						self.y_vel = collidingWith.speedList[1]*collidingWith.directionList[1]
						self.x_acceleration = collidingWith.speedList[0]*collidingWith.directionList[0]
					except:#if platform is not moving
						self.y_vel = 0
					self.rect.bottom = collidingWith.rect.top
					self.collided = True
					self.resetJumps()
					
				#Bottom collision
				elif self.rect.top >= collidingWith.rect.bottom-collidingWith.rect.height/2 and\
				self.rect.top <= collidingWith.rect.bottom:
					if DEBUG:
						print "Collide bottom"
					self.y_vel = 0
					self.rect.top = collidingWith.rect.bottom + 1
					self.collided = True
			
			if self.rect.bottom >= collidingWith.rect.top+stair_tolerance and\
			self.rect.top <= collidingWith.rect.bottom:
				
				#Right Collision
				if self.rect.left <= collidingWith.rect.right and\
				self.rect.left >= collidingWith.rect.right-10:
					if DEBUG:
						print "Collide right"
					self.x_vel = 0
					self.rect.left = collidingWith.rect.right+1
					self.collided = True
				
				#Left Collision
				elif self.rect.right >= collidingWith.rect.left and\
				self.rect.right <= collidingWith.rect.left+10:
					if DEBUG:
						print "Collide left"
					self.x_vel = 0
					self.rect.right = collidingWith.rect.left-1
					self.collided = True
			print "COLLISION DETECTED!"
			return True
		else:
			return False
		
	def shoot(self,players,dmg,speed):
		if self.xdirection>0:#facing right
			direction = self.rect.right+self.max_speed_x+10#ensure bullet doesn't hit player while running
			bullet_dir = 1
		elif self.xdirection<0:#facing left
			direction = self.rect.left-self.max_speed_x-10
			bullet_dir = -1
		shot = Bullet(players,bullet_dir,(direction,self.rect.center[1]-30),dmg,speed,self)
		return shot
		
	def throw(self,players):
		if self.xdirection>0:#facing right
			direction = self.rect.right
			grenade_dir = 1
		elif self.xdirection<0:
			direction = self.rect.left
			grenade_dir = -1
		item = Grenade(players,grenade_dir,(direction,self.rect.top+self.rect.height/2),\
		abs(self.x_vel)+GRENADE_VELOCITY,GRENADE_VELOCITY)
		self.grenade = item
		item.player = self
		if DEBUG:
			print item.rect.midbottom
		return item
		
	def mindControl(self,players):
		if self.xdirection>0:#facing right
			direction = self.rect.right+self.max_speed_x+10
			bullet_dir = 1
		elif self.xdirection<0:
			direction = self.rect.left-self.max_speed_x-10
			bullet_dir = -1
		shot = MindControlBullet(players,bullet_dir,(direction,self.rect.center[1]-30),self)
		return shot
		
		
class Enemy(Player):
	def __init__(self, spritesheet, pos = (width/2,height), controller = 0):
		#Define sprite attributes
		pygame.sprite.Sprite.__init__(self)
		self.sprite_options = spritesheet
		self.image = self.sprite_options[0]
		self.rect = self.image.get_rect()
		
		self.type = "enemy"
		self.controller = 0
		
		#Make smaller collision rectangle
		self.rect = pygame.Rect(self.rect.left+5,self.rect.top,self.rect.width-30,self.rect.height)
		self.rect.midbottom = pos
		
		#Movement and speed variables
		self.max_speed_x = MAX_SPEED_X
		self.max_speed_y = MAX_SPEED_Y
		
		self.acceleration = 1.0
		
		self.natural_acceleration = self.acceleration/2
		
		self.xdirection = 1
		self.ydirection = 0

		self.xspeed = 0
		self.yspeed = 0		
		self.x_vel = 0
		self.y_vel = 0
		self.x_acceleration = 0
		self.y_acceleration = GRAVITY
		
		#Image variables
		self.moving_sprites = self.sprite_options
		
		self.step = 0
		self.image_tempo = 6.0
		
		#State variables
		self.jumps_left = 0
		self.jumped = False
		
		self.shooting = False
		self.grenading = False
		self.controlledBy = 0
		self.grenade = 0
		
		self.collided = False
		
		#Health
		self.maxHealth = 300.0
		self.health = self.maxHealth

		#Collision Detection
		self.squaresImIn = []
		
		#Sounds
		self.die_sound = enemy_die
		self.hurt_sound = enemy_hurt
	
	def ai(self,players):
		#Basic AI, randomly shoot and randomly change direction
		if (random.randint(0,10) == 9):
			bullets.add(self.shoot(players,BULLET_DAMAGE,self.xdirection*(BULLET_SPEED)))
	
		if (random.randint(0,20) == 19):
			self.xdirection *= -1

	def update(self, players, currGrid):
		
		if self.controller == 0: 
			self.ai(players)
		else:
			state = self.controller.getState()
		
		#Test to see if unit is dead
		if self.health <= 0:
			sfx.play(self.die_sound)
			self.kill()
			return
		
		#Get direction being pressed and update accordingly
		if self.controller!=0:
			self.x_acceleration = state['L_R']*self.acceleration
		
		if self.x_acceleration < 0:
			self.xdirection = -1
		elif self.x_acceleration > 0:
			self.xdirection = 1
		
		if self.controller!=0:
			if state['U_D'] == -1 and self.jumps_left > 0 and not self.jumped:
				sfx.play(jump_sound)
				self.y_vel = -18
				self.jumped = True
				self.jumps_left -= 1
			if state['U_D'] != -1:
				self.jumped = False

		self.x_vel += self.x_acceleration
		self.y_vel += self.y_acceleration
		
		#Check for deceleration
		if self.x_acceleration == 0:
			
			if self.x_vel <= self.natural_acceleration and self.x_vel >= -1*self.natural_acceleration:
				self.x_vel = 0
			elif self.x_vel < 0:
				self.x_vel += self.natural_acceleration
			elif self.x_vel > 0:
				self.x_vel -= self.natural_acceleration
		
		#Check Max Speed
		if self.x_vel >= self.max_speed_x:
			self.x_vel = self.max_speed_x
		elif self.x_vel <= -1*self.max_speed_x:
			self.x_vel = -1*self.max_speed_x
		if self.y_vel >= self.max_speed_y:
			self.y_vel = self.max_speed_y
		elif self.y_vel <= -1*self.max_speed_y:
			self.y_vel = -1*self.max_speed_y
		
		self.collisionExclusions = [self.grenade]
		
		#Update position one pixel at a time, checking for collisions each pixel to prevent noclip
		if (self.x_vel<0):
			for i in range(abs(int(self.x_vel))):
				self.rect.left += -1
				if checkForCollisions(currGrid,self,self.collisionExclusions):
					break
		elif (self.x_vel>0):
			for i in range(int(self.x_vel)):
				self.rect.left += 1
				if checkForCollisions(currGrid,self,self.collisionExclusions):
					break
		if (self.y_vel<0):
			for i in range(abs(int(self.y_vel))):
				self.rect.top += -1
				if checkForCollisions(currGrid,self,self.collisionExclusions):
					break
		elif (self.y_vel>0):
			for i in range(int(self.y_vel)):
				self.rect.top += 1
				if checkForCollisions(currGrid,self,self.collisionExclusions):
					break
					
		self.setImage()
		
		#Check if out of bounds
		if self.rect.bottom >= levelHeight:
			self.rect.bottom = levelHeight
			self.resetJumps()
		if self.rect.left < 0:
			self.rect.left = 0
			self.x_vel = 0
			self.x_acceleration = 0
		elif self.rect.right >= levelWidth:
			self.rect.right = levelWidth
			self.x_vel = 0
			self.x_acceleration = 0
			
		if (self.controller!=0):
			#Perform other actions
			actions = {'Bullet':None, 'Grenade':None}
			if state['A'] and not self.shooting:
				self.shooting = True
				actions['Bullet'] = self.shoot(players,BULLET_DAMAGE,self.xdirection*(BULLET_SPEED))
			elif not state['A']:
				self.shooting = False
		
			if state['B'] and not self.grenading:
				self.grenading = True
				self.grenade = self.throw(players)
				actions['Grenade'] = self.grenade
			elif not state['B']:
				try:
					self.grenade.cooking = False
				except:
					pass
				self.grenading = False
				
			if state['Y']:
				self.controller = 0
				self.controlledBy.controller = self.controlledBy.tempController
				self.controlledBy.controlling = False
				self.controlledBy.controllee = 0
				

class Point(pygame.sprite.Sprite):
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
			
class Platform(pygame.sprite.Sprite):
	def __init__(self,pos):
		pygame.sprite.Sprite.__init__(self)
		self.image = platform_img
		self.rect = self.image.get_rect()
		self.rect.midbottom = pos
		self.on_screen = True	
		self.type = "platform"
		
		#Collision Detection
		self.squaresImIn = []
		
	def onCollision(self,collidingWith):
		pass
	
	def update(self, camera):
		if camera.pos[0] < self.rect.right and \
		camera.pos[0] + camera.windowSize[0] > self.rect.left and \
		camera.pos[1] < self.rect.bottom and \
		camera.pos[1] + camera.windowSize[1] > self.rect.top:
			self.on_screen = True
		else:
			self.on_screen = False

class MovingPlatform(Platform):
	def __init__(self, positionList, speedList):
		
		pygame.sprite.Sprite.__init__(self)
		self.image = platform_img
		self.rect = self.image.get_rect()
		self.rect.midbottom = positionList[0]
		self.on_screen = True	
		self.type = "platform"
		
		self.positionList = positionList
		self.speedList = speedList
		self.directionList = [0,0]
		self.counter = 0
		
		#Collision Detection
		self.squaresImIn = []
		
	def move(self, destination):
		if self.rect.centerx < destination[0]:
			self.directionList[0] = 1
		else:
			self.directionList[0] = -1
	
		if self.rect.centery < destination[1]:
			self.directionList[1] = 1
		else:
			self.directionList[1] = -1
	
		self.rect.centerx += self.speedList[0] * self.directionList[0]
		self.rect.centery += self.speedList[1] * self.directionList[1]
	
		if abs(self.rect.centerx - destination[0]) < self.speedList[0]:
			self.rect.centerx = destination[0]
			self.counter += 1
			
	def onCollision(self, collidingWith):
		self.directionList[0] *= -1		
		self.directionList[1] *= -1
		
	def update(self, camera):
		
		if camera.pos[0] < self.rect.right and \
		camera.pos[0] + camera.windowSize[0] > self.rect.left and \
		camera.pos[1] < self.rect.bottom and \
		camera.pos[1] + camera.windowSize[1] > self.rect.top:
			self.on_screen = True
		else:
			self.on_screen = False
		
		self.move(self.positionList[self.counter % len(self.positionList)])
		
class Bullet(pygame.sprite.Sprite):
	def __init__(self,players,dir,pos,damage,xvel,creator,sprite=BULLET_SPRITE_OPTIONS):
		#Play creation sound
		guns.play(shoot)
		
		#SPRITE
		pygame.sprite.Sprite.__init__(self)
		self.sprite_options = sprite
		self.image = self.sprite_options[0]
		self.rect = self.image.get_rect()
		if dir == 1: 
			self.rect.left,self.rect.top = pos
		elif dir == -1:
			self.rect.right,self.rect.top = pos
		
		#MOVEMENT
		self.x_vel = xvel + creator.x_vel
		self.y_vel = 0
		self.x_accell = 0
		self.y_accell = 0
		self.collided = False
		self.collisionCheckDist = max(self.rect.height,self.rect.width)
		
		#PARAMETERS
		self.damage = damage
		self.type = "bullet"
		self.creator = creator
		
		#Collision Detection
		self.squaresImIn = []
	
	def update(self, platforms, players, currGrid):
		
		self.x_vel += self.x_accell
		self.y_vel += self.y_accell
		
		self.outOfBounds()
		
		#Update position, checking for collisions each pixel
		if (self.x_vel<0):
			for i in range(abs(int(self.x_vel))):
				self.rect.left += -1
				if checkForCollisions(currGrid,self):
					break
		elif (self.x_vel>0):
			for i in range(int(self.x_vel)):
				self.rect.left += 1
				if checkForCollisions(currGrid,self):
					break
		if (self.y_vel<0):
			for i in range(abs(int(self.y_vel))):
				self.rect.top += -1
				if checkForCollisions(currGrid,self):
					break
		elif (self.y_vel>0):
			for i in range(int(self.y_vel)):
				self.rect.top += 1
				if checkForCollisions(currGrid,self):
					break
		
		if self.collided:
			self.kill()
			return
			
		#Check to flip for going left
		if self.x_vel <= 0:
			self.image = pygame.transform.flip(self.image, True, False)
	
	def onCollision(self,collidingWith):
		if collidingWith.type=="platform":
			self.collided = True
			return True
		
		if collidingWith.type=="player" or collidingWith.type=="enemy":
			collidingWith.health -= self.damage
			self.collided = True
			sfx.play(collidingWith.hurt_sound)
			return True
		
		return False
	
	def outOfBounds(self):
		self.collided = False
		if self.rect.bottom >= levelHeight:
			self.rect.bottom = levelHeight
			self.collided = True
		if self.rect.left < 0:
			self.rect.left = 0
			self.x_vel = 0
			self.x_accell = 0
			self.collided = True
		elif self.rect.right >= levelWidth:
			self.rect.right = levelWidth
			self.x_vel = 0
			self.x_accell = 0
			self.collided = True
			
class MindControlBullet(Bullet):
	def __init__(self,players,dir,pos,creator,xvel=10):
		super(MindControlBullet, self).__init__(players,dir,pos,0,xvel,creator,MINDCONTROL_BULLET_SPRITE_OPTIONS)
		
	def onCollision(self,collidingWith):
		if collidingWith.type=="enemy" and not self.creator.controlling:
			print "CONTROLLER BEFORE:",collidingWith.controller
			collidingWith.controller = self.creator.controller
			collidingWith.controlledBy = self.creator
			print "CONTROLLER AFTER:",collidingWith.controller
			self.creator.tempController = self.creator.controller
			self.creator.controller = 0
			self.creator.controlling = True
			self.creator.controllee = collidingWith
			self.collided = True
			sfx.play(mindcontrol)
			return True
		
		return False
		
class Grenade(pygame.sprite.Sprite):
	def __init__(self,players,dir,pos,x_vel=10,y_vel=10,elasticity = 0.8):
		pygame.sprite.Sprite.__init__(self)
		self.sprite_options = GRENADE_SPRITE_OPTIONS
		self.image = self.sprite_options[0]
		self.rect = self.image.get_rect()
		if dir == -1:
			self.rect.right,self.rect.top = pos
		elif dir == 1:
			self.rect.left,self.rect.top = pos
		self.type = "grenade"

		self.max_speed_x = 3*MAX_SPEED_X
		self.max_speed_y = MAX_SPEED_Y
		
		self.accell = 0.1
		self.friction = 0.10
		
		self.natural_accell = self.accell/2
		
		self.x_vel = dir*x_vel
		self.y_vel = -y_vel
		self.xdirection = 1
		self.ydirection = 0	
		self.x_accell = 0
		self.y_accell = GRAVITY
		self.elasticity = elasticity
		self.cooking = True
		self.player = 0
		
		self.fuse_length = 3*FPS
		self.counter = 0
		self.damage = GRENADE_DAMAGE
		self.explode_img = 0
		self.exploding = False
		
		self.collided = False
		self.collisionCheckDist = max(self.rect.height,self.rect.width)
		
		#Collision Detection
		self.squaresImIn = []
		
	def update(self,platforms,players,currGrid):
	
		self.counter += 1
		if self.counter == self.fuse_length:
			self.explode()
		
		if self.cooking:
			self.rect.x = self.player.rect.x+self.player.rect.width/2
			self.rect.y = self.player.rect.y+self.player.rect.height/2
			self.x_vel = self.player.xdirection*(abs(self.player.x_vel)+GRENADE_VELOCITY)
		
		if self.cooking and self.exploding:
			self.rect.midbottom = self.player.rect.midbottom
			
		if not self.cooking or self.exploding:
			
			#Apply friction
			if self.collided:
				self.x_accell = -self.x_vel*self.friction
			elif not self.collided:
				self.x_accell = 0
			
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
					if checkForCollisions(currGrid,self):
						break
			elif (self.x_vel>0):
				for i in range(int(self.x_vel)):
					self.rect.left += 1
					if checkForCollisions(currGrid,self):
						break
			if (self.y_vel<0):
				for i in range(abs(int(self.y_vel))):
					self.rect.top += -1
					if checkForCollisions(currGrid,self):
						break
			elif (self.y_vel>0):
				for i in range(int(self.y_vel)):
					self.rect.top += 1
					if checkForCollisions(currGrid,self):
						break

			self.outOfBounds()
			
			#Check to flip for going left
			if self.xdirection == -1:
				self.image = pygame.transform.flip(self.image, True, False)
		
		#Cycle exploding sprites
		if self.exploding and self.explode_img < len(explosion_sprites):
			tempbot = self.rect.midbottom
			self.image = explosion_sprites[self.explode_img]
			self.rect = self.image.get_rect()
			self.rect.midbottom = tempbot
			self.y_vel = 0
			self.explode_collision(players)
			self.explode_img += 1
		elif self.exploding and self.explode_img >= len(explosion_sprites):
			self.kill()
		
	def onCollision(self, collidingWith):
		#PLATFORM COLLISION
		if collidingWith.type=="platform":
			if self.rect.left <= collidingWith.rect.right and self.rect.right >= collidingWith.rect.left:
				
				#Top collision
				if self.rect.bottom <= collidingWith.rect.top+collidingWith.rect.height/2 and\
				self.rect.bottom >= collidingWith.rect.top:
					if DEBUG:
						print "Collide top"
					self.rect.bottom = collidingWith.rect.top
					self.collided = True
					self.bounce("vert")

				#Bottom collision
				elif self.rect.top >= collidingWith.rect.bottom-collidingWith.rect.height/2 and\
				self.rect.top <= collidingWith.rect.bottom:
					if DEBUG:
						print "Collide bottom"
					self.rect.top = collidingWith.rect.bottom
					self.collided = True
					self.bounce("vert")
	
			if self.rect.bottom >= collidingWith.rect.top+stair_tolerance and\
			self.rect.top <= collidingWith.rect.bottom:
		
				#Right Collision
				if self.rect.left <= collidingWith.rect.right and\
				self.rect.left >= collidingWith.rect.right-10:
					if DEBUG:
						print "Collide right"
					self.rect.left = collidingWith.rect.right+1
					self.collided = True
					self.bounce("horiz")
		
				#Left Collision
				elif self.rect.right >= collidingWith.rect.left and\
				self.rect.right <= collidingWith.rect.left+10:
					if DEBUG:
						print "Collide left"
					self.rect.right = collidingWith.rect.left-1
					self.collided = True
					self.bounce("horiz")
				
		return self.collided
	
	def outOfBounds(self):
		self.collided = False
		if self.rect.bottom >= levelHeight:
			self.rect.bottom = levelHeight
			self.bounce("vert")
			self.collided = True
			
		if self.rect.left < 0:
			self.rect.left = 1
			self.bounce("horiz")
			self.collided = True
			
		elif self.rect.right >= levelWidth:
			self.rect.right = levelWidth-1
			self.bounce("horiz")
			self.collided = True
		
	def bounce(self,bounce_dir):
		if bounce_dir=="vert":
			self.y_vel *= -self.elasticity
			if DEBUG:
				print "vert bounce"
		if bounce_dir=="horiz":
			if DEBUG:
				print "horiz bounce"
			self.x_vel *= -self.elasticity
			
	def explode(self):
		if DEBUG:
			print "exploding"
		guns.play(explosion)
		self.exploding = True
		self.x_vel = 0
		self.y_vel = 0
		self.y_accell = 0
		
	def explode_collision(self,players):
		for m in players:
			if abs(m.rect.x-self.rect.x)<= self.collisionCheckDist+m.rect.width and\
			abs(m.rect.y-self.rect.y)<= self.collisionCheckDist+m.rect.height:
				if pygame.sprite.collide_mask(m, self):
					m.health -= self.damage/float(len(explosion_sprites))#adjust damage to do x dmg per sprite for a total of self.damage
					if DEBUG:
						print m.health
					self.collided = True
					sfx.play(hurt)
					return self.collided
