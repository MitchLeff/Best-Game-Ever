import pygame, random, math, rabbyt
from pygame.locals import *
from Constants import *

#Collision class should return type of collision and object collided with
#How to make this run only once for the entire movement?
class Collision():
	def __init__(self,collidingObject,targetObject):
		self.collidingObject = collidingObject
		self.targetObject = targetObject
		self.collidedWith = [] #array of objects with which the collidingObject collided

	def checkAll(self):
		#Goes through all possible collisions
		self.collision = False
		self.checkVectorCollision()
		self.checkPolygonCollision()
		return self.collision

	def approachDirections(self,rect):
		#Relative INITIAL position of collidingObject to Target object
		#Above Target
		if rect.bottom <= self.targetObject.rect.top:
			self.aboveTarget = True
			self.underTarget = False
		#Under Target
		elif rect.top >= self.targetObject.rect.bottom:
			self.underTarget = True
			self.aboveTarget = False
		else:
			self.underTarget = False
			self.aboveTarget = False
		#To the Right of Target
		if rect.left >= self.targetObject.rect.right:
			self.rightTarget = True
			self.leftTarget = False
		#To the Left of Target
		elif rect.right <= self.targetObject.rect.left:
			self.leftTarget = True
			self.rightTarget = False
		else:
			self.leftTarget = False
			self.rightTarget = False
		#Inside of Target
		if not(self.aboveTarget or self.underTarget or self.leftTarget or self.rightTarget):
			self.insideTarget = True
		else:
			self.insideTarget = False
		
		approachDirections = [self.aboveTarget,self.underTarget,self.leftTarget,self.rightTarget,self.insideTarget]
		#print approachDirections
		return approachDirections
		
	def calcDistance(self,rect):
		xInitial,yInitial = 0,0
		if self.aboveTarget:
			yInitial = rect.bottom - self.targetObject.rect.top	
		elif self.underTarget:
			yInitial = rect.top - self.targetObject.rect.bottom	
		if self.leftTarget:
			xInitial = rect.right - self.targetObject.rect.left
		elif self.rightTarget:
			xInitial = rect.left - self.targetObject.rect.right
		return xInitial,yInitial
	
	def checkVectorCollision(self):
		#Stores expected final position of object after moving
		self.resultantPos = pygame.sprite.Sprite()
		self.resultantPos.top = self.collidingObject.rect.top + self.collidingObject.y_vel
		self.resultantPos.bottom = self.collidingObject.rect.bottom + self.collidingObject.y_vel
		self.resultantPos.left = self.collidingObject.rect.left + self.collidingObject.x_vel
		self.resultantPos.right = self.collidingObject.rect.right + self.collidingObject.x_vel

		self.initialDirections = self.approachDirections(self.collidingObject.rect)
		#Be sure to only calculate distance for objects in Player.nearbyObjects array
		self.initialDistance   = self.calcDistance(self.collidingObject.rect)
		
		self.finalDirections = self.approachDirections(self.resultantPos)
		if self.insideTarget:
			self.collision = True
			return self.collision
		self.finalDistance   = self.calcDistance(self.resultantPos)
		
	def checkPolygonCollision(self):
		distances = []
		for vertext in targetObject.vertices:
			#in actuality distance will be calculated for each vertext on object, currently just center
			distancex = self.collidingObject.rect.center[0] - vertex.x
		 	distancey = self.collidingObject.rect.center[1] - vertex.y
		 	totalDist = (distancex**2 + distancey**2)**0.5
			distances.append(totalDist)
			#need some condition that proves collision (i.e. distance <=0
			if totalDist == 0 or distancex <= 0 or distancey <= 0:
				self.collision = True
				return self.collision
		pass



#Testing sprite collision
#Arrow keys to move sprite, circle turns red upon collision
pygame.init()

width  = 150
height = 150
size   = [width, height]
screen = pygame.display.set_mode(size)
background = pygame.Surface(screen.get_size())


ball_0 = pygame.image.load("images/ball2.png").convert_alpha()
ball_1 = pygame.image.load("images/ball.png").convert_alpha()
moon = pygame.image.load("images/moon.png").convert_alpha()

BALL_IMAGE_STATES = [ball_0, ball_1]

a = pygame.sprite.Sprite()
a.image = moon
a.rect = a.image.get_rect()
a.rect.topleft = [50, 10]

b = pygame.sprite.Sprite()
b.image = BALL_IMAGE_STATES[0]
b.rect = b.image.get_rect()
b.rect.topleft = [30, 10]

clock = pygame.time.Clock()

class ball(pygame.sprite.Sprite):
	def __init__(self):
		global a
		self.image = BALL_IMAGE_STATES[0]
		self.rect = self.image.get_rect()
		self.rect.topleft = [30, 10]
		self.xdirection='none'
		self.ydirection='none'
		self.x_vel = 10
		self.y_vel = 10
		self.collisionHandler = Collision(self,a)
		#Variables for rabbyt
		self.x,self.y = self.rect.topleft[0],self.rect.topleft[1]
		self.bounding_radius =((self.rect.topleft[0]**2+self.rect.topleft[1]**2)**0.5\
		-(self.rect.bottomright[0]**2+self.rect.bottomright[1]**2)**0.5)/2
		self.bounding_radius_squared = self.bounding_radius**2
	def move(self):
		self.collisionHandler.checkAll()
		if self.xdirection == 'RIGHT':
			self.rect.left+=self.x_vel
		elif self.xdirection == 'LEFT':
			self.rect.left-=self.x_vel
		if self.ydirection == 'UP':
			self.rect.top-=self.y_vel
		elif self.ydirection == 	'DOWN':
			self.rect.top+=self.y_vel
	def borders(self):
		global width,height
		if self.rect.bottom<=0 and self.ydirection == 'UP':
			self.rect.top=height
			#print('Top Check %s' % self.rect.top)
		if self.rect.top>=height and self.ydirection == 'DOWN':#how to make this look smoother?
			self.rect.bottom=0
			#print('Bottom Check %s' % self.rect.bottom)
		if self.rect.right<=0 and self.xdirection == 'LEFT':
			self.rect.left=width
			#print('Left Check %s' % self.rect.left)
		if self.rect.left>=width and self.xdirection == 'RIGHT':#how to make this look smoother?
			self.rect.right=0
			#print('Right Check %s' % self.rect.right)

running = True
ball1 = ball()
collidees = [a]
colliders = [ball1]
while running:
	for event in pygame.event.get():
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				running = False
			if event.key == K_UP:
				ball1.ydirection = 'UP'
			if event.key == K_DOWN:
				ball1.ydirection = 'DOWN'
			if event.key == K_LEFT:
				ball1.xdirection = 'LEFT'
			if event.key == K_RIGHT:
				ball1.xdirection = 'RIGHT'#how to makes smooth controls so that you can press all 4 arrows at once?
		if event.type == KEYUP:
			ball1.xdirection = 'none'
			ball1.ydirection = 'none'
		print "Rect: "+ str(bool(pygame.sprite.collide_rect(a,ball1)))
		print "Circ: "+ str(bool(pygame.sprite.collide_circle(a,ball1)))
		print "Mask: "+ str(bool(pygame.sprite.collide_mask(a,ball1)))
		print "Vector Collision: "+ str(ball1.collisionHandler.checkAll())+"\n"
			#Vector Collision fails on right side of moon
		try:
			print "AABB:", rabbyt.collisions.aabb_collide_single(ball1.rect,collidees)
		except:
			print "Rabby AABB Collision Test failed to run."
		try:
			print "Rabbyt:", rabbyt.collisions.collide_single(colliders,collidees)
		except:
			print "Rabbyt collision test failed to run."
	ball1.move()
	ball1.borders()
	if pygame.sprite.collide_mask(a,ball1):
		ball1.image = BALL_IMAGE_STATES[1]
	else:
		ball1.image = BALL_IMAGE_STATES[0] 
	screen.fill((0,0,0))
	screen.blit(a.image, a.rect)
	screen.blit(ball1.image, ball1.rect)
	pygame.draw.rect(screen, (255,255,0), a.rect, 1)
	pygame.display.update()
	clock.tick(60)
