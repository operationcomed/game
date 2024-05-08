from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *
import gametext
import time

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Potion():

	numPics = 5
	# :)
	order = [1, 2, 3, 4, 5]
	gameFinished = False
	num = 1

	def potion(self, game, l2):
		game.textObjects.append(l2.timeTxtNode)
		l2.timeTxtNode.setColorScale(1, 1, 1, 0)
		game.ptRunning = True
		game.mouseLetGo = True
		game.speedStop = True
		gametext.Text.hideText(game.game_text, game)
		game.setBarVisibility(False)
		game.scaleFactorPotion = 2
		game.cm = CardMaker('card')
		game.potionImg = game.aspect2d.attachNewNode(game.cm.generate())
		game.potionImg.setScale((16/9)*game.scaleFactorPotion, 1, game.scaleFactorPotion)

		game.tex = game.loader.loadTexture('assets/img/l2/potion/' + str(self.num) + '.png')
		game.potionImg.setTexture(game.tex)
		game.potionImg.setColorScale(1, 1, 1, 0)
		game.potionImg.setTransparency(True)

		if (self.num == 1):
			game.potionButtons = []
			ingredients = [(-1.3, 0, -0.5), (-0.85, 0, -0.2), (0.85, 0, -0.2), (1.3, 0, -0.5), (-0.85, 0, -0.7)]

			i = 1
			for item in ingredients:
				image = DirectButton(command=self.checkAnswer, extraArgs=[self, game, i, l2], frameTexture=game.loader.loadTexture('assets/img/l2/potion/ing/' + str(i) + '.png'), pos=item, scale=(0.25), relief='flat', pressEffect=0, frameSize=(-1, 1, -1, 1))
				image.setTransparency(True)
				game.potionButtons.append(image)
				i += 1


		# these are the centers of the image
		game.potion_x = (-16/9/2)*game.scaleFactorPotion
		game.potion_y = -0.5*game.scaleFactorPotion

		game.potionImg.setPos(game.potion_x, 0, game.potion_y)
		game.potionImg.setTransparency(TransparencyAttrib.MAlpha)

		self.potionItems = [game.potionImg, *game.potionButtons]

		animItem = []
		for node in self.potionItems:
			animItem.append(LerpColorScaleInterval(node, 1.5, (1, 1, 1, 1), (1, 1, 1, 0)))
		anim = Parallel(*animItem, name="anim")
		anim.start()

	def checkAnswer(self, game, i, l2):
		print(i, self.order[self.num-1])
		if (i == self.order[self.num-1]):
			game.potionButtons[self.num-1].removeNode()
			if (self.num >= self.numPics):
				self.cleanUpGame(self, game, l2)
				return
			self.num += 1
			game.tex = game.loader.loadTexture('assets/img/l2/potion/' + str(self.num) + '.png')
			game.potionImg.setTexture(game.tex)
			pickup = game.loader.loadSfx('assets/sound/pickup.wav')
			pickup.setLoop(False)
			pickup.setVolume(game.volume)
			pickup.play()
		else:
			wrong = game.loader.loadSfx("assets/sound/wrong.mp3")
			wrong.setVolume(game.volume)
			wrong.play()
			
	def cleanUpGame(self, game, l2):
		correct = game.loader.loadSfx("assets/sound/correct.mp3")
		correct.setVolume(game.volume)
		correct.play()
		game.game_text.itcText.setTextColor(1, 1, 1, 1)
		self.popout = LerpFunc(self.fadeOut,
            extraArgs=[self, game],
            fromData=1,
            toData=0,
            duration=0.25,
			blendType='easeOut',
            name="fadeo")
		self.popout.start()
		game.ptRunning = False
		game.mouseLetGo = False
		game.speedStop = False
		gametext.Text.showText(game.game_text, game)
		game.setBarVisibility(True)
		l2.nextLevel(l2, game)
	
	def fadeOut(t, self, game):
		if (t <= 0):
			for node in self.potionItems:
				node.removeNode()
			return
		try:
			for node in self.potionItems:
				node.setColorScale(1, 1, 1, t)
		except:
			pass

	#def setFocus(self, game, focus):
	#	pass

pt = Potion