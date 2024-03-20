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

# function shorthand
KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton
# tentative jumping solution
#GROUND_POS = 2

# antialiasing
loadPrcFileData("", "framebuffer-multisample 1")
loadPrcFileData("", "multisamples 4")

# window
loadPrcFileData("", "window-title Escape MSU")
loadPrcFileData("", 'win-size 1366 720') 
loadPrcFileData("", "default-fov 60")

loadPrcFileData("", "shadow-cube-map-filter true")

class Game(ShowBase):

	accelZ = 0
	#accelZCap = 1

	accelX = 0
	#accelXCap = 0.4
	accelY = 0
	#accelYCap = 0.4
	game_text = gametext.game_text

	fog_color = (0.2, 0.3, 0.35)
	
	scene_rot = 1

	# 0: none
	# 1: girl
	# 2: boy
	character = 0
	
	def __init__(self):
		ShowBase.__init__(self)
		
		props = WindowProperties()
		props.set_icon_filename("icon.png")
		self.win.request_properties(props)

		# antialiasing
		self.render.setAntialias(AntialiasAttrib.MAuto)
		
		self.render.setShaderAuto()

		# camera
		self.camLens.setNearFar(1, 1000)
		#video before main menu
		self.mainMenu()
	
	def loadScene(self):
		self.music.stop()
		self.disable_mouse()

		# antialiasing
		self.render.setAntialias(AntialiasAttrib.MAuto)
		
		self.render.setShaderAuto()

		# camera
		self.camLens.setNearFar(0.1, 10000000)

		# tentative scene
		self.scene = self.loader.loadModel("inf.glb")

		self.scene.reparentTo(self.render)

		self.scene.setScale(1.25, 1.25, 1.25)
		#self.scene.setPos(0, 128, 6.8)

		self.scene.setShaderOff()
		self.scene.setTwoSided(False)

		# for some reason the scene is rotated 90 degrees on one computer but normal on the other
		self.scene.setHpr(0, 0, 0)

		self.scene.setCollideMask(BitMask32.bit(0))
		self.enableParticles()


		# lights and shadows
		alight = AmbientLight("alight1")
		alnp = self.render.attachNewNode(alight)
		alight.setColor((.35, .45, .5, 1))

		self.slight = PointLight('slight')
		self.slight.setColor((1, 1, 1, 1))
		#self.lens = PerspectiveLens()
		#self.slight.setLens(self.lens)
		#self.slight.attenuation = (0, 0, 1)
		self.slnp = self.render.attachNewNode(self.slight)
		self.slnp.node().setShadowCaster(True, 1024, 1024)
		self.slnp.setPos(0, 0, 8.5)
		self.slnp.setHpr(0, -90, 0)
		#self.lens.setNearFar(1, 1000000)

		self.render.setLight(self.slnp)
		self.render.setLight(alnp)
		self.setBackgroundColor(self.fog_color)

		self.sunActor = Actor("models/smiley")

		self.sunActor.reparentTo(self.slnp)
		self.sunActor.setColor(600, 600, 600)

		# remove the shader for the sun because the sun shouldnt have a shadow
		self.sunActor.setShaderOff()

		# player + physics
		self.playerCharacter = Actor()

		self.playerPhysics = ActorNode("player-physics")
		self.ppnp = self.render.attachNewNode(self.playerPhysics)
		self.physicsMgr.attachPhysicalNode(self.playerPhysics)
		self.colliderNode = self.ppnp.attachNewNode(CollisionNode('colNode'))
		self.colliderNode.node().addSolid(CollisionTube(0, 0, 0, 0, 1, 2.4, 1))

		self.gravity = ForceNode("gravity")
		self.gnp = self.render.attachNewNode(self.gravity)
		self.gravity_amt = LinearVectorForce(0, 0, -10)
		self.gravity.addForce(self.gravity_amt)
		self.physicsMgr.addLinearForce(self.gravity_amt)
		self.playerPhysics.getPhysicsObject().setMass(45)

		self.playerCharacter.reparentTo(self.ppnp)
		#self.ppnp.reparentTo(self.camera)
		self.playerCharacter.loop("walk")

		# https://arsthaumaturgis.github.io/Panda3DTutorial.io/tutorial/tut_lesson06.html
		self.cTrav = CollisionTraverser()
		self.pusher = PhysicsCollisionHandler()
		self.pusher.addCollider(self.colliderNode, self.ppnp)
		self.cTrav.addCollider(self.colliderNode, self.pusher)
		
		#self.colliderNode.show()

		# tasks
		self.taskMgr.add(self.moveTask, "moveTask")
		#self.taskMgr.add(self.coordinateTask, "coordinateTask")
		
		# filters 
		filters = CommonFilters(self.win, self.cam)
		filters.setAmbientOcclusion(numsamples=128, amount=2, strength=5)
		#filters.setBloom(intensity=0.1)

		# fog
		fog = Fog("Fog")
		fog.setColor(LVecBase4f(self.fog_color))
		fog.setExpDensity(0.045)
		self.render.setFog(fog)

		# text
		
		self.textNodePath = aspect2d.attachNewNode(self.game_text.ctlText)
		self.textNodePath.setScale(0.07)
		self.textNodePath.setPos(-1.2, 0, 0.9)

		self.textNodePath = aspect2d.attachNewNode(self.game_text.escText)
		self.textNodePath.setScale(0.07)
		self.textNodePath.setPos(-1.2, 0, -0.85)

	timer = 0
	# basic player movement
	def moveTask(self, task):
		button_down = self.mouseWatcherNode.is_button_down
		if (button_down(KB_BUTTON('x'))):
			exit()

		has_mouse = self.mouseWatcherNode.hasMouse()
		rot_x = self.camera.getH()
		rot_y = self.camera.getP()
		rot_z = self.camera.getR()

		sensitivity = 30
		
		props = WindowProperties()
		if (button_down(KB.escape())):
			has_mouse = False

		# move screen with mouse
		if (has_mouse):
			# hides cursor
			props.setCursorHidden(True)
			self.win.requestProperties(props)
			props = self.win.getProperties()

			# limits cursor to the middle
			self.win.movePointer(0, props.getXSize() // 2, props.getYSize() // 2)
			mouse_x = self.mouseWatcherNode.getMouseX() * sensitivity
			mouse_y = self.mouseWatcherNode.getMouseY() * sensitivity

			# prevent camera from going upside down
			if (rot_y+mouse_y > 90):
				self.camera.setHpr(rot_x-mouse_x, 90, 0)
			elif (rot_y+mouse_y < -90):
				self.camera.setHpr(rot_x-mouse_x, -90, 0)
			else:
				self.camera.setHpr(rot_x-mouse_x, rot_y+mouse_y, 0)

		posX = self.ppnp.getX()
		posY = self.ppnp.getY()

		self.speed = 0.025
		if (button_down(KB.shift())):
			self.speed = 0.1

		# primitive ground collision checking
		#if (posZ < GROUND_POS):
		#	posZ = GROUND_POS
		#	self.accelZ = 0
		# movement with smooth acceleration
		# hala may math ew
		if (button_down(KB_BUTTON('w'))):
			self.accelY += self.speed * cos(rot_x * (pi/180))
			self.accelX -= self.speed * sin(rot_x * (pi/180))
		if (button_down(KB_BUTTON('s'))):
			self.accelY -= self.speed * cos(rot_x * (pi/180))
			self.accelX += self.speed * sin(rot_x * (pi/180))
		if (button_down(KB_BUTTON('d'))):
			self.accelY += self.speed * sin(rot_x * (pi/180))
			self.accelX += self.speed * cos(rot_x * (pi/180))
		if (button_down(KB_BUTTON('a'))):
			self.accelY -= self.speed * sin(rot_x * (pi/180))
			self.accelX -= self.speed * cos(rot_x * (pi/180))
		# jumping (note, for debugging purposes only)
		if (button_down(KB.space())):
			self.ppnp.setZ(self.ppnp.getZ()+0.1)

		# misc
		if (button_down(KB_BUTTON('m'))):
			gametext.Text.hideText(self.game_text)
		if (button_down(KB_BUTTON('n'))):
			gametext.Text.showText(self.game_text)
		# temp fix for bug
		if (button_down(KB_BUTTON('o')) and self.timer <= 0):
			if (self.scene_rot):
				self.scene.setHpr(0, 0, 0)
			else:
				self.scene.setHpr(0, 90, 0)
			self.scene_rot = not self.scene_rot
			self.timer = 10
		self.timer -= 1
		# deceleration bcoz of gravity
		# self.accelZ -= self.gravity
		# deceleration bcoz of friction
		self.accelY *= 0.8
		self.accelX *= 0.8

		# apply acceleration to position
		posY += self.accelY
		posX += self.accelX

		# the speed is faster when you're going diagonally since we apply the acceleration like a square instead of a circle (?)
		if ((self.accelX * self.accelX) + (self.accelY * self.accelY) > 0.04):
			while ((self.accelX * self.accelX) + (self.accelY * self.accelY) > 0.04): 
				self.accelY *= 0.9
				self.accelX *= 0.9
		# player
				
		# see if the player has fallen off of the world
		if (self.ppnp.getZ() < -5):
			self.ppnp.setZ(10)
		self.ppnp.setX(posX)
		self.ppnp.setY(posY)
		self.camera.setPos(self.ppnp.getPos())
		# the +2.5 is there for emotional support
		self.camera.setZ(self.ppnp.getZ() + 2.5)

		return Task.cont
		

	def mainMenu(self):
		self.scaleFactor = 3
		self.scaleFactorLogo = 0.2
	
		self.cm = CardMaker('video')
		self.video = self.aspect2d.attachNewNode(self.cm.generate())
		self.video.setScale((2))
		self.tex = self.loader.loadTexture('helloworld.avi')
		self.video.setTexture(self.tex)

		
		
		self.music = self.loader.loadSfx("main_menu.mp3")
		self.music.setVolume(0.75)
		self.music.setLoop(True)
		self.music.play()

		self.scaleFactor = 3
		self.scaleFactorLogo = 0.35
		x_offset = -0.95
		
		self.cm = CardMaker('card')
		self.card = self.aspect2d.attachNewNode(self.cm.generate())
		self.logo = self.aspect2d.attachNewNode(self.cm.generate())
		self.card.setScale((16/9)*self.scaleFactor, 1, 1*self.scaleFactor)
		self.logo.setScale((746/168)*self.scaleFactorLogo, 1, 1*self.scaleFactorLogo)

		self.tex = self.loader.loadTexture('background.png')
		self.card.setTexture(self.tex)
		self.tex = self.loader.loadTexture('logo.png')
		self.logo.setTexture(self.tex)

		# these are the centers of the images
		self.background_x = (-16/18)*self.scaleFactor
		self.background_y = -0.5*self.scaleFactor
		self.logo_x = (-746/168/2)*self.scaleFactorLogo
		self.logo_y = -0.5*self.scaleFactorLogo

		self.card.setPos(self.background_x, 0, self.background_y)
		self.logo.setPos(self.logo_x + x_offset + -0.1, 0, self.logo_y + 0.5)
		self.logo.setTransparency(TransparencyAttrib.MAlpha)

		# buttons
		playTexture = (self.loader.loadTexture("buttons/play_normal.png"), self.loader.loadTexture("buttons/play_normal.png"), self.loader.loadTexture("buttons/play_hover.png"), self.loader.loadTexture("buttons/play_normal.png"))
		self.startGameButton = DirectButton(command=self.initGame, frameTexture=playTexture, relief='flat', pressEffect=0, frameSize=(-1, 1, -1,1))
		self.startGameButton.setTransparency(True)
		self.startGameButton.setSx(482/226)

		# unused for the time being
		self.settingsButton = DirectButton(text="Settings")

		exitGameTexture = (self.loader.loadTexture("buttons/exit_normal.png"), self.loader.loadTexture("buttons/exit_normal.png"), self.loader.loadTexture("buttons/exit_hover.png"), self.loader.loadTexture("buttons/exit_normal.png"))
		self.exitGameButton = DirectButton(command=self.exitGame, frameTexture=exitGameTexture, relief='flat', pressEffect=0, frameSize=(-1, 1, -1,1))
		self.exitGameButton.setTransparency(True)
		self.exitGameButton.setSx(482/226)

		
		self.muteTexture = (self.loader.loadTexture("buttons/mute.png"))
		self.unmuteTexture = (self.loader.loadTexture("buttons/unmute.png"))
		self.muteButton = DirectButton(command=self.mute, frameTexture=self.muteTexture, relief='flat', pressEffect=0, frameSize=(-1, 1, -1,1))
		self.muteButton.setTransparency(True)
		self.muteButton.setSx(1)

		# y'know what'd be better
		# positioning the offsets to be relative to the window bounds
		# but noooooooooo i guess we have to do it this way
		# :( 
		self.startGameButton.setPos(x_offset, 0, 0.1)
		self.settingsButton.setPos(x_offset, 0, -0.2)
		self.exitGameButton.setPos(x_offset, 0, -0.3)
		self.muteButton.setPos(1.7, -1.5, -0.8)

		self.menuItems = [self.video, self.startGameButton, self.settingsButton, self.exitGameButton, self.card, self.logo, self.muteButton,]

		self.buttonList = [self.startGameButton, self.settingsButton, self.exitGameButton, self.muteButton]
		self.buttonScale = 0.15

		# laziness will consume
		for button in self.buttonList:
			button.setScale(button.getSx()*self.buttonScale, self.buttonScale, self.buttonScale)

		self.startGameButton.scale = self.startGameButton.getScale()
		# hide non-functional settings button
		self.settingsButton.setScale(0, 0, 0)
		#self.settingsButton.scale = self.settingsButton.getScale()
		self.exitGameButton.scale = self.exitGameButton.getScale()
		self.muteButton.scale = self.muteButton.getScale()

		self.taskMgr.add(self.moveBackground, "mainMenu")
		self.taskMgr.add(self.hoverEffect, "mainMenu")
		
	def moveBackground(self, task):
		sensitivity = 0.05
		self.background_move_x = self.background_x
		self.background_move_y = self.background_y
		if (self.mouseWatcherNode.hasMouse()):
			self.background_move_x += (self.mouseWatcherNode.getMouseX() * sensitivity)
			self.background_move_y += (self.mouseWatcherNode.getMouseY() * sensitivity)
			self.card.setPos(self.background_move_x, 0, self.background_move_y)
		return Task.cont
	
	buttonHoverScale = 1.2
	def hoverEffect(self, task):
		for button in self.buttonList:
			# fix for settings
			if (button == self.settingsButton):
				continue
			if (button.node().getState() == 2):
				button.setScale(self.buttonHoverScale*button.scale[0], self.buttonHoverScale*button.scale[1], self.buttonHoverScale*button.scale[2])
			else:
				button.setScale(button.scale)
		return Task.cont
	
	def mute(self):
		if (self.musicActive):
			self.music.setVolume(0)
			self.muteButton["frameTexture"] = self.unmuteTexture
		else:
			self.music.setVolume(0.75)
			self.muteButton["frameTexture"] = self.muteTexture
		self.musicActive = not self.musicActive
		print(self.musicActive)

	
	def initGame(self):
		for node in self.menuItems:
			node.removeNode()
		self.taskMgr.remove("mainMenu")
		self.characterSelect()

	def characterSelect(self):
		self.cselback = self.aspect2d.attachNewNode(self.cm.generate())
		self.cselback.setScale((16/9)*self.scaleFactor, 1, 1*self.scaleFactor)

		self.tex = self.loader.loadTexture('charselect/background.png')
		self.cselback.setTexture(self.tex)
		self.cselback.setPos(self.background_x, 0, self.background_y)

		self.boyPreview = (self.loader.loadTexture("helloworld.avi"))
		self.girlPreview = (self.loader.loadTexture("charselect/girl.png"))

		self.boySelect = DirectButton(frameTexture=self.boyPreview, relief='flat', pressEffect=0, frameSize=(-1, 1, -1, 1))
		self.girlSelect = DirectButton(frameTexture=self.girlPreview, relief='flat', pressEffect=0, frameSize=(-1, 1, -1, 1))
		self.boySelect.setPos(0.67, 0, 0)
		self.girlSelect.setPos(-0.67, 0, 0)

		self.charButtons = [self.boySelect, self.girlSelect]
		self.charNodes = [self.boySelect, self.girlSelect, self.cselback]

		for char in self.charButtons:
			char.setTransparency(True)
			char.setScale((512/640) * 0.5, 0.5, 0.5)
		# i wish there was like a 'this' from js in python so i could see what the pressed thing is so i dont have to do this stupid stuff
			# ^^^ incomprehendable
		self.girlSelect["command"] = self.setCharacterA
		self.boySelect["command"] = self.setCharacterB
	
	def setCharacterA(self):
		self.character = 1
		self.setCharacter()

	def setCharacterB(self):
		self.character = 2
		self.setCharacter()

	def setCharacter(self):
		print(self.character)
		
		for node in self.charNodes:
			node.removeNode()
		self.loadScene()

	def exitGame(self):
		exit()