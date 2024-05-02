from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *
import gametext
import time

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Room5():

	ans = ['escape', 'flower', 'journal', 'choke']
	finished = []
	num = 0
	gameFinished = False

	def wordSearch(self, game, l2):
		game.r5Running = True
		game.mouseLetGo = True
		game.speedStop = True
		gametext.Text.hideText(game.game_text, game)
		game.setBarVisibility(False)
		game.scaleFactorwordSearch = 2
		game.cm = CardMaker('card')
		game.wordSearchImg = game.aspect2d.attachNewNode(game.cm.generate())
		game.wordSearchImg.setScale((16/9)*game.scaleFactorwordSearch, 1, game.scaleFactorwordSearch)

		game.tex = game.loader.loadTexture('assets/img/l2/room5/'+str(self.num+1)+'.png')
		game.wordSearchImg.setTexture(game.tex)
		game.wordSearchImg.setColorScale(1, 1, 1, 0)
		game.wordSearchImg.setTransparency(True)

		# these are the centers of the image
		game.wordSearch_x = (-16/9/2)*game.scaleFactorwordSearch
		game.wordSearch_y = -0.5*game.scaleFactorwordSearch

		game.wordSearchImg.setPos(game.wordSearch_x, 0, game.wordSearch_y)
		game.wordSearchImg.setTransparency(TransparencyAttrib.MAlpha)

		self.answer = DirectEntry(text="",
							 scale=0.2, 
							 command=self.checkAnswer, 
							 text_align=TextNode.ACenter, 
							 extraArgs=[self, game, self.num, l2], 
							 entryFont=game.font, 
							 width=6, 
							 frameTexture=game.loader.loadTexture("assets/img/textbox.png"), 
							 text_fg=(1,1,1,1))

		self.answer.setPos(0.9, 0, -0.67)
		self.answer.setTransparency(TransparencyAttrib.MAlpha)

		self.pos1 = self.answer.posInterval(0.1, Point3(self.answer.getX()+0.1, 0, self.answer.getZ()), blendType='easeIn')
		self.pos2 = self.answer.posInterval(0.1, Point3(self.answer.getX()-0.1, 0, self.answer.getZ()), blendType='easeIn')
		self.pos3 = self.answer.posInterval(0.05, Point3(self.answer.getX(), 0, self.answer.getZ()), blendType='easeIn')

		self.wordSearchItems = [game.wordSearchImg, self.answer]

		animItem = []
		for node in self.wordSearchItems:
			animItem.append(LerpColorScaleInterval(node, 1.5, (1, 1, 1, 1), (1, 1, 1, 0)))
		anim = Parallel(*animItem, name="anim")
		anim.start()

	def checkAnswer(input, self, game, i, l2):
		print(input, self.ans[i])
		if (input == "uwu"):
			self.cleanUpGame(self, game, l2)
			return
		if (input.lower() == self.ans[i]):
			print("yay")
			correct = game.loader.loadSfx("assets/sound/correct.mp3")
			correct.setVolume(game.volume)
			correct.play()
			self.answer.enterText('')
			self.num += 1
			if (input.lower() == 'choke'):
				self.cleanUpGame(self, game, l2)
				return
			for node in self.wordSearchItems:
				node.remove_node()
			self.wordSearch(self, game, l2)
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
		
	def cleanUpGame(self, game, l2):
		l2.addItem(l2, game, 'DOG FANGS')
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
		game.r5Running = False
		game.mouseLetGo = False
		game.speedStop = False
		game.r5Done = True
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
	#	game.r5Running = False
	#	game.mouseLetGo = False
	#	gametext.Text.showText(game.game_text, game)
	#	game.setBarVisibility(True)
	#	game.speedStop = False
	
	def fadeOut(t, self, game):
		if (t <= 0):
			for node in self.wordSearchItems:
				node.removeNode()
			return
		for node in self.wordSearchItems:
			node.setColorScale(1, 1, 1, t)

	#def setFocus(self, game, focus):
	#	pass

r5 = Room5