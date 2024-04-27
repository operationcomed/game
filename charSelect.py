from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *

class CharSelect():
	buttonHoverScale = 1.2
	def hoverEffect(self, game, task):
		for button in game.charButtons:
			if (button.node().getState() == 2):
				button.setScale(game.buttonHoverScale*button.scale[0], game.buttonHoverScale*button.scale[1], game.buttonHoverScale*button.scale[2])
			else:
				button.setScale(button.scale)
		return Task.cont
	
	def characterSelect(self, game):
		self.game_i = game
		game.MMsensitivity = 0.005
		game.scaleFactorCS = 2.25
		game.background_x = (-16/18)*game.scaleFactorCS
		game.background_y = -0.5*game.scaleFactorCS
		game.card = game.aspect2d.attachNewNode(game.cm.generate())
		game.card.setScale((16/9)*game.scaleFactorCS, 1, 1*game.scaleFactorCS)

		game.tex = game.loader.loadTexture('assets/charselect/background.png')
		game.card.setTexture(game.tex)
		game.card.setPos(game.background_x, 0, game.background_y)

		BoyTexture = (game.loader.loadTexture("assets/charselect/boy.png"), game.loader.loadTexture("assets/charselect/boy.png"), game.loader.loadTexture("assets/charselect/girl_hover.avi"), game.loader.loadTexture("assets/charselect/boy.png"))
		game.boySelect = DirectButton(frameTexture=BoyTexture, relief='flat', pressEffect=0, frameSize=(-1, 1, -1,1))
		game.boySelect.setTransparency(True)
		game.boySelect.setSx(1024/226)

		GirlTexture = (game.loader.loadTexture("assets/charselect/girl.png"), game.loader.loadTexture("assets/charselect/girl.png"), game.loader.loadTexture("assets/charselect/girl_hover.avi"), game.loader.loadTexture("assets/charselect/girl.png"))
		game.girlSelect = DirectButton(frameTexture=GirlTexture, relief='flat', pressEffect=0, frameSize=(-1, 1, -1,1))
		game.girlSelect.setTransparency(True)
		game.girlSelect.setSx(1024/226)

		charDistance = 1.05
		game.boySelect.setPos(charDistance, 0, -0.25)
		game.girlSelect.setPos(-charDistance, 0, -0.25)

		game.charButtons = [game.boySelect, game.girlSelect]
		game.charNodes = [game.boySelect, game.girlSelect, game.card]


		game.taskMgr.add(game.moveBackground, "moveBackground")
		game.taskMgr.add(game.hoverEffectCHS, "charSelect")

		for char in game.charButtons:
			char.setTransparency(True)
			char.setScale((512/640) * 0.5, 0.5, 0.5)
			char.scale = char.getScale()
	
		def setCharacterA():
			game.character = 1
			game.backstoryVideo = "assets/backstories/Girl.avi"
			game.l2Video = "assets/media/l2_girl.avi"
			self.setCharacter(game)

		def setCharacterB():
			game.character = 2
			game.backstoryVideo = "assets/backstories/Boy.avi"
			game.l2Video = "assets/media/l2_boy.avi"
			self.setCharacter(game)

		game.girlSelect["command"] = setCharacterA
		game.boySelect["command"] = setCharacterB

	def setCharacter(game):
		print(game.character)
		
		game.taskMgr.remove("moveBackground")
		game.taskMgr.remove("charSelect")

		# bed scene
		game.cameraOffset = 4
		game.taskMgr.add(game.backstory, "backstory")

ch_select = CharSelect