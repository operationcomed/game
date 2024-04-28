from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
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
		if (self.num > len(self.answers)):
			return
		game.anagramRunning = True
		game.mouseLetGo = True
		gametext.Text.hideText(game.game_text)
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

		self.answer = DirectEntry(text="", scale=0.1, command=self.inputAnswer, extraArgs=[self, game, l2], focus=1, focusInCommand=self.setFocus, focusInExtraArgs=[self, game, True], focusOutCommand=self.setFocus, focusOutExtraArgs=[self, game, False], entryFont=game.font, width=16)

		self.answer.setPos(-0.8, 0, -0.4)

		self.anagramItems = [game.anagramImg, self.answer]

	def inputAnswer(input, self, game, l2):
		answer = ""
		for char in input.lower():
			if (char != " " and char != "," and char != "."):
				answer += char

		print(answer)
		if (answer == self.answers[self.num - 1]):
			print("huwaw")
			correct = game.loader.loadSfx("assets/sound/correct.mp3")
			correct.setVolume(game.volume)
			correct.play()
			self.nextAnagram(self, game, l2)
		else:
			self.answer.enterText('')
			wrong = game.loader.loadSfx("assets/sound/wrong.mp3")
			wrong.setVolume(game.volume)
			wrong.play()


	def nextAnagram(self, game, l2):
		self.num += 1
		for node in self.anagramItems:
			node.remove_node()
		if (self.num > len(self.answers)):
			self.clearAnagrams(self, game)
		self.anagram(self, game, l2)

	def clearAnagrams(self, game):
		dismiss = game.loader.loadSfx("assets/sound/dismiss.mp3")
		dismiss.setVolume(game.volume)
		dismiss.play()
		game.anagramRunning = False
		game.mouseLetGo = False
		gametext.Text.showText(game.game_text)
		game.setBarVisibility(True)
		game.speedStop = False

	def setFocus(self, game, focus):
		pass
	#	game.answer = focus

ag = Anagram