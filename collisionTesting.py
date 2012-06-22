#CONSTANTS
FPS = 900
DEFAULT_GRID_SQUARE_WIDTH = 22 #Default grid square width to be used
GRID_SQUARE_WIDTH = DEFAULT_GRID_SQUARE_WIDTH
STARTING_BILLS = 60
DRAW_SQUARES = False #Will only work on Grid-zone mode.
INCREMENT = False #Increments the grid square size every INCREMENT_CYCLES cycles
INCREMENT_CYCLES = 20 #Number of cycles to go through to obtain an average fps for each grid size
INCREMENT_RANGE = 190 #Number of times to increment the grid square size
INCREMENTATIONS = 100 #Number of objects to make while incrementing
COLLISSION_DETECTION_MODE = 1 #0 for n^2 object-to-object checks, 1 for grid-zone based checks, 2 for priority checklist
SPEED = 2 #Speed at which bills move
PRINT_HITS = False #Will print 'HIT' each time objects collide

#IMPORTS
import pygame, random, time
from pygame.locals import *

#Initializations
clock = pygame.time.Clock()
pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.display.set_mode()
pygame.mouse.set_visible(False)
pygame.display.set_caption("Collision Testing")

#Load images
miniBill = pygame.image.load("images/miniBill.png").convert_alpha()

#Screen setup
width  = 800
height = 400
size   = [width, height]
screen = pygame.display.set_mode(size)

bills = pygame.sprite.Group()

gridSquares = [] #The Grid
priorityCheckList = [] #Checklist of squares to be checked (for COLLISSION_DETECTION_MODE 2)
increment_data = [] #Data stored during an Incrementation run

class gridSquare:
	"""A square on the grid, used to determine if 2 objects should be compared"""
	def __init__(self, topLeft):
		self.topLeft = topLeft
		self.rect = pygame.Rect(self.topLeft[0], self.topLeft[1], GRID_SQUARE_WIDTH+1, GRID_SQUARE_WIDTH+1)
		self.adjacentSquares = []
		self.objectsContained = []
		
	def draw(self):
		if DRAW_SQUARES:
			pygame.draw.rect(screen, (0,0,0), self.rect, 1)

class bill(pygame.sprite.Sprite):
	"""Sprite objects that move and get checked for collisions"""
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
		"""Updates the grid by putting self into square objects and putting square objects in my list"""
		leftMostColumn = self.rect.left/GRID_SQUARE_WIDTH
		upperMostRow = self.rect.top/GRID_SQUARE_WIDTH

		squaresWide = self.rect.width/GRID_SQUARE_WIDTH+1
		squaresTall = self.rect.height/GRID_SQUARE_WIDTH+1

		#Remove myself from the objects contained list of all squares that I am in
		for s in self.squaresImIn:
			s.objectsContained.remove(self)
		
		#Clear out list of squares I'm in
		self.squaresImIn = []
		
		#Calculate the left most and upper most square I'm in
		zone_left = max(0,leftMostColumn)
		zone_top = max(0,upperMostRow)
		
		#Determine how far over and down I go
		zone_width = min(width/GRID_SQUARE_WIDTH, leftMostColumn+squaresWide)
		zone_height = min(height/GRID_SQUARE_WIDTH, upperMostRow+squaresTall)
		
		#Determine if I'm OVER THE LINE, MARK IT ZERO
		if self.rect.right >= (leftMostColumn + squaresWide) * GRID_SQUARE_WIDTH:
			zone_width += 1
		if self.rect.bottom >= (upperMostRow + squaresTall) * GRID_SQUARE_WIDTH:
			#League game, Smokey.
			zone_height += 1
		
		#Add myself to the list of objects contained for the squares I'm in and add them to my list of Square's I'm in
		for i in range(zone_left, zone_width):
			for j in range(zone_top, zone_height):
				gridSquares[i][j].objectsContained.append(self)
				self.squaresImIn.append(gridSquares[i][j])
				if COLLISSION_DETECTION_MODE == 2: #Add myself to the priority checklist to be checked
					priorityCheckList.append(gridSquares[i][j])
				
	def update(self):
		#Move along
		if self.mode == 'fire':
			self.rect.centerx += self.speed*self.dir[0]
			self.rect.centery += self.speed*self.dir[1]
		
		#Check for edge of screen and flip
		if self.rect.right >= width or self.rect.left <0 or self.rect.top < 0 or self.rect.bottom >= height:
			self.image = pygame.transform.rotate(self.image, 180)
			self.dir = [self.dir[0]*-1, self.dir[1]*-1]
		
		#Update dat grid, G
		self.updateGrid()
	
	def draw(self):
		#Drawwwwwwww
		screen.blit(self.image, self.rect.topleft)

def resetGrid(): #This function resets the grid.
	global width, GRID_SQUARE_WIDTH, gridSquares
	gridSquares = []
	for s in range(0, width+GRID_SQUARE_WIDTH+1, GRID_SQUARE_WIDTH):
		row = []
		for ss in range(0, height+GRID_SQUARE_WIDTH+1, GRID_SQUARE_WIDTH):
			row.append(gridSquare((s,ss)))
		gridSquares.append(row)

resetGrid()

running = True
cycles = 0

for i in range(0,STARTING_BILLS):
	bill(bills)

if INCREMENT:#Initialize variables for an Incrementation run
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
	bills.update()
		
	if COLLISSION_DETECTION_MODE == 0:
		for b in bills:
			for bb in bills:
				if pygame.sprite.collide_mask(b, bb) and b != bb:
					if PRINT_HITS:
						print "HIT"

	if COLLISSION_DETECTION_MODE == 1:
		c = 0
		for row in gridSquares:
			for square in row:
				if len(square.objectsContained) > 1:
					if DRAW_SQUARES:
						pygame.draw.rect(screen, (0,0,255), square.rect)
					for b in square.objectsContained:
						for bb in square.objectsContained:
							c += 1
							if pygame.sprite.collide_mask(b, bb) and b != bb:
								if DRAW_SQUARES:
									pygame.draw.rect(screen, (255,0,0), square.rect)
								if PRINT_HITS:
									print "HIT"
				elif len(square.objectsContained) == 1:
					if DRAW_SQUARES:
						pygame.draw.rect(screen, (0,255,0), square.rect)
				square.draw()
		print c
	elif COLLISSION_DETECTION_MODE == 2:
		#print len(priorityCheckList)
		c = 0
		for square in priorityCheckList:
			if len(square.objectsContained) > 1:
				if DRAW_SQUARES:
					pygame.draw.rect(screen, (0,0,255), square.rect)
				for b in square.objectsContained:
					for bb in square.objectsContained:
						c += 1
						if pygame.sprite.collide_mask(b, bb) and b != bb:
							if DRAW_SQUARES:
								pygame.draw.rect(screen, (255,0,0), square.rect)
							if PRINT_HITS:
								print "HIT"
			elif len(square.objectsContained) == 1:
				if DRAW_SQUARES:
					pygame.draw.rect(screen, (0,255,0), square.rect)
			square.draw()
		print c
		priorityCheckList = []
	
	for b in bills:
		b.draw()
	
	if INCREMENT:
		ss += clock.get_fps()
		if cycles % INCREMENT_CYCLES == 0:
			avgFPS = ss/INCREMENT_CYCLES
			if avgFPS > maxFPS:
				maxFPS = avgFPS
				bestSquareSize = GRID_SQUARE_WIDTH
				print maxFPS, bestSquareSize
			GRID_SQUARE_WIDTH += 1
			if GRID_SQUARE_WIDTH >= 200:
				print maxFPS, bestSquareSize
				quit()
			ss = 0
			
			resetGrid()
		if cycles % (INCREMENT_CYCLES * INCREMENT_RANGE) == 0:
			increment_data.append((len(bills.sprites()),maxFPS,bestSquareSize))
			bill(bills)
			maxFPS = 1
			GRID_SQUARE_WIDTH = DEFAULT_GRID_SQUARE_WIDTH
			resetGrid()
		if cycles >= INCREMENT_CYCLES * INCREMENT_RANGE * INCREMENTATIONS:
			for i in increment_data:
				print i
			running = False
			
	else:
		print clock.get_fps(), len(bills.sprites())
			
	pygame.display.flip()
	
	cycles += 1