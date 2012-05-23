#CONSTANTS
FPS = 60
GRAVITY = .8
MIN_SPAWN = 22
MAX_SPAWN = 26
MIN_SPEED = 2
MAX_SPEED = 3
DEATH_TIMER = 40
FLOATING_TEXT_LIFESPAN = 70
MAX_SPEED_X = 7
MAX_SPEED_Y = 15

#IMPORTS
import pygame, random
from pygame.locals import *

clock = pygame.time.Clock()
pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.display.set_mode()
pygame.mouse.set_visible(False)
pygame.display.set_caption("Bullet Buster")


#LOAD SOUNDS
sfx = pygame.mixer.Channel(0)
announcer = pygame.mixer.Channel(1)

die_sound = pygame.mixer.Sound("sounds/die.wav")
jump_sound = pygame.mixer.Sound("sounds/jump.wav")
stomp_sound = pygame.mixer.Sound("sounds/stomp.wav")

combo0 = pygame.mixer.Sound("sounds/killingspree.wav")
combo1 = pygame.mixer.Sound("sounds/rampage.wav")
combo2 = pygame.mixer.Sound("sounds/unstoppable.wav")
combo3 = pygame.mixer.Sound("sounds/godlike.wav")
combo4 = pygame.mixer.Sound("sounds/holyshit.wav")

#LOAD IMAGES
background_image = pygame.image.load("images/coach.png").convert_alpha()

mario_still = (pygame.image.load("images/mario_still.png").convert_alpha())
mario_jump = (pygame.image.load("images/mario_jump.png").convert_alpha())
mario_walk1 = (pygame.image.load("images/mario_walk1.png").convert_alpha())
mario_walk2 = (pygame.image.load("images/mario_walk2.png").convert_alpha())
mario_walk3 = (pygame.image.load("images/mario_walk3.png").convert_alpha())
MARIO_SPRITE_OPTIONS = [mario_still, mario_jump, mario_walk1, mario_walk2, mario_walk3, mario_walk2]

bill_image = pygame.image.load("images/bill.png").convert_alpha()
bigBill_image = pygame.transform.scale2x(bill_image)
megaBill_image = pygame.transform.scale2x(bigBill_image)

width  = max(300,background_image.get_width())
height = max(200,background_image.get_height())
size   = [width, height]
screen = pygame.display.set_mode(size)
background = pygame.Surface(screen.get_size())

class bill(pygame.sprite.Sprite):
	def __init__(self, *groups):
		directions = [-1, 1]
		pygame.sprite.Sprite.__init__(self)

		size = random.random()

		if size < .025:
			self.image = megaBill_image
		elif size < .1:
			self.image = bigBill_image
		else:
			self.image = bill_image
		self.rect = self.image.get_rect()

		self.direction = random.choice(directions)
		self.y_dir = 0
		self.y_vel = 0

		hh = random.random()

		if hh < .30:
			h = random.randint((height-1*height/6), (height))
		elif hh < .55:
			h = random.randint((height-2*height/6), (height-1*height/6))
		elif hh < .75:
			h = random.randint((height-3*height/6), (height-2*height/6))
		elif hh <= .90:
			h = random.randint((height-4*height/6), (height-3*height/6))
		else:
			h = random.randint((height-5*height/6), (height-4*height/6))

		if h + self.rect.height > height:
			h = height - self.rect.height

		if self.direction == 1:
			self.rect.midright = [0, h]
		elif self.direction == -1:
			self.rect.midleft = [width, h]
			self.image = pygame.transform.flip(self.image, True, False)
		self.speed = random.randint(MIN_SPEED,MAX_SPEED)

		for g in groups:
			g.add(self)

		self.mode = "fire"

	def update(self):
		if self.mode == 'fire':
			self.rect.right += self.speed*self.direction
		elif self.mode == 'die':
			self.y_vel += GRAVITY
			self.rect.top += self.y_vel
		if self.rect.right < -10 or self.rect.left > width+10 or self.rect.top > height + 10:
			self.kill()

class mario(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)

		self.sprite_options = MARIO_SPRITE_OPTIONS
		self.image = self.sprite_options[0]
		self.rect = self.image.get_rect()
		self.rect.midbottom = [width/2, height]

		self.max_speed_x = MAX_SPEED_X
		self.max_speed_y = MAX_SPEED_Y

		self.accell = 1.0

		self.natural_accell = self.accell/2

		self.xdirection = 1
		self.ydirection = 0

		self.x_vel = 0
		self.y_vel = 0
		self.x_accell = 0
		self.y_accell = GRAVITY

		self.moving_sprites = self.sprite_options[2:]

		self.step = 0
		self.image_tempo = 6.0
		self.jump_frames = 0
		self.jumped = True

		self.combo = 0

	def update(self):
		global UP, DOWN, RIGHT, LEFT, height, width

		#Determine x direction and acceleration
		if LEFT and RIGHT:
			pass
		elif LEFT:
			self.xdirection = -1
			self.x_accell = -1*self.accell
		elif RIGHT:
			self.xdirection = 1
			self.x_accell = self.accell
		else:
			self.x_accell = 0


		if UP and self.jump_frames <= 10 and not self.jumped:
			if self.jump_frames == 0 and self.combo == 0:
				sfx.play(jump_sound)
			self.y_vel = -10
			self.jump_frames += 1

		if not UP:
			self.jumped = True

		#Update velocity
		self.x_vel += self.x_accell
		self.y_vel += self.y_accell

		#Check for deceleration
		if self.x_accell == 0:

			if self.x_vel <= self.natural_accell and self.x_vel >= -1*self.natural_accell:
				self.x_vel = 0
			elif self.x_vel < 0:
				self.x_vel += self.natural_accell
			elif self.x_vel > 0:
				self.x_vel -= self.natural_accell

		#Check Max Speed
		if self.x_vel >= self.max_speed_x:
			self.x_vel = self.max_speed_x
		elif self.x_vel <= -1*self.max_speed_x:
			self.x_vel = -1*self.max_speed_x
		if self.y_vel >= self.max_speed_y:
			self.y_vel = self.max_speed_y
		elif self.y_vel <= -1*self.max_speed_y:
			self.y_vel = -1*self.max_speed_y

		#Update position
		self.rect.top += self.y_vel
		self.rect.left += self.x_vel

		#Bounds Check
		if self.rect.bottom >= height:
			self.rect.bottom = height
			self.jump_frames = 0
			self.jumped = False
			self.combo = 0
		if self.rect.left < 0:
			self.rect.left = 0
			self.x_vel = 0
			self.x_accell = 0
		elif self.rect.right >= width:
			self.rect.right = width
			self.x_vel = 0
			self.x_accell = 0

		#Set Image
		if self.jump_frames != 0: #Jump image if jumped
			self.image = self.sprite_options[1]
			self.step = 0
		elif self.x_vel == 0:
			self.image = self.sprite_options[0]
			self.step = 0
		else:
			self.image = self.moving_sprites[int(self.step) % len(self.moving_sprites)]
			self.step += 1.0/self.image_tempo
		#Check to flip for going left
		if self.xdirection == -1:
			self.image = pygame.transform.flip(self.image, True, False)

pointFont = pygame.font.SysFont('ocraextended',24)
class point(pygame.sprite.Sprite):
	def __init__(self, n, pos):
		pygame.sprite.Sprite.__init__(self)
		self.life = FLOATING_TEXT_LIFESPAN
		self.pos = pos
		self.n = n
		self.text = pointFont.render("+%s" % self.n, True, (0,255,0))

	def update(self):
		self.life -= 1
		if self.life <= 0:
			self.kill()

points = pygame.sprite.Group()
marios = pygame.sprite.Group(mario())
bills = pygame.sprite.Group()

highscore = 0
score = 0
running = True
cycles = 0
next_spawn = random.randint(MIN_SPAWN, MAX_SPAWN)
death_timer = 0

scoreFont = pygame.font.SysFont('ocraextended', 26)
scoreText = scoreFont.render("Score: %s" % score, True, (0,0,255))
highscoreText = scoreFont.render("High Score: %s" % highscore, True, (0,0,255))

#START MUSICS
pygame.mixer.music.load("sounds/Five Armies.mp3")
pygame.mixer.music.play(-1)

while running:
	clock.tick(FPS)
	pressed = pygame.key.get_pressed()

	UP = pressed[273]
	DOWN = pressed[274]
	RIGHT = pressed[275]
	LEFT = pressed[276]

	event = pygame.event.poll()
	if event.type == KEYDOWN:
		pressed = pygame.key.get_pressed()
		if event.key == K_ESCAPE:
			running = False


	marios.update()
	bills.update()
	points.update()

	if next_spawn == 0:
		new_bill = bill(bills)
		next_spawn = random.randint(MIN_SPAWN, MAX_SPAWN)

	screen.blit(background_image, (0,0))

	for b in bills.sprites():
		screen.blit(b.image, b.rect)
		for m in marios.sprites():
			if pygame.sprite.collide_mask(b, m) and b.mode == 'fire':
				if m.rect.bottom < b.rect.centery + m.y_vel + 1:
					sfx.play(stomp_sound)
					b.mode = 'die'
					b.y_vel = -8
					b.image = pygame.transform.flip(b.image,False, True)
					m.jump_frames = 1
					m.jumped = False
					m.combo += 1
					score += m.combo
					if score > highscore:
						highscore = score
						highscoreText = scoreFont.render("High Score: %s" % highscore, True, (0,0,255))
					m.y_vel = -6
					m.rect.top += m.y_vel
					points.add(point(m.combo, b.rect.center))
					if m.combo == 3:
						announcer.play(combo0)
					elif m.combo == 6:
						announcer.play(combo1)
					elif m.combo == 9:
						announcer.play(combo2)
					elif m.combo == 12:
						announcer.play(combo3)
					elif m.combo >= 15:
						announcer.play(combo4)
				else:
					m.kill()
					sfx.play(die_sound)
					death_timer = DEATH_TIMER
				scoreText = scoreFont.render("Score: %s" % score, True, (0,0,255))

	for m in marios.sprites():
		screen.blit(m.image, m.rect)

	for p in points.sprites():
		screen.blit(p.text, p.pos)

	screen.blit(scoreText, (0,0))
	screen.blit(highscoreText, (width/2 - highscoreText.get_width()/2, 0))
	pygame.display.update()

	cycles += 1
	next_spawn -= 1
	if death_timer > 0:
		death_timer -= 1
		if death_timer <= 0:
			marios.add(mario())
			for b in bills.sprites():
				b.kill()
			score = 0
			scoreText = scoreFont.render("Score: %s" % score, True, (0,0,255))

