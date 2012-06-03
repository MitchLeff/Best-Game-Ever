import pygame, random, sys, glob, pickle

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
	
def saveLevel(currentmap, mapname):
	map = open("maps/"+mapname+".map",'w') #write only means we can create new files
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