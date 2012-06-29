class Camera:
	def __init__(self, mainPlayer, windowSize, levelSize):
		self.mainPlayer = mainPlayer
		self.windowSize = windowSize
		self.levelSize = levelSize
		
		self.pos = [0,0]
		
	def update(self):
		self.pos = [self.mainPlayer.rect.centerx - self.windowSize[0]/2, self.mainPlayer.rect.centery - self.windowSize[1]/2]
		
		#Out of Bounds Width	
		if self.pos[0] < 0:
			self.pos[0] = 0
		if self.pos[0] + self.windowSize[0] > self.levelSize[0]:
			self.pos[0] = self.levelSize[0] - self.windowSize[0]
		
		#Out of Bounds Height
		if self.pos[1] < 0:
			self.pos[1] = 0
		if self.pos[1] + self.windowSize[1] > self.levelSize[1]:
			self.pos[1] = self.levelSize[1] - self.windowSize[1]
			
	def mod(self, rect):
		return (rect[0] - self.pos[0], rect[1] - self.pos[1])
	
	def mod2(self, rect):
		return (rect[0] + self.pos[0], rect[1] + self.pos[1])
		
	def mod3(self, rect):
		return (rect[0] - self.pos[0], rect[1] - self.pos[1], rect.width, rect.height)
