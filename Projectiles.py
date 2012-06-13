#Base class for bullet-type projectiles
import pygame

from sprite_sheet_loader import *
from Constants import *
from ObjectLists import *

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
		
	def update(self, platforms, players):

		self.x_vel += self.x_accell
		self.y_vel += self.y_accell
		
		#Update position
		if (self.x_vel<0):
			for i in range(abs(int(self.x_vel))):
				self.rect.left += -1
				if self.collisioncheck(platforms,players):
					break 
		elif (self.x_vel>0):
			for i in range(int(self.x_vel)):
				self.rect.left += 1
				if self.collisioncheck(platforms,players):
					break
		if (self.y_vel<0):
			for i in range(abs(int(self.y_vel))):
				self.rect.top += -1
				if self.collisioncheck(platforms,players):
					break
		elif (self.y_vel>0):
			for i in range(int(self.y_vel)):
				self.rect.top += 1
				if self.collisioncheck(platforms,players):
					break
		if self.collided or self.rect.left > levelWidth or self.rect.right < 0:
			self.kill()
			return
			
		#Check to flip for going left
		if self.x_vel <= 0:
			self.image = pygame.transform.flip(self.image, True, False)
		
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
					if self.collisioncheck(platforms,players):
						break 
			elif (self.x_vel>0):
				for i in range(int(self.x_vel)):
					self.rect.left += 1
					if self.collisioncheck(platforms,players):
						break
			if (self.y_vel<0):
				for i in range(abs(int(self.y_vel))):
					self.rect.top += -1
					if self.collisioncheck(platforms,players):
						break
			elif (self.y_vel>0):
				for i in range(int(self.y_vel)):
					self.rect.top += 1
					if self.collisioncheck(platforms,players):
						break
			
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
		
	def collisioncheck(self,platforms,players):
		self.collided = False
		if self.rect.bottom >= levelHeight:
			self.rect.bottom = levelHeight-1
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
