#CONSTANTS
from Constants import *

#Running Options
COLLISSION_DETECTION_MODE = 1 #0 for n^2 object-to-object checks, 1 for grid-zone based checks, 2 for priority checklist
PRINT_HITS = False #Will print 'HIT' each time objects collide\

#IMPORTS
import pygame, random, time
from pygame.locals import *

#Initializations
clock = pygame.time.Clock()
pygame.init()
pygame.font.init()
pygame.mixer.init()

class gridSquare:
	"""A square on the grid, used to determine if 2 objects should be compared"""
	def __init__(self, topLeft):
		self.topLeft = topLeft
		self.rect = pygame.Rect(self.topLeft[0], self.topLeft[1], GRID_SQUARE_LENGTH+1, GRID_SQUARE_LENGTH+1)
		self.adjacentSquares = []
		self.objectsContained = []
		
	def draw(self, screen, camera):
		modRect = camera.mod3(self.rect)
		if len(self.objectsContained) == 1:
			pygame.draw.rect(screen, (0,255,0),modRect)
		elif len(self.objectsContained) >= 2:
			pygame.draw.rect(screen, (0,0,255),modRect)
		pygame.draw.rect(screen,(0,0,0),modRect, 1)

#class bill(pygame.sprite.Sprite):
#	"""Sprite objects that move and get checked for collisions"""
#	def __init__(self, *groups):
#		directions = [(1,0), (0,1), (-1,0), (0,-1)]
#		pygame.sprite.Sprite.__init__(self)
#
#		self.image = miniBill
#
#		dirChoice = random.randint(0,3)
#		
#		self.dir = directions[dirChoice]
#		self.speed = random.choice(range(MIN_SPEED,MAX_SPEED))
#		
#
#		self.squaresImIn = []
#
#		if dirChoice == 0:
#			pass
#		elif dirChoice == 1:
#			self.image = pygame.transform.rotate(self.image, -90)
#		elif dirChoice == 2:
#			self.image = pygame.transform.rotate(self.image, 180)
#		elif dirChoice == 3:
#			self.image = pygame.transform.rotate(self.image, 90)
#
#		self.rect = self.image.get_rect()
#		self.rect.topleft = (random.randint(0, width - self.rect.width - 1), random.randint(0, height - self.rect.height - 1))
#
#		for g in groups:
#			g.add(self)
#
#		self.mode = "fire"
#				
#	def update(self):
#		#Move along
#		if self.mode == 'fire':
#			self.rect.centerx += self.speed*self.dir[0]
#			self.rect.centery += self.speed*self.dir[1]
#		
#		#Check for edge of screen and flip
#		if self.rect.right >= width or self.rect.left <0 or self.rect.top < 0 or self.rect.bottom >= height:
#			self.image = pygame.transform.rotate(self.image, 180)
#			self.dir = [self.dir[0]*-1, self.dir[1]*-1]
#		
#		#Update dat grid, G
#		self.updateGrid()
#	
#	def draw(self,screen):
#		#Drawwwwwwww
#		screen.blit(self.image, self.rect.topleft)

def updateGrid(sprite,currGrid):
	"""Updates the grid by putting self into square objects and putting square objects in my list"""
	leftMostColumn = sprite.rect.left/GRID_SQUARE_LENGTH
	upperMostRow = sprite.rect.top/GRID_SQUARE_LENGTH

	squaresWide = sprite.rect.width/GRID_SQUARE_LENGTH+1
	squaresTall = sprite.rect.height/GRID_SQUARE_LENGTH+1

	#Remove myself from the objects contained list of all squares that I am in
	for s in sprite.squaresImIn:
		s.objectsContained.remove(sprite)
	
	#Clear out list of squares I'm in
	sprite.squaresImIn = []
	
	#Calculate the left most and upper most square I'm in
	zone_left = max(0,leftMostColumn)
	zone_top = max(0,upperMostRow)
	
	#Determine how far over and down I go
	zone_width = min(width/GRID_SQUARE_LENGTH, leftMostColumn+squaresWide)
	zone_height = min(height/GRID_SQUARE_LENGTH, upperMostRow+squaresTall)
	
	#Determine if I'm OVER THE LINE, MARK IT ZERO
	if sprite.rect.right >= (leftMostColumn + squaresWide) * GRID_SQUARE_LENGTH:
		zone_width += 1
	if sprite.rect.bottom >= (upperMostRow + squaresTall) * GRID_SQUARE_LENGTH:
		#League game, Smokey.
		zone_height += 1
	
	#Add myself to the list of objects contained for the squares I'm in and add them to my list of Square's I'm in
	for i in range(zone_left, zone_width):
		for j in range(zone_top, zone_height):
			currGrid[i][j].objectsContained.append(sprite)
			sprite.squaresImIn.append(currGrid[i][j])
			if COLLISSION_DETECTION_MODE == 2: #Add myself to the priority checklist to be checked
				priorityCheckList.append(currGrid[i][j])
	
	return currGrid

def createGrid(squareLength): #This function resets the grid.
	global levelWidth, levelHeight
	print levelWidth, levelHeight
	gridSquares = []
	for s in range(0, levelWidth+squareLength+1, squareLength):
		row = []
		for ss in range(0, levelHeight+squareLength+1, squareLength):
			row.append(gridSquare((s,ss)))
		gridSquares.append(row)
	return gridSquares

def checkForCollisions(currGrid):
	for row in currGrid:
		for square in row:
			if len(square.objectsContained) > 1:
				for b in square.objectsContained:
					print 'CHECKING:',b
					for bb in square.objectsContained:
						print 'CHECKING:',b
						if pygame.sprite.collide_mask(b, bb) and b != bb:
							print "HIT"