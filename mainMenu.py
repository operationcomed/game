from direct.showbase.ShowBase import ShowBase
from direct.showbase import Audio3DManager
from math import pi, sin, cos
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from direct.gui.OnscreenText import OnscreenText
from direct.filter.CommonFilters import CommonFilters
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import *
from direct.gui.DirectGui import *
from panda3d.physics import ActorNode, ForceNode, LinearVectorForce, PhysicsCollisionHandler
import time
import gametext

class MainMenu():
	def mainInit(self, game):
		def mute():
			if (game.musicActive):
				game.music.setVolume(0)
				game.muteButton["frameTexture"] = game.unmuteTexture
			else:
				game.music.setVolume(game.volume)
				game.muteButton["frameTexture"] = game.muteTexture
			game.musicActive = not game.musicActive
			print(game.musicActive)
		game.sensitivity = 0.025
		game.scaleFactor = 3
		game.scaleFactorLogo = 0.2
	
		game.cm = CardMaker('video')
		#game.video = game.aspect2d.attachNewNode(game.cm.generate())
		#game.video.setScale((2))
		#game.tex = game.loader.loadTexture('assets/media/helloworld.avi')
		#game.video.setTexture(game.tex)
		
		if (game.musicPlaying == False):
			game.music = game.loader.loadSfx("assets/sound/main_menu.mp3")
			game.music.setVolume(game.volume)
			game.music.setLoop(True)
			game.music.play()
			game.musicPlaying = True

		game.scaleFactor = 3
		game.scaleFactorLogo = 0.35
		x_offset = -0.95
		
		game.cm = CardMaker('card')
		game.card = game.aspect2d.attachNewNode(game.cm.generate())
		game.logo = game.aspect2d.attachNewNode(game.cm.generate())
		game.card.setScale((16/9)*game.scaleFactor, 1, 1*game.scaleFactor)
		game.logo.setScale((746/168)*game.scaleFactorLogo, 1, 1*game.scaleFactorLogo)

		game.tex = game.loader.loadTexture('assets/media/bkgnew.png')
		game.card.setTexture(game.tex)
		game.tex = game.loader.loadTexture('assets/media/logo.png')
		game.logo.setTexture(game.tex)

		# these are the centers of the images
		game.background_x = (-16/18)*game.scaleFactor
		game.background_y = -0.5*game.scaleFactor
		game.logo_x = (-746/168/2)*game.scaleFactorLogo
		game.logo_y = -0.5*game.scaleFactorLogo

		game.card.setPos(game.background_x, 0, game.background_y)
		game.logo.setPos(game.logo_x + x_offset, 0, game.logo_y + 0.5)
		game.logo.setTransparency(TransparencyAttrib.MAlpha)

		# buttons
		# play
		playTexture = (game.loader.loadTexture("assets/buttons/play_normal.png"), game.loader.loadTexture("assets/buttons/play_normal.png"), game.loader.loadTexture("assets/buttons/play_hover.png"), game.loader.loadTexture("assets/buttons/play_normal.png"))
		game.startGameButton = DirectButton(command=game.initGame, frameTexture=playTexture, relief='flat', pressEffect=0, frameSize=(-1, 1, -1,1))
		game.startGameButton.setTransparency(True)
		game.startGameButton.setSx(482/226)

		# settings
		settingsTexture = (game.loader.loadTexture("assets/buttons/settings_normal.png"), game.loader.loadTexture("assets/buttons/settings_normal.png"), game.loader.loadTexture("assets/buttons/settings_hover.png"), game.loader.loadTexture("assets/buttons/settings_normal.png"))
		game.settingsButton = DirectButton(command=game.settings, frameTexture=settingsTexture, relief='flat', pressEffect=0, frameSize=(-1, 1, -1,1))
		game.settingsButton.setTransparency(True)
		game.settingsButton.setSx(1024/226)

		# exit
		exitGameTexture = (game.loader.loadTexture("assets/buttons/exit_normal.png"), game.loader.loadTexture("assets/buttons/exit_normal.png"), game.loader.loadTexture("assets/buttons/exit_hover.png"), game.loader.loadTexture("assets/buttons/exit_normal.png"))
		game.exitGameButton = DirectButton(command=game.exitGame, frameTexture=exitGameTexture, relief='flat', pressEffect=0, frameSize=(-1, 1, -1,1))
		game.exitGameButton.setTransparency(True)
		game.exitGameButton.setSx(482/226)

		
		game.muteTexture = (game.loader.loadTexture("assets/buttons/mute.png"))
		game.unmuteTexture = (game.loader.loadTexture("assets/buttons/unmute.png"))
		game.muteButton = DirectButton(command=mute, frameTexture=game.muteTexture, relief='flat', pressEffect=0, frameSize=(-1, 1, -1,1))
		game.muteButton.setTransparency(True)
		game.muteButton.setSx(1)

		# y'know what'd be better
		# positioning the offsets to be relative to the window bounds
		# but noooooooooo i guess we have to do it this way
		# :( 
		game.startGameButton.setPos(x_offset, 0, 0.2)
		game.settingsButton.setPos(x_offset, 0, -0.2)
		game.exitGameButton.setPos(x_offset, 0, -0.6)
		game.muteButton.setPos(1.575, -1.5, -0.8)

		game.menuItems = [game.video, game.startGameButton, game.settingsButton, game.exitGameButton, game.card, game.logo, game.muteButton,]

		game.buttonList = [game.startGameButton, game.settingsButton, game.exitGameButton, game.muteButton]
		game.buttonScale = 0.1

		# laziness will consume
		for button in game.buttonList:
			button.setScale(button.getSx()*game.buttonScale, game.buttonScale, game.buttonScale)

		game.startGameButton.scale = game.startGameButton.getScale()
		game.settingsButton.scale = game.settingsButton.getScale()
		game.exitGameButton.scale = game.exitGameButton.getScale()
		game.muteButton.scale = game.muteButton.getScale()

		game.taskMgr.add(game.moveBackground, "mainMenu")
		game.taskMgr.add(game.hoverEffect, "mainMenu")

	
	def settings(self, game):
		def toggleFullscreenViaButton():
			if (game.fullscreen == False):
				game.fullscreenButton['frameTexture'] = game.fullscreenTextureOn
			if (game.fullscreen == True):
				game.fullscreenButton['frameTexture'] = game.fullscreenTextureOff
			game.toggleFullscreen()
		def changeVol():
			game.volume = game.soundSlider['value']
			game.music.setVolume(game.volume)
			game.volumeText.setText(str(int(round(game.volume, 2) * 100)) + "%")
		def backSettings():
			for node in game.settingsItems:
				node.removeNode()
			game.taskMgr.remove("mainMenu")
			game.mainMenu()
		for node in game.menuItems:
			if (node == game.card):
				continue
			node.removeNode()
		game.taskMgr.remove("mainMenu")
		game.taskMgr.add(game.moveBackground, "mainMenu")


		backTexture = (game.loader.loadTexture("assets/buttons/exit_normal.png"), game.loader.loadTexture("assets/buttons/exit_normal.png"), game.loader.loadTexture("assets/buttons/exit_hover.png"), game.loader.loadTexture("assets/buttons/exit_normal.png"))
		game.backButton = DirectButton(command=backSettings, frameTexture=backTexture, relief='flat', pressEffect=0, frameSize=(-1, 1, -1,1))
		game.backButton.setTransparency(True)
		game.backButton.setSx(482/226)
		game.backButton.setPos(-1.2, 0, 0.6)

		game.fullscreenTextureOff = (game.loader.loadTexture("assets/buttons/fullscreen_on.png"))
		game.fullscreenTextureOn = (game.loader.loadTexture("assets/buttons/fullscreen_off.png"))
		if (game.fullscreen):
			fullscreenTexture = game.fullscreenTextureOn
		else:
			fullscreenTexture = game.fullscreenTextureOff
		game.fullscreenButton = DirectButton(command=toggleFullscreenViaButton, frameTexture=fullscreenTexture, relief='flat', pressEffect=0, frameSize=(-1, 1, -1,1))
		game.fullscreenButton.setTransparency(TransparencyAttrib.MAlpha)
		game.fullscreenButton.setScale(0.1)
		game.fullscreenButton.setPos(0, 0, -0.2)

		soundSliderBg = loader.loadTexture("assets/buttons/slider_bkg.png")
		soundSliderThumb = loader.loadTexture("assets/buttons/slider_thumb.png")

		game.soundSliderText = TextNode('volume')
		game.soundSliderText.setText("Volume:")
		game.soundSliderText.setShadow(0.07, 0.07)
		game.soundSliderText.setFont(game.font)
		game.soSlNode = aspect2d.attachNewNode(game.soundSliderText)
		game.soSlNode.setScale(0.12)
		game.soSlNode.setPos(-0.62, 0, 0.08)
		
		game.volumeText = TextNode('volume')
		game.volumeText.setText(str(int(round(game.volume, 2) * 100)) + "%")
		game.volumeText.setShadow(0.07, 0.07)
		game.volumeText.setFont(game.font)
		game.vTNode = aspect2d.attachNewNode(game.volumeText)
		game.vTNode.setScale(0.1)
		game.vTNode.setPos(0.62, 0, 0)

		game.soundSlider = DirectSlider(value=game.volume, pos=(0, 0, 0), scale=(0.6), range=(0, 1), frameTexture=soundSliderBg, command=changeVol, thumb_frameTexture=soundSliderThumb, thumb_pressEffect=0, thumb_frameSize=(-0.075, 0.075, -0.075, 0.075), thumb_relief='flat')
		game.soundSlider.setTransparency(TransparencyAttrib.MAlpha)

		game.settingsButtons = [game.backButton]
		for button in game.settingsButtons:
			button.setScale(button.getSx()*game.buttonScale, game.buttonScale, game.buttonScale)
		game.settingsItems = [game.backButton, game.soundSlider, game.soSlNode, game.vTNode, game.card, game.fullscreenButton]


main_menu = MainMenu