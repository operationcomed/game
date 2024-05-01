from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *
import gametext
import time

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Room4():

	ans = ['justice', 'answers', 'revenge', 'cursed', 'abused', 'escape']
	finished = []
	num = 0
	gameFinished = False

	def wordSearch(self, game, l2):
		game.r4Running = True
		game.mouseLetGo = True
		game.speedStop = True
		gametext.Text.hideText(game.game_text, game)
		game.setBarVisibility(False)
		game.scaleFactorwordSearch = 2
		game.cm = CardMaker('card')
		game.wordSearchImg = game.aspect2d.attachNewNode(game.cm.generate())
		game.wordSearchImg.setScale((16/9)*game.scaleFactorwordSearch, 1, game.scaleFactorwordSearch)

		game.tex = game.loader.loadTexture('assets/img/l2/wordSearch/bkg.png')
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
							 extraArgs=[self, game, l2], 
							 entryFont=game.font, 
							 width=6, 
							 frameTexture=game.loader.loadTexture("assets/img/textbox.png"), 
							 text_fg=(1,1,1,1))

		self.answer.setPos(1.3, 0, -0.67)
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

	def checkAnswer(input, self, game, l2):
		i = 0
		if (self.num > len(self.ans)):
			self.cleanUpGame(self, game, l2)
			return
		for ans in self.ans:
			if (input.lower() == ans):
				print("yay", ans)
				self.num += 1
				correct = game.loader.loadSfx("assets/sound/correct.mp3")
				correct.setVolume(game.volume)
				correct.play()
				self.answer.enterText('')
				self.finished.append(ans)
				print(self.finished)
				self.ans.remove(ans)
				guess = TextNode('thing')
				guess.setAlign(TextNode.ACenter)
				guess.setText(ans)
				guess.setShadow(0.07, 0.07)
				guessText = game.aspect2d.attachNewNode(guess)
				game.attachTextToHUD(guessText, guess, (0.5, 0, (-self.num*0.1)+1), 0.15, game.font)
				self.wordSearchItems.append(guess)
				return
			else:
				shake = Sequence(self.pos1, self.pos2, self.pos1, self.pos2, self.pos3, name="shake")
				shake.start()
				self.answer.enterText('')
				print("naur")
				game.mistakes += 1
				print(game.mistakes)
			i += 1
			
		wrong = game.loader.loadSfx("assets/sound/wrong.mp3")
		wrong.setVolume(game.volume)
		wrong.play()
		
	def cleanUpGame(self, game, l2):
		l2.addItem(l2, game, 'SPOON')
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
		game.r4Running = False
		game.mouseLetGo = False
		game.speedStop = False
		game.r4Done = True
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
	#	game.r4Running = False
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

r4 = Room4