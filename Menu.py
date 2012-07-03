from Constants import *

class Menu:
	def __init__(self,buttons,pos = (width/2-100,height/2), columns = 1):
		self.buttons = buttons
		self.numColumns = columns
		self.buttonX = width/2-100

		currentColumn = 1
		currentRow = 1
		for button in self.buttons:
			#align the buttons according to the starting position of the menu unless overriden
			if button.rect.topleft == (0,0):
				button.rect.topleft = pos[0]+(currentColumn-1)*200,pos[1]+50*(currentRow-1)
				button.textPos = (button.rect.left+button.rect.width/4,\
					button.rect.top+button.rect.height/4)				
				#reset column to 1 for the next row or increment it to finish current row
				if currentColumn == self.numColumns:
					currentColumn = 1
					currentRow += 1
				else:
					currentColumn += 1
					
					
				
		self.background = MENU_BACKGROUND
		screen.blit(self.background,(0,0))
	
	def update(self):
		for button in self.buttons:
			button.imageTimer()
			screen.blit(button.image,button.rect.topleft)
			screen.blit(button.text,button.textPos)
		
class Button(pygame.sprite.Sprite):
	def __init__(self,text,pos=(0,0)):
		pygame.sprite.Sprite.__init__(self)
		self.image_normal = BUTTON_IMAGE
		self.image_clicked = BUTTON_CLICKED_IMAGE
		self.image = self.image_normal
		self.rect = self.image.get_rect()
		self.rect.topleft = pos
		self.text = scoreFont.render(text,True,(230,255,240))
		self.textPos = (self.rect.left+self.rect.width/4,self.rect.top+self.rect.height/4)
		self.imageCounter = 0

	#activates onClick when clicked
	def clicked(self,mousePos):
		x,y = mousePos[0],mousePos[1]
		if x < self.rect.right and x > self.rect.left and y < self.rect.bottom and y > self.rect.top:
			self.image = self.image_clicked
			return True
	
	#Updates counter so that button will revert to normal image a certain interval after it was clicked
	def imageTimer(self):
		if self.imageCounter == FPS/2:
			self.imageCounter=0
			self.image = self.image_normal
		if self.image == self.image_clicked:
			self.imageCounter+=1
