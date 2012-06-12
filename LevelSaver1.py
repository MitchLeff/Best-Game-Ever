#!/usr/bin/python
#
#Level Saver/Loader by Peter Kennedy
#
#License - All rights reserved, copyright Mitch Leff and Peter Kennedy
#
#Version = '1.0'

import pygame,pickle, glob, string
from pygame.locals import *
from glob import glob#allows wildcard calls to filenames

def br(lines=1):
	for i in range(0,lines):
		print ""
	
def saveLevel(currentmap, mapname):
	map = open(string.replace("maps/"+mapname+".map","\r",""),'w') #write only means we can create new files
	try: 
		pickle.dump(currentmap, map)#(object to save, file to save to)
	except:
		return saveLevel(currentmap, raw_input("Invalid map name. New name: "))
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
	options = glob("maps/*.map")#Uses wildcard to make list of all files
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

def main():
	saveLevel(raw_input("What to save? "), raw_input("What name to save as? "))
	print chooseLevel()
	
main()
	
	
