from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *
import gametext

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Room1():

	numPics = 6
	orders = ['136', '356']
	answerNum = 0
	answer = []

	def mensa(self, game, l2):
		game.r1Running = True
		game.mouseLetGo = True
		gametext.Text.hideText(game.game_text, game)
		game.setBarVisibility(False)
		game.scaleFactorMensa = 7/4
		game.cm = CardMaker('card')
		game.mensaImg = game.aspect2d.attachNewNode(game.cm.generate())
		game.mensaImg.setScale((16/9)*game.scaleFactorMensa, 1, game.scaleFactorMensa)

		game.tex = game.loader.loadTexture('assets/img/l2/mensa/bkg.png')
		game.mensaImg.setTexture(game.tex)

		game.mensaButtons = []

		i = 1
		while (i <= self.numPics):
			image = DirectButton(frameTexture=game.loader.loadTexture('assets/img/l2/mensa/' + str(i) + '.png'), pos=((i*0.25), 0, 0), scale=(0.25), relief='flat', pressEffect=0, frameSize=(-1, 1, -1, 1))
			image.setTransparency(True)
			game.mensaButtons.append(image)
			i += 1

		# these are the centers of the image
		game.mensa_x = (-16/9/2)*game.scaleFactorMensa
		game.mensa_y = -0.5*game.scaleFactorMensa

		game.mensaImg.setPos(game.mensa_x, 0, game.mensa_y)
		game.mensaImg.setTransparency(TransparencyAttrib.MAlpha)

		self.mensaItems = [game.mensaImg]

	def checkAnswer(self, game, i):
		if (self.answerNum):
			# do a
			''''''
			return
		
	#def inputAnswer(input, self, game, l2):
	#	answer = ""
	#	for char in input.lower():
	#		if (char != " " and char != "," and char != "."):
	#			answer += char
	#
	#	print(answer)
	#	if ((answer == self.answers[self.num - 1]) or (answer == "" and game.debug)):
	#		print("huwaw")
	#		correct = game.loader.loadSfx("assets/sound/correct.mp3")
	#		correct.setVolume(game.volume)
	#		correct.play()
	#		self.nextAnagram(self, game, l2)
	#	else:
	#		shake = Sequence(self.pos1, self.pos2, self.pos1, self.pos2, self.pos3, name="shake")
	#		shake.start()
	#		self.answer.enterText('')
	#		wrong = game.loader.loadSfx("assets/sound/wrong.mp3")
	#		wrong.setVolume(game.volume)
	#		wrong.play()

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
	
	#def fadeOut(t, self, game):
	#	if (t <= 0):
	#		for node in self.mensaItems:
	#			node.removeNode()
	#		return
	#	for node in self.mensaItems:
	#		node.setColorScale(1, 1, 1, t)
	#	game.mensaImg.setScale(min(16/9*t*game.scaleFactorMission, 16/9*game.scaleFactorMission), min(t*game.scaleFactorMission, 1*game.scaleFactorMission), min(t*game.scaleFactorMission, 1*game.scaleFactorMission))

	#def setFocus(self, game, focus):
	#	pass

r1 = Room1