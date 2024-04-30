from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *
import gametext
import time

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Room1():

	numPics = 6
	orders = ['356']
	answerNum = 0
	answer = ''
	ansLen = 3
	gameFinished = False

	def mensa(self, game, l2):
		game.r1Running = True
		game.mouseLetGo = True
		game.speedStop = True
		gametext.Text.hideText(game.game_text, game)
		game.setBarVisibility(False)
		game.scaleFactorMensa = 2
		game.cm = CardMaker('card')
		game.mensaImg = game.aspect2d.attachNewNode(game.cm.generate())
		game.mensaImg.setScale((16/9)*game.scaleFactorMensa, 1, game.scaleFactorMensa)

		game.tex = game.loader.loadTexture('assets/img/l2/mensa/bkg.png')
		game.mensaImg.setTexture(game.tex)
		game.mensaImg.setColorScale(1, 1, 1, 0)
		game.mensaImg.setTransparency(True)

		game.mensaButtons = []

		i = 1
		n = 0.2
		while (i <= self.numPics):
			if (i >= 4):
				n = -0.5
				hi = i - 3
			else:
				hi = i
			image = DirectButton(command=self.checkAnswer, extraArgs=[self, game, i, l2], frameTexture=game.loader.loadTexture('assets/img/l2/mensa/' + str(i) + '.png'), pos=((hi*0.7)-1.4, 0, n), scale=(0.33), relief='flat', pressEffect=0, frameSize=(-1, 1, -1, 1))
			image.setTransparency(True)
			image.setColorScale(1, 1, 1, 0)
			game.mensaButtons.append(image)
			i += 1


		# these are the centers of the image
		game.mensa_x = (-16/9/2)*game.scaleFactorMensa
		game.mensa_y = -0.5*game.scaleFactorMensa

		game.mensaImg.setPos(game.mensa_x, 0, game.mensa_y)
		game.mensaImg.setTransparency(TransparencyAttrib.MAlpha)

		self.mensaItems = [game.mensaImg, *game.mensaButtons]

		animItem = []
		for node in self.mensaItems:
			animItem.append(LerpColorScaleInterval(node, 1.5, (1, 1, 1, 1), (1, 1, 1, 0)))
		anim = Parallel(*animItem, name="anim")
		anim.start()

	def checkAnswer(self, game, i, l2):
		self.answerNum += 1
		self.answer += str(i)
		print(self.answer)
		if (self.answerNum >= self.ansLen):
			for ans in self.orders:
				if (self.answer == ans):
					print("yay")
					dismiss = game.loader.loadSfx("assets/sound/dismiss.mp3")
					dismiss.setVolume(game.volume)
					dismiss.play()
					game.itemsCollected.append(game.itemsRequired[0])
					correct = game.loader.loadSfx("assets/sound/correct.mp3")
					correct.setVolume(game.volume)
					correct.play()
					self.answerNum = 0
					self.answer = ''
					self.gameFinished = True
					game.r1Done = True
					l2.addItem(l2, game, 'EYEBALLS')
					self.cleanUpGame(self, game)
					return
			
			for node in game.mensaButtons:
				pos = node.getPos()
				left = (node.getPos()[0]-0.15, node.getPos()[1], node.getPos()[2])
				right = (node.getPos()[0]+0.15, node.getPos()[1], node.getPos()[2])
				shake1 = node.posInterval(0.1, left, pos, blendType='easeIn')
				shake2 = node.posInterval(0.1, right, left, blendType='easeIn')
				shake3 = node.posInterval(0.1, left, right, blendType='easeIn')
				shake4 = node.posInterval(0.05, pos, right, blendType='easeIn')
				shake = Sequence(shake1, shake2, shake3, shake2, shake4)
				shake.start()
			self.answerNum = 0
			self.answer = ''
			print("naur")
			wrong = game.loader.loadSfx("assets/sound/wrong.mp3")
			wrong.setVolume(game.volume)
			wrong.play()
			game.mistakes += 1
			print(game.mistakes)
			self.cleanUpGame(self, game)
			return
		pickup = game.loader.loadSfx('assets/sound/pickup.wav')
		pickup.setLoop(False)
		pickup.setVolume(game.volume)
		pickup.play()
			
	def cleanUpGame(self, game):
		game.game_text.itcText.setTextColor(1, 1, 1, 1)
		self.popout = LerpFunc(self.fadeOut,
            extraArgs=[self, game],
            fromData=1,
            toData=0,
            duration=0.25,
			blendType='easeOut',
            name="fadeo")
		self.popout.start()
		game.r1Running = False
		game.mouseLetGo = False
		game.speedStop = False
		gametext.Text.showText(game.game_text, game)
		game.setBarVisibility(True)

	#def clearAnagrams(self, game):
	#	dismiss = game.loader.loadSfx("assets/sound/dismiss.mp3")
	#	dismiss.setVolume(game.volume)
	#	dismiss.play()
	#	self.popout = LerpFunc(self.fadeOut,
    #        extraArgs=[self, game],
    #        fromData=1,
    #        toData=0,
    #        duration=0.25,
	#		blendType='easeOut',
    #        name="fadeo")
	#	self.popout.start()
	#	game.r1Running = False
	#	game.mouseLetGo = False
	#	gametext.Text.showText(game.game_text, game)
	#	game.setBarVisibility(True)
	#	game.speedStop = False
	
	def fadeOut(t, self, game):
		if (t <= 0):
			for node in self.mensaItems:
				node.removeNode()
			return
		for node in self.mensaItems:
			node.setColorScale(1, 1, 1, t)

	#def setFocus(self, game, focus):
	#	pass

r1 = Room1