import pygame
from Constants import *

class Item(pygame.sprite.Sprite):
	def __init__(self,itemType,position):
		pygame.sprite.Sprite.__init__(self)
		
		self.itemType = itemType
		self.image = itemImages[itemType]#get item image from dictionary
		self.rect = self.image.get_rect()
		self.rect.topleft = position
		self.collisionCheckDist = max(self.rect.width,self.rect.height)
		self.collided = False
		self.owner = 0
	
	def update(self,players):
		if self.collisionCheck(players):
			self.use()
			self.kill()
		screen.blit(self.image,self.rect)
		
	def collisionCheck(self,players):
		self.collided = False
		for player in players:
			for m in player:
				if abs(m.rect.x-self.rect.x)<= self.collisionCheckDist+m.rect.width and\
				abs(m.rect.y-self.rect.y)<= self.collisionCheckDist+m.rect.height:
					if pygame.sprite.collide_mask(m, self):
						self.owner = m
						self.owner.inventory.append(self)
						self.collided = True
						return self.collided
	def use(self):
		pass

class Medkit(Item):
	def __init__(self,position):
		super(Medkit,self).__init__('Medkit',position)
		
	def use(self):
		self.owner.health+=50
		if self.owner.health>=100:
			self.owner.health = 100
		self.kill()
		
class QuadDamage(Item):
	def __init__(self,position):
		super(QuadDamage,self).__init__('QuadDamage',position)
		
	def use(self):
		self.owner.damage
