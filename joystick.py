import pygame, time
from Controller import *
from pygame.locals import *

pygame.init()
pygame.joystick.init()
pygame.display.set_mode()
pygame.mouse.set_visible(True)
pygame.display.set_caption("Multiplayer Arena Test")

width  = 200
height = 200#max(300,background_image.get_height())
size   = [width, height]
screen = pygame.display.set_mode(size)

c1 = Joystick(0)
c2 = Keyboard(K_n, K_j, K_b, K_h, K_g, K_k, K_y, K_o, K_LSHIFT, K_LCTRL, K_a, K_d, K_w, K_s)


running = True
while running:
	for event in pygame.event.get():
		if event.type == KEYDOWN:	
			if event.key == K_ESCAPE:
				running = False
	print c1.getState()
	print ''
	print c1.getState()
	time.sleep(1)	