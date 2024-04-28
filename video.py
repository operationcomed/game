from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import *
from direct.gui.DirectGui import *

class Video():
	
	def playVid(self, game, vidFile):
		game.isPlaying = True
		# this bg is here to prevent 3d game from being shown
		game.blackBg = OnscreenImage(image='assets/backstories/black.png', scale=(1000, 1, 1000))
		game.cm = CardMaker('card')
		game.cm.setFrameFullscreenQuad()
		game.scaleFactorVid = 1.9
		game.video = game.aspect2d.attachNewNode(game.cm.generate())
		game.video.setScale(game.scaleFactorVid, 1, game.scaleFactorVid)

		game.tex = MovieTexture("backstory")
		game.tex.read(vidFile)
		game.sound = game.loader.loadSfx(vidFile)
		game.sound.setVolume(game.volume)
		game.tex.synchronizeTo(game.sound)
		game.cm.setUvRange(game.tex)
		game.video.setTexture(game.tex)
		game.sound.setLoop(False)
		game.sound.play()

		game.background_x = 0.115
		game.background_y = 0.899

		game.video.setPos(game.background_x, 0, game.background_y)
		game.skipText = TextNode('items')
		game.skipText.setText(game.skipTextLabel)
		game.skipText.setShadow(0.15, 0.15)
		game.skipText.setFont(game.font)
		game.stnp = aspect2d.attachNewNode(game.skipText)
		game.stnp.setPos(-1.2, 0, 0.85)
		game.stnp.setScale(0.07)

video = Video