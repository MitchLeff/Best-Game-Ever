from Collision import *
from Constants import *
from HUD import *
from ObjectLists import *
import pygame, random, sys, glob, pickle

init()
#All sprites must now have an onCollision(Sprite collidingWith) method that defines how each sprite type reacts to a collision with a different type of object#

#Furthermore, all sprites need a self.spriteType variable defining what type of sprite unless Python has a built-in instanceOf function#
class Bill(pygame.sprite.Sprite):
	global width, height
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
		
		#Collision Detection
		self.squaresImIn = []

	def update(self):
		if self.mode == 'fire':
			self.rect.right += self.speed*self.direction
		elif self.mode == 'die':
			self.y_vel += GRAVITY
			self.rect.top += self.y_vel
		if self.rect.right < -10 or self.rect.left > width+10 or self.rect.top > height + 10:
			self.kill()

class Player(pygame.sprite.Sprite):
	global width, height
	def __init__(self, spritesheet, controller, number):
		pygame.sprite.Sprite.__init__(self)
		
		self.controller = controller
		self.player_number = number
		self.playerNum = 1
		self.type = "player"
		
		self.sprite_options = spritesheet
		self.image = self.sprite_options[0]
		self.rect = self.image.get_rect()
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
		
		self.collided = False
		self.collisionCheckDist = max(self.rect.height,self.rect.width)
		
		self.maxHealth = 100.0
		self.health = self.maxHealth
		self.healthBar = HealthBar(self)
		self.inventory = Inventory(self)
		self.currentItems = []

		#Collision Detection
		self.squaresImIn = []
	
	def resetJumps(self):
		self.jumped = False
		self.jumps_left = 2
	
	def update(self, players, platforms):
		#Joystick compatible
		
		#Get the state of the controller to determine how to update
		state = self.controller.getState()
		
		#Test to see if unit is dead
		if self.health <= 0:
			sfx.play(die_sound)
			self.kill()
			return self.player_number
		
		#Get direction being pressed and update accordingly
		self.x_acceleration = state['L_R']*self.acceleration
		
		if self.x_acceleration < 0:
			self.xdirection = -1
		elif self.x_acceleration > 0:
			self.xdirection = 1
		
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
		
		#Update position
		if (self.x_vel<0):
			for i in range(abs(int(self.x_vel))):
				self.rect.left += -1
		elif (self.x_vel>0):
			for i in range(int(self.x_vel)):
				self.rect.left += 1
		if (self.y_vel<0):
			for i in range(abs(int(self.y_vel))):
				self.rect.top += -1
		elif (self.y_vel>0):
			for i in range(int(self.y_vel)):
				self.rect.top += 1
					
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
			
		self.inventory.update()
		self.healthBar.update()
		
		return actions
		
	def onCollision(self, collidingWith):
		"""This method is triggered when a collision is detected. Its parameters are the two objects colliding, and this method determines what happens to the player based on the collision type"""
		if collidingWith.type == "platform":
			if self.rect.left <= collidingWith.rect.right and self.rect.right >= collidingWith.rect.left:
				
				#Top collision
				if self.rect.bottom <= collidingWith.rect.top+collidingWith.rect.height/2 and\
				self.rect.bottom >= collidingWith.rect.top:
					if DEBUG:
						print "Collide top"
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
					self.rect.top = collidingWith.rect.bottom - 1
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
		
	def shoot(self,players,dmg,speed):
		if self.xdirection>0:#facing right
			direction = self.rect.right+self.max_speed_x+10#ensure bullet doesn't hit player while running
			bullet_dir = 1
		elif self.xdirection<0:#facing left
			direction = self.rect.left-self.max_speed_x-10
			bullet_dir = -1
		shot = Bullet(players,bullet_dir,(direction,self.rect.top+self.rect.height/2),dmg,speed)
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
	def __init__(self,players,dir,pos,damage,xvel,sprite=BULLET_SPRITE_OPTIONS):
		#Play creation sound
		guns.play(shoot)
		
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
		self.type = "bullet"
		
		#Collision Detection
		self.squaresImIn = []
	def update(self, platforms, players):

		self.x_vel += self.x_accell
		self.y_vel += self.y_accell
		
		#Update position
		if (self.x_vel<0):
			for i in range(abs(int(self.x_vel))):
				self.rect.left += -1
#				if self.collisioncheck(platforms,players):
#					break 
		elif (self.x_vel>0):
			for i in range(int(self.x_vel)):
				self.rect.left += 1
#				if self.collisioncheck(platforms,players):
#					break
		if (self.y_vel<0):
			for i in range(abs(int(self.y_vel))):
				self.rect.top += -1
#				if self.collisioncheck(platforms,players):
#					break
		elif (self.y_vel>0):
			for i in range(int(self.y_vel)):
				self.rect.top += 1
#				if self.collisioncheck(platforms,players):
#					break
		if self.collided or self.rect.left > levelWidth or self.rect.right < 0:
			self.kill()
			return
			
		#Check to flip for going left
		if self.x_vel <= 0:
			self.image = pygame.transform.flip(self.image, True, False)
	
	def onCollision(self,collidingWith):
		pass
	
	def collisioncheck(self,platforms,players):
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
								#self.rect.bottom = p.rect.top
								self.collided = True
							#Bottom collision
							elif self.rect.top >= p.rect.bottom-p.rect.height/2 and\
							self.rect.top <= p.rect.bottom:
								self.y_vel = 0
								self.jumped = True
								self.jump_frames = 0
								#self.rect.top = p.rect.bottom
								self.collided = True
						
						if self.rect.bottom >= p.rect.top and\
						self.rect.top <= p.rect.bottom:
							#Right Collision
							if self.rect.left <= p.rect.right and\
							self.rect.left >= p.rect.right-10:
								self.x_vel = 0
								self.jumped = True
								self.jump_frames = 0
								#self.rect.left = p.rect.right+1
								self.collided = True
							#Left Collision
							elif self.rect.right >= p.rect.left and\
							self.rect.right <= p.rect.left+10:
								self.x_vel = 0
								self.jumped = True
								self.jump_frames = 0
								#self.rect.right = p.rect.left-1
								self.collided = True
		for m in players:
			if abs(m.rect.x-self.rect.x)<= self.collisionCheckDist+m.rect.width and\
			abs(m.rect.y-self.rect.y)<= self.collisionCheckDist+m.rect.height:
				if pygame.sprite.collide_mask(m, self):
					m.health -= self.damage
					if DEBUG:
						print m.health
					self.collided = True
					hurt.play()
					return self.collided
		
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
		
	def update(self,platforms,players):
	
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
#					if self.collisioncheck(platforms,players):
#						break 
			elif (self.x_vel>0):
				for i in range(int(self.x_vel)):
					self.rect.left += 1
#					if self.collisioncheck(platforms,players):
#						break
			if (self.y_vel<0):
				for i in range(abs(int(self.y_vel))):
					self.rect.top += -1
#					if self.collisioncheck(platforms,players):
#						break
			elif (self.y_vel>0):
				for i in range(int(self.y_vel)):
					self.rect.top += 1
#					if self.collisioncheck(platforms,players):
#						break
			
			#Check to flip for going left
			if self.xdirection == -1:
				self.image = pygame.transform.flip(self.image, True, False)
		
		#Cycle exploding sprites
		if self.exploding and self.explode_img < len(explosion_sprites):
			tempbot = self.rect.midbottom
			self.image = explosion_sprites[self.explode_img]
			self.rect = self.image.get_rect()
			self.collisionCheckDist = max(self.rect.height,self.rect.width)
			self.rect.midbottom = tempbot
			self.y_vel = 0
			self.explode_collision(players)
			self.explode_img += 1
		elif self.exploding and self.explode_img >= len(explosion_sprites):
			self.kill()
		
	def onCollision(self, collidingWith):
		pass
	
	def collisioncheck(self,platforms,players):
		self.collided = False
		if self.rect.bottom >= levelHeight-HUDSIZE:
			self.rect.bottom = levelHeight-HUDSIZE-1
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
			
		#PLATFORM COLLISIONS
		for p in platforms:
			if abs(p.rect.x-self.rect.x)<= self.collisionCheckDist+p.rect.width and abs(p.rect.y-self.rect.y)<= self.collisionCheckDist+p.rect.height:#Check this code
				if pygame.sprite.collide_mask(p, self):
						if self.rect.left <= p.rect.right and self.rect.right >= p.rect.left:
							
							#Top collision
							if self.rect.bottom <= p.rect.top+p.rect.height/2 and\
							self.rect.bottom >= p.rect.top:
								if DEBUG:
									print "Collide top"
								self.rect.bottom = p.rect.top
								self.collided = True
								self.bounce("vert")

							#Bottom collision
							elif self.rect.top >= p.rect.bottom-p.rect.height/2 and\
							self.rect.top <= p.rect.bottom:
								if DEBUG:
									print "Collide bottom"
								self.rect.top = p.rect.bottom
								self.collided = True
								self.bounce("vert")
						
						if self.rect.bottom >= p.rect.top+stair_tolerance and\
						self.rect.top <= p.rect.bottom:
							
							#Right Collision
							if self.rect.left <= p.rect.right and\
							self.rect.left >= p.rect.right-10:
								if DEBUG:
									print "Collide right"
								self.rect.left = p.rect.right+1
								self.collided = True
								self.bounce("horiz")
							
							#Left Collision
							elif self.rect.right >= p.rect.left and\
							self.rect.right <= p.rect.left+10:
								if DEBUG:
									print "Collide left"
								self.rect.right = p.rect.left-1
								self.collided = True
								self.bounce("horiz")
		return self.collided
		
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
					hurt.play()
					return self.collided
