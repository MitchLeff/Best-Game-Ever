import pygame
from pygame.locals import *

class Controller:
	def __init__(self):
		pass

class Joystick(Controller):
	def __init__(self, joystick_number):
		self.joystick = pygame.joystick.Joystick(joystick_number)
		self.joystick.init()
	
	def getState(self):
		state = {
			'A':self.joystick.get_button(1),
			'B':self.joystick.get_button(2),
			'X':self.joystick.get_button(0),
			'Y':self.joystick.get_button(3),
			'L1':self.joystick.get_button(4),
			'R1':self.joystick.get_button(5),
			'L2':self.joystick.get_button(6),
			'R2':self.joystick.get_button(7),
			'Select':self.joystick.get_button(8),
			'Start':self.joystick.get_button(9),
			'L_R': int(round(self.joystick.get_axis(0),1)),
			'U_D': int(round(self.joystick.get_axis(1),1))
		}
		return state

class Keyboard(Controller):
	def __init__(self, A, B, X, Y, L1, R1, L2, R2, Start, Select, Left, Right, Up, Down):
		self.A = A
		self.B = B
		self.X = X
		self.Y = Y
		self.L1 = L1
		self.R1 = R1
		self.L2 = L2
		self.R2 = R2
		self.Start = Start
		self.Select = Select
		self.L = Left
		self.R = Right
		self.U = Up
		self.D = Down
	
	def getState(self):
		pressed = pygame.key.get_pressed()
		
		L_R = 0
		if (not pressed[self.L] and not pressed[self.R]) or (pressed[self.L] and pressed[self.R]):
			L_R = 0
		elif pressed[self.L]:
			L_R = -1
		elif pressed[self.R]:
			L_R = 1
		
		U_D = 0
		if (not pressed[self.U] and not pressed[self.D]) or (pressed[self.U] and pressed[self.D]):
			U_D = 0
		elif pressed[self.U]:
			U_D = -1
		elif pressed[self.D]:
			U_D = 1
			
		state = {
			'A':pressed[self.A],
			'B':pressed[self.B],
			'X':pressed[self.X],
			'Y':pressed[self.Y],
			'L1':pressed[self.L1],
			'R1':pressed[self.R1],
			'L2':pressed[self.L2],
			'R2':pressed[self.R2],
			'Select':pressed[self.Select],
			'Start':pressed[self.Start],
			'L_R': L_R,
			'U_D': U_D
		}
		return state