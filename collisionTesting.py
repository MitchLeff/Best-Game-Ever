#CONSTANTS
FPS = 60  
GRID_SQUARE_WIDTH = 22
STARTING_BILLS = 30
DRAW_SQUARES = False
INCREMENT = False
COLLISSION_DETECTION_MODE = 1 #0 for n^2 object-to-object checks, 1 for zone based checks
SPEED = 2

#IMPORTS
import pygame, random, time
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

bills = pygame.sprite.Group()

gridSquares = []
priorityCheckList = []

class gridSquare:
	def __init__(self, topLeft):
		self.topLeft = topLeft
		self.rect = pygame.Rect(self.topLeft[0], self.topLeft[1], GRID_SQUARE_WIDTH+1, GRID_SQUARE_WIDTH+1)
		self.adjacentSquares = []
		self.objectsContained = []
		
	def draw(self):
		if DRAW_SQUARES:
			pygame.draw.rect(screen, (0,0,0), self.rect, 1)

class bill(pygame.sprite.Sprite):
	def __init__(self, *groups):
		directions = [(1,0), (0,1), (-1,0), (0,-1)]
		pygame.sprite.Sprite.__init__(self)

		self.image = miniBill

		dirChoice = random.randint(0,3)
		
		self.dir = directions[dirChoice]
		self.speed = SPEED
		

		self.squaresImIn = []

		if dirChoice == 0:
			pass		elif dirChoice == 1:
			self.image = pygame.transform.rotate(self.image, -90)
		elif dirChoice == 2:
			self.image = pygame.transform.rotate(self.image, 180)
		elif dirChoice == 3:
			self.image = pygame.transform.rotate(self.image, 90)

		self.rect = self.image.get_rect()
		self.rect.topleft = (random.randint(0, width - self.rect.width - 1), random.randint(0, height - self.rect.height - 1))

		for g in groups:
			g.add(self)

		self.mode = "fire"

	def updateGrid(self):
		leftMostColumn = self.rect.left/GRID_SQUARE_WIDTH
		upperMostRow = self.rect.top/GRID_SQUARE_WIDTH

		squaresWide = self.rect.width/GRID_SQUARE_WIDTH+1
		squaresTall = self.rect.height/GRID_SQUARE_WIDTH+1

		for s in self.squaresImIn:
			s.objectsContained.remove(self)
			
		self.squaresImIn = []

		for i in range(max(0,leftMostColumn-1), min(width/GRID_SQUARE_WIDTH, leftMostColumn+squaresWide+1)):
			for j in range(max(0,upperMostRow-1), min(height/GRID_SQUARE_WIDTH, upperMostRow+squaresTall+1)):
				gridSquares[i][j].objectsContained.append(self)
				self.squaresImIn.append(gridSquares[i][j])
				
	def update(self):
		if self.mode == 'fire':
			self.rect.centerx += self.speed*self.dir[0]
			self.rect.centery += self.speed*self.dir[1]
			
		if self.rect.right >= width or self.rect.left <0 or self.rect.top < 0 or self.rect.bottom >= height:
			self.image = pygame.transform.rotate(self.image, 180)
			self.dir = [self.dir[0]*-1, self.dir[1]*-1]
		screen.blit(self.image, self.rect.topleft)

def resetGrid():
	global width, GRID_SQUARE_WIDTH, gridSquares
	gridSquares = []
	for s in range(0, width, GRID_SQUARE_WIDTH):
		row = []
		for ss in range(0, height, GRID_SQUARE_WIDTH):
			row.append(gridSquare((s,ss)))
		gridSquares.append(row)

resetGrid()

running = True
cycles = 0

for i in range(0,STARTING_BILLS):
	bill(bills)

if INCREMENT:
	maxFPS = 1
	bestSquareSize = 1
	ss = 0

while running:
	clock.tick(FPS)
	
	for event in pygame.event.get():
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				running = False
				quit()
			elif event.key == K_SPACE:
				bill(bills)
			elif event.key == K_p:
				time.sleep(5)
				
	screen.fill((255,255,255))
	
	if COLLISSION_DETECTION_MODE == 1:
		for row in gridSquares:
			for square in row:
				if len(square.objectsContained) > 1:
					if DRAW_SQUARES:
						pygame.draw.rect(screen, (0,0,255), square.rect)
					for b in square.objectsContained:
						for bb in square.objectsContained:
							if pygame.sprite.collide_mask(b, bb) and b != bb:
								if DRAW_SQUARES:
									pygame.draw.rect(screen, (255,0,0), square.rect)
								print "HIT"
				elif len(square.objectsContained) == 1:
					if DRAW_SQUARES:
						pygame.draw.rect(screen, (0,255,0), square.rect)
				
				square.draw()
				
	for b in bills:
		if COLLISSION_DETECTION_MODE == 0:
			for bb in bills:
				if pygame.sprite.collide_mask(b, bb) and b != bb:
					print "HIT"
		b.updateGrid()
		b.update()
		
	if INCREMENT:
		ss += clock.get_fps()
		if cycles % 100 == 0:
			avgFPS = ss/100.0
			if avgFPS > maxFPS:
				maxFPS = avgFPS
				bestSquareSize = GRID_SQUARE_WIDTH
				print maxFPS, bestSquareSize
			GRID_SQUARE_WIDTH += 1
			if GRID_SQUARE_WIDTH >= 50:
				print maxFPS, bestSquareSize
				quit()
			ss = 0
			
			resetGrid()
	else:
		print clock.get_fps()
			
	pygame.display.flip()
	
	cycles += 1