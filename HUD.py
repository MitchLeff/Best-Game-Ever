import pygame
from Constants import *

class healthBar():
	def __init__(self,owner):
		self.owner = owner
		self.height = 10
		self.length = self.owner.health
		self.position = self.owner.playerNum*10 + (self.owner.playerNum-1)*self.length
		self.text = scoreFont.render("Player %s" % self.owner.playerNum, True, (255,255,255))
		self.rect = self.text.get_rect()
		
	def update(self):
		#if self.owner.health > 0:
		self.rect.bottomleft = self.position,height-HUDSIZE/2-10
		pygame.draw.rect(screen, (80,255,60), \
		(self.position, height-HUDSIZE/2, self.owner.health, self.height))
		screen.blit(self.text, self.rect)
