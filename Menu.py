from Constants import *

class Menu:
	def __init__(self,buttons,pos = (0,0)):
		self.buttons = buttons
		self.background = MENU_BACKGROUND
		screen.blit(self.background,pos)
	
	def update(self):
		for button in self.buttons:
			screen.blit(button.image,button.rect.topleft)
			screen.blit(button.text,button.textPos)
		
class Button(pygame.sprite.Sprite):
	def __init__(self,pos):
		pygame.sprite.Sprite.__init__(self)
		self.image_normal = BUTTON_IMAGE
		self.image_clicked = BUTTON_CLICKED_IMAGE
		self.image = self.image_normal
		self.rect = self.image.get_rect()
		self.rect.topleft = pos
		
	def onClick(self):
		pass
	
	#activates onClick when clicked
	def clicked(self,mousePos):
		x,y = mousePos[0],mousePos[1]
		if x < self.rect.right and x > self.rect.left and y < self.rect.bottom and y > self.rect.top:
			return self.onClick()
		
class StartGame(Button):
	def __init__(self,pos):
		super(StartGame, self).__init__(pos)
		self.text = scoreFont.render("Start Game!", True, (230,255,240))
		self.textPos = (self.rect.left+self.rect.width/4,self.rect.top+self.rect.height/4)
	
	def onClick(self):
		self.image = self.image_clicked
		return True
