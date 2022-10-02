import pygame,random, threading, time
from Token import *

class Board():
	RED = 1
	YELLOW = 2

	MINSCORE = -99999
	MAXSCORE = 99999

	MININFINITY = -100000000
	MAXINFINITY = 100000000

	COLWEIGHT = [3,2,1,0] # au centre 3 points et ensuite ca descend de 1 point par colonne...

	def __init__(self):
		# une version en mémoire du Board qui permet notamment de faire les simulations de jeu par l'I.A.
		self.board = [ [0]*6 for i in range(7)]
		self.minmaxcounter = 0

		# la représentation graphique du Board
		self.background = pygame.image.load("./background/background.png").convert_alpha()
		self.foreground = pygame.image.load("./background/foreground.png").convert_alpha()
		self.image = pygame.Surface([self.background.get_width(),self.background.get_height()], pygame.SRCALPHA, 32)
		self.image = self.image.convert_alpha()
		self.rect = pygame.Rect(0,0,self.image.get_width(),self.image.get_height())

		# on créé un jeton qui permettra d'indiquer au joueur ou il veut jouer
		self.token = Token(Token.RED)
		self.token.setCol(3)
		self.token.setRow(-1)

		# on créé les groupes de token pour l'affichage et les animations
		self.stabletokens = pygame.sprite.Group()
		self.fallingtokens = pygame.sprite.Group()

		# on créé des variables qui vont permettre de récuperer les informations de l'I.A.
		# car le calcul va etre asynchrone (dans un thread séparé)
		self.bestscore = 0
		self.bestposition = -1
		self.thread = None

		return

	def update(self,time):

		self.token.update(time) # on met à jour le token qui represente ou le joueur veut jouer

		self.stabletokens.update(time) # on met a jour tous les tokens qui sont sur le board
		self.fallingtokens.update(time) # on met a jour tous les tokens qui sont en train de tomber

		# on change de groupe les tokens qui sont tombés
		for token in self.fallingtokens:
			if(not token.isDropping()):
				self.stabletokens.add(token)
				self.fallingtokens.remove(token)

		# on créé l'image avec les jetons en train de tomber
		self.image.blit(self.background, self.rect)
		self.fallingtokens.draw(self.image)
		self.image.blit(self.foreground, self.rect)
		# on dessine le token que l'on veut jouer
		self.image.blit(self.token.image, self.token.rect)
		# on dessine par dessus les tokens qui sont sur le board
		self.stabletokens.draw(self.image)

		return

	def getInsertPosition(self, position):
		if(self.board[position][0]!=0):
			return -1
		else:
			index = 0
			for i in range(1,6):
				if(self.board[position][i]!=0):
					return i-1
			return i

	def containsToken(self, position):
		return self.board[position][5] != 0

	def canInsertPosition(self, position):
		pos = self.getInsertPosition(position)
		return pos!=-1

	def tokenIsDropping(self):
		return len(self.fallingtokens)>0

	def drop(self, position=-1):
		'''
		Drop a real token on the board
		It will appear on the screen
		'''
		color = self.token.getColor()
		if(position==-1):
			position = self.token.getCol()
		if(not self.canInsertPosition(position)):
			return -1

		newtoken = Token(self.token.getColor()) # on créé un nouveau token que l'on fait tomber
		newtoken.setCol(position)
		newtoken.setRow(self.getInsertPosition(position))
		newtoken.drop()
		self.fallingtokens.add(newtoken)

		# on fini par inserer le jeton sur le Board en mémoire
		return self.insert(position, color)

	def nextPlayer(self):
		self.token.flip()
		self.token.setCol(3)

	def isHumanPlaying(self):
		return self.token.getColor()==Token.RED

	def isComputerPlaying(self):
		return self.token.getColor()==Token.YELLOW

	def insert(self, position, color):
		'''
		Insert a token on the board memory buffer (can be used for simulation during minmax)
		no changes on the screen
		'''
		pos = self.getInsertPosition(position)
		if(pos==-1):
			return -1
		
		self.board[position][pos] = color
		return position


	def remove(self, position):
		if(not self.containsToken(position)):
			return -1
		pos = self.getInsertPosition(position)+1
		self.board[position][pos] = 0

	def is4Horiz(self, col, row):
		'''
		test vers la droite
		'''
		color = self.board[col][row]
		if(color==0):
			return 0
		elif(	
			self.board[col+1][row]==color and
			self.board[col+2][row]==color and
			self.board[col+3][row]==color
			):
			return color
		else:
			return 0

	def is4Vert(self, col, row):
		'''
		test vers le bas
		'''
		color = self.board[col][row]
		if(color==0):
			return 0
		elif(	
			self.board[col][row+1]==color and
			self.board[col][row+2]==color and
			self.board[col][row+3]==color
			):
			return color
		else:
			return 0

	def is4DownRight(self, col, row):
		'''
		test vers le bas
		'''
		color = self.board[col][row]
		if(color==0):
			return 0
		elif(	
			self.board[col+1][row+1]==color and
			self.board[col+2][row+2]==color and
			self.board[col+3][row+3]==color
			):
			return color
		else:
			return 0

	def is4UpRight(self, col, row):
		'''
		test vers le haut
		'''
		color = self.board[col][row]
		if(color==0):
			return 0
		elif(	
			self.board[col+1][row-1]==color and
			self.board[col+2][row-2]==color and
			self.board[col+3][row-3]==color
			):
			return color
		else:
			return 0

	def is3Horiz(self, col, row):
		'''
		test vers la droite
		col: 0 à 4
		'''

		# on récupère les couleurs des 3 jetons ainsi que les couleurs des jetons avant et apres les 3 jetons
		point2 = self.board[col][row] 
		if(point2==0): # le case que l'on cherche à tester n'a pas de jeton, pas la peine d'aller plus loin...
			return 0
		if(col>0):
			point1 = self.board[col-1][row] # on récupère le jeton avant ssi on est pas sur le bord
		else:
			point1 = -1 
		point3 = self.board[col+1][row] # jeton juste a droite de celui que l'on cherche a tester
		point4 = self.board[col+2][row] # jeton suivant de celui juste a droite que l'on cherche a tester
		if(col<4):
			point5 = self.board[col+3][row]  # on récupère le jeton apres ssi on est pas sur le bord
		else:
			point5 = -1

		candidate = (point2==point3) and (point3==point4)
		if(candidate): # 3 jetons de la meme couleur alignés, c'est bon signe
			if(point1==0 or point5 ==0):
				return point2 # la case avant ou apres ces 3 jetons est vide, il y a donc la possibilité de faire un 4 à la suite!
			else:
				return 0 # les jetons avant et apres sont deja remplis... c'est donc un faux positif
		else:
			return 0

	def is2Horiz(self, col, row):
		'''
		test vers la droite
		col: 0 à 5
		'''

		# on récupère les couleurs des 3 jetons ainsi que les couleurs des jetons avant et apres les 2 jetons
		point2 = self.board[col][row] 
		if(point2==0): # le case que l'on cherche à tester n'a pas de jeton, pas la peine d'aller plus loin...
			return 0
		if(col>0):
			point1 = self.board[col-1][row] # on récupère le jeton avant ssi on est pas sur le bord
		else:
			point1 = -1 
		point3 = self.board[col+1][row] # jeton juste a droite de celui que l'on cherche a tester
		if(col<4):
			point4 = self.board[col+2][row]  # on récupère le jeton apres ssi on est pas sur le bord
		else:
			point4 = -1

		candidate = (point2==point3)
		if(candidate): # 2 jetons de la meme couleur alignés, c'est bon signe
			if(point1==0 or point4 ==0):
				return point2 # la case avant ou apres ces 2 jetons est vide, il y a donc la possibilité de faire un 4 à la suite!
			else:
				return 0 # les jetons avant et apres sont deja remplis... c'est donc un faux positif
		else:
			return 0

	def is3Vert(self, col, row):
		'''
		test vers le bas
		row: 1 à 3
		'''

		# on récupère les couleurs des 3 jetons ainsi que si la case du dessus est vide
		point2 = self.board[col][row] 
		if(point2==0): # le case que l'on cherche à tester n'a pas de jeton pas la peine d'aller plus loin...
			return 0
		point1 = self.board[col][row-1] # on récupère le jeton du dessus
		if(point1!=0): # il y a deja un jeton au dessus, pas la peine d'aller plus loin...
			return 0
		point3 = self.board[col][row+1] # jeton juste en dessus de celui que l'on cherche a tester
		point4 = self.board[col][row+2] # jeton encore en dessous de celui que l'on cherche a tester

		candidate = (point2==point3) and (point3==point4)
		if(candidate): # 3 jetons de la meme couleur alignés, et il n'y a pas de jeton au dessus, good!
			return point2 # il y a donc la possibilité de faire un 4 à la suite!
		else:
			return 0

	def is2Vert(self, col, row):
		'''
		test vers le bas
		row: 1 à 4
		'''

		# on récupère les couleurs des 2 jetons ainsi que si la case du dessus est vide
		point2 = self.board[col][row] 
		if(point2==0): # le case que l'on cherche à tester n'a pas de jeton pas la peine d'aller plus loin...
			return 0
		point1 = self.board[col][row-1] # on récupère le jeton du dessus
		if(point1!=0): # il y a deja un jeton au dessus, pas la peine d'aller plus loin...
			return 0
		point3 = self.board[col][row+1] # jeton juste en dessous de celui que l'on cherche a tester

		candidate = (point2==point3)
		if(candidate): # 2 jetons de la meme couleur alignés, et il n'y a pas de jeton au dessus, good!
			return point2 # il y a donc la possibilité de faire un 4 à la suite!
		else:
			return 0

	def is3UpRight(self,col,row):
		'''
		3 aligned
		col 0-4
		row 3-5
		'''
		# on récupère les couleurs des 3 jetons ainsi que si la case du dessus est vide
		point2 = self.board[col+2][row-2] 
		if(point2==0): # le case que l'on cherche à tester n'a pas de jeton pas la peine d'aller plus loin...
			return 0
		if(col+3>6 or row-3<0):
			point1 = -1
		else:
			point1 = self.board[col+3][row-3] # on récupère le jeton du dessus

		point3 = self.board[col+1][row-1] # jeton juste en dessus de celui que l'on cherche a tester
		point4 = self.board[col][row] # jeton encore en dessous de celui que l'on cherche a tester
		if(col-1<0 or row+1>5):
			point5 = -1
		else:
			point5 = self.board[col-1][row-1] # on récupère le jeton du dessus

		candidate = (point2==point3) and (point3==point4)
		if(candidate): # 3 jetons de la meme couleur alignés
			if(point1==0 or point5==0): # et il y a un emplacement libre sur une extrémité de la diagonale
				return point2
			else:
				return 0
		else:
			return 0

	def is3DownRight(self,col,row):
		'''
		3 aligned
		col 0-4
		row 0-3
		'''
		# on récupère les couleurs des 3 jetons ainsi que si la case du dessus est vide
		point2 = self.board[col][row] 
		if(point2==0): # le case que l'on cherche à tester n'a pas de jeton pas la peine d'aller plus loin...
			return 0
		if(col<0 or row<0):
			point1 = -1
		else:
			point1 = self.board[col-1][row-1] # on récupère le jeton du dessus

		point3 = self.board[col+1][row+1] # jeton juste en dessous de celui que l'on cherche a tester
		point4 = self.board[col+2][row+2] # jeton encore en dessous de celui que l'on cherche a tester
		if(col+3>6 or row+3>5):
			point5 = -1
		else:
			point5 = self.board[col+3][row+3] # on récupère le jeton en dessous

		candidate = (point2==point3) and (point3==point4)
		if(candidate): # 3 jetons de la meme couleur alignés
			if(point1==0 or point5==0): # et il y a un emplacement libre sur une extrémité de la diagonale
				return point2
			else:
				return 0
		else:
			return 0

	def evalPosition(self,col,row,color):
		'''
		evaluate the "weight" of a position
		'''
		token = self.board[col][row]
		if(token==0):
			return 0

		index = abs(col-3)
		val = Board.COLWEIGHT[index]
		if(token==color):
			return val
		else:
			return -val

	def is4inarow(self):
		# lignes horizontales
		for col in range(4):
			for row in range(6):
				res = self.is4Horiz(col, row)
				if(res!=0):
					return res

		# lignes verticales
		for col in range(7):
			for row in range(3):
				res = self.is4Vert(col, row)
				if(res!=0):
					return res

		# diagonales vers le bas
		for col in range(4):
			for row in range(3):
				res = self.is4DownRight(col, row)
				if(res!=0):
					return res

		# diagonales vers le haut
		for col in range(4):
			for row in range(5,2,-1):
				res = self.is4UpRight(col, row)
				if(res!=0):
					return res

		return 0

	def evalBoard(self, color):
		'''
		Eval board
		'''
		score = 0

		# test de 3 pions alignés verticalement
		for col in range(7):
			for row in range(1,4):
				res = self.is3Vert(col, row)
				if(res!=0):
					if(res==color):
						score += 100
					else:
						score -= 100
					
		# test de 3 pions alignés horizontalement
		for col in range(5):
			for row in range(6):
				res = self.is3Horiz(col, row)
				if(res!=0):
					if(res==color):
						score += 100
					else:
						score -= 100
		
		# test de 3 pions alignés en diagonale vers le haut
		for col in range(5):
			for row in range(3,6):
				res = self.is3UpRight(col, row)
				if(res!=0):
					if(res==color):
						score += 100
					else:
						score -= 100

		# test de 3 pions alignés en diagonale vers le bas
		for col in range(5):
			for row in range(4):
				res = self.is3DownRight(col, row)
				if(res!=0):
					if(res==color):
						score += 100
					else:
						score -= 100


		# test de 2 pions alignés verticalement
		for col in range(7):
			for row in range(1,5):
				res = self.is2Vert(col, row)
				if(res!=0):
					if(res==color):
						score += 10
					else:
						score -= 10

		# test de 2 pions alignés horizontalement
		for col in range(6):
			for row in range(6):
				res = self.is2Horiz(col, row)
				if(res!=0):
					if(res==color):
						score += 10
					else:
						score -= 10

		# on fini par évaluer le score global des positions des pions sachant que les pions au milieu offrent plus de possibilité
		for col in range(7):
			for row in range(6):
				res = self.evalPosition(col,row, color)
				score += res

		return score

	def printBoard(self):
		for j in range(6):
			ln = ''
			for i in range(7):
				if(self.board[i][j]==0):
					ln+=' '
				elif(self.board[i][j]==Board.RED):
					ln+='X'
				elif(self.board[i][j]==Board.YELLOW):
					ln+='O'
			print(ln)
		print('-------')

	def getBestScore(self):
		return self.bestscore

	def getBestPosition(self):
		return self.bestposition

	def getComputeElapsedTime(self):
		if(self.isComputing()):
			return -1
		else:
			return self.elapsedtime

	def getComputeDepth(self):
		depth = 0
		fillfactor = self.getFillFactor()
		if(fillfactor<0.25):
			depth=5
		elif(fillfactor<0.5):
			depth=6
		else:
			depth=8
		return depth

	def getNbMinMaxIteration(self):
		return self.minmaxcounter

	def isComputing(self):
		if(self.thread==None):
			return False
		elif(self.thread.is_alive()):
			return True
		else:
			self.thread = None
			self.enddtime = time.time()
			self.elapsedtime = self.enddtime-self.starttime
			return False

	def waitComputing(self):
		if(self.thread!=None and self.thread.is_alive()):
			self.thread.join()
			self.thread = None
			self.enddtime = time.time()
			self.elapsedtime = self.enddtime-self.starttime

	def compute(self, color):
		'''
		Lance le calcul par l'I.A. pour trouver la meilleure position
		Attention: Ce calcul est asynchrone, il faut donc ensuite utiliser isComputing, waitComputing, getBestScore, getBestPosition, getNbMinMaxIteration, getComputeElapsedTime
		'''
		self.starttime = time.time()
		self.minmaxcounter = 0
		depth = self.getComputeDepth()

		if(self.thread==None or not self.thread.is_alive()):
			self.thread = threading.Thread(target=self.threadcompute, args=(depth, color, True))
			self.thread.start()

	def threadcompute(self, depth, color, ismax):
		(self.bestscore,self.bestposition) = self.minmax(depth, color, ismax)

	def minmax(self, depth, color, ismax):
		self.minmaxcounter += 1

		# on regarde si on est pas en étape terminale (4 pions alignés)
		is4 = self.is4inarow()
		if(is4==color):
			return (Board.MAXSCORE+depth,-1) # la couleur sélectionnée a gagnée
		elif(is4!=0):
			return (Board.MINSCORE-depth,-1) # l'autre couleur a gagnée

		if(depth==0 or self.getFillFactor()==1): # on est tout en bas ou le board est plein, on évalue la situation
			return (self.evalBoard(color),-1)


		othercolor = Board.RED if color == Board.YELLOW else Board.YELLOW
		depth -= 1 # on décrémente la profondeur
		if(ismax==True):
			ret = Board.MININFINITY
		else:
			ret = Board.MAXINFINITY
		bestposition = -1
		for col in range(7):
			if(self.canInsertPosition(col)):
				self.insert(col, color if ismax else othercolor) # on ajoute une piece sur le board pour la tester
				(val,tmp) = self.minmax(depth, color, not ismax) # on appelle récursivement la fonction en changeant de joueur
				self.remove(col) # puis on l'enleve aussitot

				if(ismax==True): # on maximise
					if(val>=Board.MAXSCORE): # on est tombé sur une partie gagnante, on s'arrete la
						return(val, col)
					elif(val>ret):
						ret = val # on garde le score courant car c'est le meilleur...
						bestposition = col
					elif(val==ret and random.randint(0,1)==0):
						ret = val # on garde le score courant car il est à égalité avec le meilleur score (pour donner un coté aléatoire au jeu)
						bestposition = col

				else:  # on minimise
					if(val<=Board.MINSCORE): # on est tombé sur une partie gagnante, on s'arrete la
						return(val, col)
					elif(val<ret):
						ret = val # on garde le score courant car c'est le meilleur...
						bestposition = col
					elif(val==ret and random.randint(0,1)==0):
						ret = val # on garde le score courant car il est à égalité avec le meilleur score (pour donner un coté aléatoire au jeu)
						bestposition = col

		return (ret, bestposition)

	def getTokenColorString(self, color):
		if(color==Board.RED):
			return "RED"
		elif(color==Board.YELLOW):
			return "YELLOW"
		else:
			return None

	def moveNextFreePositionLeft(self):
		col = self.token.getCol() # on récupère la position courante du jeton
		newcol = self.getNextFreePositionLeft(col) # on regarde si il y a une position à gauche
		if(newcol!=-1): # si c'est le cas on déplace le jeton
			self.token.setCol(newcol)

	def getNextFreePositionLeft(self, col):
		if(col==0): # on est deja tout a gauche...
			return -1
		for i in range(col-1, -1, -1):
			if(self.canInsertPosition(i)):
				return i
		return -1 # plus de place

	def moveNextFreePositionRight(self):
		col = self.token.getCol() # on récupère la position courante du jeton
		newcol = self.getNextFreePositionRight(col) # on regarde si il y a une position à droite
		if(newcol!=-1): # si c'est le cas on déplace le jeton
			self.token.setCol(newcol)

	def getNextFreePositionRight(self, col):
		if(col==6): # on est deja tout a droite...
			return -1
		for i in range(col+1, 7):
			if(self.canInsertPosition(i)):
				return i
		return -1 # plus de place

	def getFillFactor(self):
		notnull = 0
		for col in range(7):
			for row in range(6):
				if(self.board[col][row]!=0):
					notnull += 1
		
		return notnull/(6*7)