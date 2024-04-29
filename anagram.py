from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *
import gametext

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Anagram():

	answers = [
		"you'vebeencursed",
		"finisheachminigame",
		"collecteachingredient",
		"craftthepotion",
		"escapemsu",
	]
	num = 1

	def anagram(self, game, l2):
		game.anagramRunning = True
		game.mouseLetGo = True
		gametext.Text.hideText(game.game_text, game)
		game.setBarVisibility(False)
		game.speedStop = True
		game.scaleFactorAnagram = 7/4
		game.cm = CardMaker('card')
		game.anagramImg = game.aspect2d.attachNewNode(game.cm.generate())
		game.anagramImg.setScale((16/9)*game.scaleFactorAnagram, 1, game.scaleFactorAnagram)

		game.tex = game.loader.loadTexture('assets/media/l2/' + str(self.num) + '.png')
		game.anagramImg.setTexture(game.tex)

		# these are the centers of the image
		game.mission_x = (-16/9/2)*game.scaleFactorMission
		game.mission_y = -0.5*game.scaleFactorMission

		game.anagramImg.setPos(game.mission_x, 0, game.mission_y)
		game.anagramImg.setTransparency(TransparencyAttrib.MAlpha)

		self.answer = DirectEntry(text="", scale=0.1, command=self.inputAnswer, extraArgs=[self, game, l2], focus=1, focusInCommand=self.setFocus, focusInExtraArgs=[self, game, True], focusOutCommand=self.setFocus, focusOutExtraArgs=[self, game, False], entryFont=game.font, width=16, text_align=TextNode.ACenter, frameTexture=game.loader.loadTexture("assets/img/textbox.png"))

		self.answer.setPos(0, 0, -0.4)
		self.answer.setTransparency(TransparencyAttrib.MAlpha)

		self.pos1 = self.answer.posInterval(0.1, Point3(0.1, 0, -0.4), blendType='easeIn')
		self.pos2 = self.answer.posInterval(0.1, Point3(-0.1, 0, -0.4), blendType='easeIn')
		self.pos3 = self.answer.posInterval(0.05, Point3(0, 0, -0.4), blendType='easeIn')

		self.anagramItems = [game.anagramImg, self.answer]

	def inputAnswer(input, self, game, l2):
		answer = ""
		for char in input.lower():
			if (char != " " and char != "," and char != "."):
				answer += char

		print(answer)
		if ((answer == self.answers[self.num - 1]) or (answer == "" and game.debug)):
			print("huwaw")
			correct = game.loader.loadSfx("assets/sound/correct.mp3")
			correct.setVolume(game.volume)
			correct.play()
			self.nextAnagram(self, game, l2)
		else:
			shake = Sequence(self.pos1, self.pos2, self.pos1, self.pos2, self.pos3, name="shake")
			shake.start()
			self.answer.enterText('')
			wrong = game.loader.loadSfx("assets/sound/wrong.mp3")
			wrong.setVolume(game.volume)
			wrong.play()


	def nextAnagram(self, game, l2):
		self.num += 1
		if (self.num > len(self.answers)):
			self.clearAnagrams(self, game)
			return
		for node in self.anagramItems:
			node.remove_node()
		self.anagram(self, game, l2)

	def clearAnagrams(self, game):
		dismiss = game.loader.loadSfx("assets/sound/dismiss.mp3")
		dismiss.setVolume(game.volume)
		dismiss.play()
		self.popout = LerpFunc(self.fadeOut,
            extraArgs=[self, game],
            fromData=1,
            toData=0,
            duration=0.25,
			blendType='easeOut',
            name="fadeo")
		self.popout.start()
		game.anagramRunning = False
		game.mouseLetGo = False
		gametext.Text.showText(game.game_text, game)
		game.setBarVisibility(True)
		game.speedStop = False

	
	def fadeOut(t, self, game):
		if (t <= 0):
			for node in self.anagramItems:
				node.removeNode()
			return
		for node in self.anagramItems:
			node.setColorScale(1, 1, 1, t)
		game.anagramImg.setScale(min(16/9*t*game.scaleFactorMission, 16/9*game.scaleFactorMission), min(t*game.scaleFactorMission, 1*game.scaleFactorMission), min(t*game.scaleFactorMission, 1*game.scaleFactorMission))

	def setFocus(self, game, focus):
		pass

ag = Anagram