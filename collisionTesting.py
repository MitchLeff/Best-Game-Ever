#CONSTANTS
FPS = 60
GRID_SQUARE_WIDTH = 40

#IMPORTS
import pygame, random
from pygame.locals import *

clock = pygame.time.Clock()
pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.display.set_mode()
pygame.mouse.set_visible(False)
pygame.display.set_caption("Collision Testing")

miniBill = pygame.image.load("images/miniBill.png").convert_alpha()

width  = 800
height = 400
size   = [width, height]
screen = pygame.display.set_mode(size)

class gridSquare:
	def __init__(self, width, topLeft, listOfSquares):
		self.width = width
		self.topLeft = topLeft
		self.rect = pygame.Rect(self.topLeft[0], self.topLeft[1], self.width+1, self.width+1)
		listOfSquares.append(self)
		adjacentSquares = []
		objectsContained = []
		
	def draw(self):
		pygame.draw.rect(screen, (0,0,0), self.rect, 1)

class bill(pygame.sprite.Sprite):
	def __init__(self, *groups):
		directions = [(1,0), (0,1), (-1,0), (0,-1)]
		pygame.sprite.Sprite.__init__(self)

		self.image = miniBill
		self.rect = self.image.get_rect()

		dirChoice = random.randint(0,3)
		
		self.dir = directions[dirChoice]
		self.speed = 2
		
		self.rect.center = (random.randint(self.rect.width, width - self.rect.width), random.randint(self.rect.height, height - self.rect.height))
		
		if dirChoice == 0:
			pass		elif dirChoice == 1:
			self.image = pygame.transform.rotate(self.image, -90)
		elif dirChoice == 2:
			self.image = pygame.transform.rotate(self.image, 180)
		elif dirChoice == 3:
			self.image = pygame.transform.rotate(self.image, 90)

		for g in groups:
			g.add(self)

		self.mode = "fire"

	def update(self):
		if self.mode == 'fire':
			self.rect.centerx += self.speed*self.dir[0]
			self.rect.centery += self.speed*self.dir[1]
			
		if self.rect.right >= width or self.rect.left <0 or self.rect.top < 0 or self.rect.bottom >= height:
			self.image = pygame.transform.rotate(self.image, 180)
			self.dir = [self.dir[0]*-1, self.dir[1]*-1]
		screen.blit(self.image, self.rect.topleft)
			
bills = pygame.sprite.Group()

gridSquares = []
for s in range(0, width, GRID_SQUARE_WIDTH):
	for ss in range(0, height, GRID_SQUARE_WIDTH):
		gridSquare(GRID_SQUARE_WIDTH, (s,ss), gridSquares)

running = True
cycles = 0

for i in range(0,10):
	bill(bills)
while running:
	clock.tick(FPS)
	print int(clock.get_fps()), len(bills.sprites())
	
	for event in pygame.event.get():
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				running = False
			elif event.key == K_SPACE:
				bill(bills)
				
	screen.fill((255,255,255))
	for b in bills:
		for bb in bills:
			if pygame.sprite.collide_mask(b, bb) and b != bb:
				print "HIT"
		b.update()
	
	for s in gridSquares:
		s.draw()
	
	pygame.display.flip()
	
	cycles += 1