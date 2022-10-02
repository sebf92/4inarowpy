import pygame

class Token(pygame.sprite.Sprite):
	RED = 1
	YELLOW = 2
	tokens = None

	def __init__(self, color):
		pygame.sprite.Sprite.__init__(self)

		if(Token.tokens == None):
			redToken = pygame.image.load("./sprites/rtoken.png").convert_alpha()
			yellowToken = pygame.image.load("./sprites/ytoken.png").convert_alpha()
			Token.tokens = list()
			Token.tokens.append(redToken)
			Token.tokens.append(yellowToken)

		self.color = color
		self.col = 0
		self.row = 0

		self.velocity = 0
		self.acceleration = 1

		self.falling = False

		self.image = Token.tokens[0]
		self.rect = pygame.Rect(0,0,self.image.get_width(),self.image.get_height())


	def update(self,time):
		self.image = Token.tokens[self.color-1]
		if(self.falling):
			targety = 99+self.row*90
			self.rect.x = 9+self.col*90
			self.velocity += self.acceleration
			self.rect = self.rect.move(0,self.velocity)
			if(self.rect.y>targety):
				self.rect.y = targety
				self.falling = False
		else:
			self.rect = pygame.Rect(9+self.col*90,99+self.row*90,self.image.get_width(),self.image.get_height())

	def setCol(self, col):
		col=max(min(col,6),0)
		self.col = col

	def setRow(self, row):
		row=max(min(row,5),-1)
		self.row = row

	def setColor(self, color):
		color = max(min(color,1),0)
		self.color = color

	def getCol(self):
		return self.col

	def getRow(self):
		return self.row

	def getColor(self):
		return self.color

	def drop(self):
		self.velocity = 0
		self.falling = True
		self.rect.y = 9
		return

	def isDropping(self):
		return self.falling

	def flip(self):
		if(self.color == Token.RED):
			self.color = Token.YELLOW
		else:
			self.color = Token.RED
