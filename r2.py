from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *
import gametext
import time

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Room2():

	ans = 'msu'
	gameFinished = False

	def padlock(self, game, l2):
		game.r2Running = True
		game.mouseLetGo = True
		game.speedStop = True
		gametext.Text.hideText(game.game_text, game)
		game.setBarVisibility(False)
		game.scaleFactorpadlock = 2
		game.cm = CardMaker('card')
		game.padlockImg = game.aspect2d.attachNewNode(game.cm.generate())
		game.padlockImg.setScale((16/9)*game.scaleFactorpadlock, 1, game.scaleFactorpadlock)

		game.tex = game.loader.loadTexture('assets/img/l2/padlock/bkg.png')
		game.padlockImg.setTexture(game.tex)
		game.padlockImg.setColorScale(1, 1, 1, 0)
		game.padlockImg.setTransparency(True)

		# these are the centers of the image
		game.padlock_x = (-16/9/2)*game.scaleFactorpadlock
		game.padlock_y = -0.5*game.scaleFactorpadlock

		game.padlockImg.setPos(game.padlock_x, 0, game.padlock_y)
		game.padlockImg.setTransparency(TransparencyAttrib.MAlpha)

		self.answer = DirectEntry(text="", scale=(0.325, 0.325, 0.225), text_scale=(1, 0.325/0.225), command=self.checkAnswer, extraArgs=[self, game, l2], entryFont=game.font, width=2.25, frameTexture=game.loader.loadTexture("assets/img/blank.png"), text_fg=(1,1,1,1))

		self.answer.setPos(-1.25, 0, -0.45)
		self.answer.setTransparency(TransparencyAttrib.MAlpha)

		self.pos1 = self.answer.posInterval(0.1, Point3(self.answer.getX()+0.1, 0, self.answer.getZ()), blendType='easeIn')
		self.pos2 = self.answer.posInterval(0.1, Point3(self.answer.getX()-0.1, 0, self.answer.getZ()), blendType='easeIn')
		self.pos3 = self.answer.posInterval(0.05, Point3(self.answer.getX(), 0, self.answer.getZ()), blendType='easeIn')

		self.padlockItems = [game.padlockImg, self.answer]

		animItem = []
		for node in self.padlockItems:
			animItem.append(LerpColorScaleInterval(node, 1.5, (1, 1, 1, 1), (1, 1, 1, 0)))
		anim = Parallel(*animItem, name="anim")
		anim.start()

	def checkAnswer(input, self, game, l2):
		if (input.lower() == self.ans):
			print("yay")
			dismiss = game.loader.loadSfx("assets/sound/dismiss.mp3")
			dismiss.setVolume(game.volume)
			dismiss.play()
			correct = game.loader.loadSfx("assets/sound/correct.mp3")
			correct.setVolume(game.volume)
			correct.play()
			game.r2Done = True
			l2.addItem(l2, game, 'MANDRAKE')
			self.cleanUpGame(self, game, l2)
			return
		
		shake = Sequence(self.pos1, self.pos2, self.pos1, self.pos2, self.pos3, name="shake")
		shake.start()
		self.answer.enterText('')
		print("naur")
		wrong = game.loader.loadSfx("assets/sound/wrong.mp3")
		wrong.setVolume(game.volume)
		wrong.play()
		game.mistakes += 1
		print(game.mistakes)
		return
			
	def cleanUpGame(self, game, l2):
		game.game_text.itcText.setTextColor(1, 1, 1, 1)
		self.popout = LerpFunc(self.fadeOut,
            extraArgs=[self, game],
            fromData=1,
            toData=0,
            duration=0.25,
			blendType='easeOut',
            name="fadeo")
		self.popout.start()
		game.r2Running = False
		game.mouseLetGo = False
		game.speedStop = False
		game.r2Done = True
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
	#	game.r2Running = False
	#	game.mouseLetGo = False
	#	gametext.Text.showText(game.game_text, game)
	#	game.setBarVisibility(True)
	#	game.speedStop = False
	
	def fadeOut(t, self, game):
		if (t <= 0):
			for node in self.padlockItems:
				node.removeNode()
			return
		for node in self.padlockItems:
			node.setColorScale(1, 1, 1, t)

	#def setFocus(self, game, focus):
	#	pass

r2 = Room2