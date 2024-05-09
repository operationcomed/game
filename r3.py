from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *
import gametext
import time

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Room3():

	ans = ['escape', 'curse', 'ghost']
	num = 1
	gameFinished = False

	def fourPics(self, game, l2):
		game.r3Running = True
		game.mouseLetGo = True
		game.speedStop = True
		gametext.Text.hideText(game.game_text, game)
		game.setBarVisibility(False)
		game.scaleFactorfourPics = 2
		game.cm = CardMaker('card')
		game.fourPicsImg = game.aspect2d.attachNewNode(game.cm.generate())
		game.fourPicsImg.setScale((16/9)*game.scaleFactorfourPics, 1, game.scaleFactorfourPics)

		game.tex = game.loader.loadTexture('assets/img/l2/fourPics/' + str(self.num) + '.png')
		game.fourPicsImg.setTexture(game.tex)
		game.fourPicsImg.setColorScale(1, 1, 1, 0)
		game.fourPicsImg.setTransparency(True)

		# these are the centers of the image
		game.fourPics_x = (-16/9/2)*game.scaleFactorfourPics
		game.fourPics_y = -0.5*game.scaleFactorfourPics

		game.fourPicsImg.setPos(game.fourPics_x, 0, game.fourPics_y)
		game.fourPicsImg.setTransparency(TransparencyAttrib.MAlpha)

		self.answer = DirectEntry(text="", scale=0.2, command=self.checkAnswer, text_align=TextNode.ACenter, extraArgs=[self, game, self.num, l2], entryFont=game.font, width=12, frameTexture=game.loader.loadTexture("assets/img/blank.png"), text_fg=(1,0.2,0.2,1), focus=1)

		self.answer.setPos(0, 0, -0.72)
		self.answer.setTransparency(TransparencyAttrib.MAlpha)

		self.pos1 = self.answer.posInterval(0.1, Point3(self.answer.getX()+0.1, 0, self.answer.getZ()), blendType='easeIn')
		self.pos2 = self.answer.posInterval(0.1, Point3(self.answer.getX()-0.1, 0, self.answer.getZ()), blendType='easeIn')
		self.pos3 = self.answer.posInterval(0.05, Point3(self.answer.getX(), 0, self.answer.getZ()), blendType='easeIn')

		self.fourPicsItems = [game.fourPicsImg, self.answer]

		animItem = []
		for node in self.fourPicsItems:
			animItem.append(LerpColorScaleInterval(node, 1.5, (1, 1, 1, 1), (1, 1, 1, 0)))
		anim = Parallel(*animItem, name="anim")
		anim.start()

	def checkAnswer(input, self, game, i, l2):
		if (input.lower() == self.ans[i-1]):
			print("yay")
			correct = game.loader.loadSfx("assets/sound/correct.mp3")
			correct.setVolume(game.volume)
			correct.play()
			self.answer.enterText('')
			self.nextPic(self, game, l2)
		else:
			shake = Sequence(self.pos1, self.pos2, self.pos1, self.pos2, self.pos3, name="shake")
			shake.start()
			self.answer.enterText('')
			print("naur")
			wrong = game.loader.loadSfx("assets/sound/wrong.mp3")
			wrong.setVolume(game.volume)
			wrong.play()
			game.mistakes += 1
			print(game.mistakes)
			self.answer.setFocus()
			
	def nextPic(self, game, l2):
		self.num += 1
		if (self.num > len(self.ans)):
			self.cleanUpGame(self, game, l2)
			return
		for node in self.fourPicsItems:
			node.remove_node()
		self.fourPics(self, game, l2)
		
	def cleanUpGame(self, game, l2):
		l2.addItem(l2, game, 'SHELL')
		dismiss = game.loader.loadSfx("assets/sound/dismiss.mp3")
		dismiss.setVolume(game.volume)
		dismiss.play()
		game.game_text.itcText.setTextColor(1, 1, 1, 1)
		self.popout = LerpFunc(self.fadeOut,
            extraArgs=[self, game],
            fromData=1,
            toData=0,
            duration=0.25,
			blendType='easeOut',
            name="fadeo")
		self.popout.start()
		game.r3Running = False
		game.mouseLetGo = False
		game.speedStop = False
		game.r3Done = True
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
	#		 blendType='easeOut',
    #        name="fadeo")
	#	self.popout.start()
	#	game.r3Running = False
	#	game.mouseLetGo = False
	#	gametext.Text.showText(game.game_text, game)
	#	game.setBarVisibility(True)
	#	game.speedStop = False
	
	def fadeOut(t, self, game):
		if (t <= 0):
			for node in self.fourPicsItems:
				node.removeNode()
			return
		for node in self.fourPicsItems:
			node.setColorScale(1, 1, 1, t)

	#def setFocus(self, game, focus):
	#	pass

r3 = Room3