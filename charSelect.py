from panda3d.core import *
from direct.gui.DirectGui import *

class CharSelect():
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

		game.boyPreview = (game.loader.loadTexture("assets/charselect/boy.png"))
		game.girlPreview = (game.loader.loadTexture("assets/charselect/girl.png"))

		game.boySelect = DirectButton(frameTexture=game.boyPreview, relief='flat', pressEffect=0, frameSize=(-1, 1, -1, 1))
		game.girlSelect = DirectButton(frameTexture=game.girlPreview, relief='flat', pressEffect=0, frameSize=(-1, 1, -1, 1))
		charDistance = 1.05
		game.boySelect.setPos(charDistance, 0, -0.25)
		game.girlSelect.setPos(-charDistance, 0, -0.25)

		game.charButtons = [game.boySelect, game.girlSelect]
		game.charNodes = [game.boySelect, game.girlSelect, game.card]

		game.taskMgr.add(game.moveBackground, "moveBackground")

		for char in game.charButtons:
			char.setTransparency(True)
			char.setScale((512/640) * 0.5, 0.5, 0.5)
		# i wish there was like a 'this' from js in python so i could see what the pressed thing is so i dont have to do this stupid stuff
			# ^^^ incomprehendable
	
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
		for node in game.charNodes:
			node.removeNode()

		# bed scene
		game.cameraOffset = 4
		game.loadScene("assets/models/bed.glb", (3.5, 6, 1.42), (0, 0, 10), doors=False, customTask=game.bedDoor, playerRot=(180, -90, 0))
		game.helpMenu()
		game.itmTxtNode.hide()
		game.taskMgr.add(game.backstory, "backstory")

ch_select = CharSelect