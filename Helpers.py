import pygame, random, sys, glob, pickle, string

def init():
	pygame.init()
	pygame.font.init()
	pygame.mixer.init()
	pygame.display.set_mode()
	pygame.mouse.set_visible(True)
	pygame.display.set_caption("Multiplayer Arena Test")
	
def br(lines=1):
	for i in range(0,lines):
		print ""

#takes only one channel as argument
def volumeChange(channel,change):
	currentVol = channel.get_volume()
	currentVol += change
	if currentVol > 1.0:
		currentVol = 1.0
	elif currentVol < 0.0:
		currentVol = 0.0
	channel.set_volume(currentVol)
	
#takes a list of channels as argument
def volumeChangeAll(channels,change):
	for channel in channels:
		currentVol = channel.get_volume()
		currentVol += change
		if currentVol > 1.0:
			currentVol = 1.0
		elif currentVol < 0.0:
			currentVol = 0.0
		channel.set_volume(currentVol)

def saveLevel(currentmap, mapname):
	map = open(string.replace("maps/"+mapname+".map","\r",""),'w') #write only means we can create new files
	pickle.dump(currentmap, map)#(object to save, file to save to)
	map.close()
	print "Map saved as:",mapname+".map"
	br()

def loadLevel(mapname):
	try: 
		file = open(mapname,'r')
	except:
		print "No such map: "+mapname
		return
	unpickledmap = pickle.load(file)#load(filename) recreates pickled object
	file.close()
	print "Level '%s"%mapname+"' loaded successfully!"
	br()
	return unpickledmap
	
def chooseLevel():
	options = glob.glob("maps/*.map")#Uses wildcard to make list of all files
	print "Your level options are:"
	for choice in enumerate(options):
		print str(choice[0]+1)+")", choice[1]
	br()
	try:
		choice = input("Which level do you want? ")
	except (NameError,TypeError,SyntaxError):
		print "Invalid choice."
		return chooseLevel()
	return loadLevel(options[choice-1])
	br()
	
def sprite_sheet(size,file,offsetX=0,offsetY=0,pos=(0,0)):

	#Initial Values
	len_sprt_x,len_sprt_y = size #sprite size
	sprt_rect_x,sprt_rect_y = pos #where to find sprite on sheet
	
	sheet = pygame.image.load(file).convert_alpha() #Load the sheet
	sheet_rect = sheet.get_rect()
	sprites = []
	print sheet_rect.height, sheet_rect.width
	for i in range(0,sheet_rect.height-len_sprt_y,size[1]):#rows
		print "row"
		for j in range(0,sheet_rect.width-len_sprt_x,size[0]):#columns
			print "column"
			#For the first sprite, ignore the offsetX and offsetY
			sheet.set_clip(pygame.Rect(sprt_rect_x, sprt_rect_y, len_sprt_x, len_sprt_y))
			#Grab the sprite you want
			sprite = sheet.subsurface(sheet.get_clip()) #grab the sprite you want
			sprites.append(sprite)
			sprt_rect_x += len_sprt_x+offsetX
			
		sprt_rect_y += len_sprt_y+offsetY
		sprt_rect_x = 0
	print sprites
	return sprites
