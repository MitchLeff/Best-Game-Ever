#!usr/bin/python
import pygame
from Constants import *
#Platforms Class
class platform(pygame.sprite.Sprite):
	def __init__(self,pos):
		pygame.sprite.Sprite.__init__(self)
		self.image = platform_img
		self.rect = self.image.get_rect()
		self.rect.midbottom = pos	

#How to make platforms accessible by all sprite classes and by main class?
	#temp answer - all sprite classes take platforms as parameter
