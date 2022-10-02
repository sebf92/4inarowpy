# #####################################################################################
#
# Un exemple de jeu de plateau en python ou l'on joue contre "l'ordinateur"
# PUISSANCE 4
# 
# #####################################################################################

# Ne pas oublier d'installer les librairies manquantes:
# pip install pygame

import sys,time,pygame

from tkhelpers import *
from Board import Board

if __name__ != '__main__': 
	exit() # on sort si on a pas executé ce script car c'est certainement une erreur, il ne DOIT PAS etre importé dans un autre script

# Paramètres principaux du jeu
WIDTH = 630
HEIGHT = 630
FPS = 60 
FULLSCREEN = False
TITLE = "Py-ssance 4"
DEBUG = True

# On initialise les variables du jeu
pygame.init()
pygame.mixer.init()
playfield = pygame.Rect(0,0,800, 600)

if(FULLSCREEN):
	screen = pygame.display.set_mode((WIDTH,HEIGHT), pygame.FULLSCREEN | pygame.DOUBLEBUF, vsync=1)
else:
	screen = pygame.display.set_mode((WIDTH,HEIGHT))

pygame.display.set_caption(TITLE)


# on cache le curseur de la souris
if(FULLSCREEN):
	pygame.mouse.set_visible(False)


# ##################################################
# ##################################################
# Ecran accueil
# ##################################################
# ##################################################
loop = True
splashscreen = pygame.image.load("./background/splashscreen.png").convert_alpha()
screen.fill((255,255,255))
xoffset = (screen.get_width()-splashscreen.get_width())/2
yoffset = (screen.get_height()-splashscreen.get_height())/2
screen.blit(splashscreen, pygame.Rect(xoffset,yoffset,splashscreen.get_width(), splashscreen.get_height()))

while loop:
	# on gère les evenements clavier
	###################
	for event in pygame.event.get():
		if event.type == pygame.QUIT: 
			pygame.quit()
			sys.exit(0)
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE or event.key == pygame.K_DOWN:
				loop = False
			if event.key == pygame.K_ESCAPE:
				pygame.quit()
				sys.exit(0)

	# on met à jour l'affichage ecran
	pygame.display.update()


# ##################################################
# ##################################################
# Jeu
# ##################################################
# ##################################################
screen.fill((28,98,204))
while True:
	#pygame.mixer.music.load('./soundtracks/original/01_-_Arkanoid_-_ARC_-_Start_Demo.ogg')
	#pygame.mixer.music.play()

	# on créé un plateau de jeu, qui contient toute la logique du jeu
	# y compris l'intelligence de l'ordinateur
	board = Board()

	clock = pygame.time.Clock()
	next = False
	winnercolor = 0
	computeinprogress= False
	while not next or board.tokenIsDropping():
		# on limite l'affichage à FPS images par secondes
		elapsedtime = clock.tick(FPS)	
		
		# Si c'est aux jaunes de jouer, on demande à l'ordinateur
		# on utilise un algorithme appelé "minmax"
		# (on fait au moins une itération de boucle pour ne pas avoir un écran noir si les jaunes commencent car le calcul de l'ordinateur peut etre long...)
		if(board.isComputerPlaying() and not board.tokenIsDropping()):

			# on lance le calcul de facon un peu complexe car il peut etre long:
			# il va etre lancé de maniere asynchrone dans un "thread" dédié

			if(not computeinprogress):
				# on lance l'IA
				board.compute(Board.YELLOW)
				computeinprogress = True
			else:
				# un calcul est en cours...
				if(not board.isComputing()):
					# le calcul est terminé, on récupère les informations
					computeinprogress= False
					etime = board.getComputeElapsedTime()
					bestscore = board.getBestScore()
					bestposition = board.getBestPosition()
					depth = board.getComputeDepth()
					minmaxcounter = board.getNbMinMaxIteration()

					# on insère le pion à la position retenue par l'ordinateur
					board.drop(bestposition)
					board.nextPlayer()
					winnercolor = board.is4inarow()

					if(winnercolor!=0): # on a trouvé un 4 à la suite, on sort
						next = True

					if(DEBUG):
						board.printBoard()
						print("Best score (",bestscore,") best position (",bestposition,") for Yellow in (",etime,") seconds with (",depth,") depth and (",minmaxcounter,") iterations")


		# on gère les evenements clavier
		###################
		for event in pygame.event.get():
			if event.type == pygame.QUIT: 
				pygame.quit()
				sys.exit(0)
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					sys.exit(0)
				if(board.isHumanPlaying() and not board.tokenIsDropping()):
					# on gère les touches seulement si c'est à l'humain de jouer
					if event.key == pygame.K_LEFT:
						# on deplace le jeton a gauche
						board.moveNextFreePositionLeft()
					if event.key == pygame.K_RIGHT:
						# on deplace le jeton a droite
						board.moveNextFreePositionRight()
					if event.key == pygame.K_SPACE or event.key == pygame.K_DOWN:
						# on fait tomber la piece
						if(board.drop()!=-1):
							board.nextPlayer()
							winnercolor = board.is4inarow()

							if(DEBUG):
								board.printBoard()
								print("Note X: ", board.evalBoard(Board.RED))

							if(winnercolor!=0):
								next = True
					if event.key == pygame.K_h:
						# si on appuie sur H on demande à l'ordinateur de jouer à notre place
						board.compute(Board.RED) # on lance le calcul
						board.waitComputing() # on attend qu'il se termine
						bestscore = board.getBestScore() # on récupère les résultats
						bestposition = board.getBestPosition()

						# on insère le pion à la position retenue par l'ordinateur
						board.drop(bestposition)
						board.nextPlayer()
						winnercolor = board.is4inarow()

						if(winnercolor!=0):
							next = True



		board.update(time)

		xoffset = (screen.get_width()-board.rect.w)/2
		yoffset = (screen.get_height()-board.rect.h)/2
		screen.blit(board.image, pygame.Rect(xoffset, yoffset, board.rect.w, board.rect.h))

		# on met à jour l'affichage ecran
		pygame.display.update()

		if(board.getFillFactor()==1):
			next= True # le board est plein, on sort

	if(winnercolor==0):
		tk_message("Draw\t\t\t\t\t\t")
	else:
		tk_message(board.getTokenColorString(winnercolor)+" wins!"+"\t\t\t\t\t\t")
