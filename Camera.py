

class Camera:
	def __init__(self, mainPlayer, windowSize, levelSize):
		self.mainPlayer = mainPlayer
		self.windowSize = windowSize
		self.levelSize = levelSize
		
		self.pos = [0,0]
		
	def update(self):
		self.pos = [0 - self.mainPlayer.rect.centerx + self.windowSize[0]/2, 0 - self.mainPlayer.rect.centery + self.windowSize[1]/2]