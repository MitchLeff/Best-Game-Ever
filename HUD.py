import pygame
from Constants import *

class HealthBar():
	def __init__(self,owner):
		self.owner = owner
		self.height = 10
		self.length = self.owner.maxHealth
		#Xposition
		self.position = self.owner.playerNum*10 + (self.owner.playerNum-1)*self.length
		self.text = scoreFont.render("Player %s" % self.owner.playerNum, True, (255,255,255))
		self.rect = self.text.get_rect()
		
	def update(self):
		self.rect.bottomleft = self.position,32
		#Draw red bar
		pygame.draw.rect(HUD, (140,20,10), \
		(self.owner.health, self.rect.bottom+10, 100-self.owner.health, self.height))
		#Draw green bar
		pygame.draw.rect(HUD, (80,255,60), \
		(self.rect.left, self.rect.bottom+10, self.owner.health, self.height))
		HUD.blit(self.text, self.rect)
		
class Inventory():
	def __init__(self,owner):
		self.owner = owner
		self.height = 10
		self.length = 100
		self.position = self.owner.playerNum*10 + (self.owner.playerNum-1)*self.length
		self.text = scoreFont.render("Inventory", True, (255,255,255))
		self.rect = self.text.get_rect()
			
		#assuming items are all 32x32 images looks like grid: --|--
		self.rect.bottomleft = self.position,82
		self.itemPosition = [(self.rect.left,self.rect.bottom),\
		(self.rect.left+33,self.rect.bottom),\
		(self.rect.left,self.rect.bottom+33),(self.rect.left+33,self.rect.bottom+33)]

	def update(self):
		HUD.blit(self.text,self.rect)
		for i in enumerate(self.owner.currentItems):
			pos = self.itemPosition[i[0]]
			print pos
			img = i[1].image
			HUD.blit(img,pos)
