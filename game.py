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
import direct.particles

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
loadPrcFileData("", "show-frame-rate-meter true")

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
	
	scene_rot = False

	speedStop = False

	# 0: none
	# 1: girl
	# 2: boy
	character = 0

	cameraOffset = 4.5
	doorRot = False

	stamina = 10
	staminaCap = 10

	sceneScale = (1.5, 1.5, 1.5)
	
	def __init__(self):
		ShowBase.__init__(self)
		self.accept("f11", self.toggleFullscreen)
		self.accept("x", self.exitGame)
		self.accept("shift-x", self.exitGame)

		self.scene_rot = open("assets/ROT_SCENE", "r").read()
		print(self.scene_rot)

		props = WindowProperties()
		props.set_icon_filename("icon.ico")
		self.win.request_properties(props)
		self.font = self.loader.loadFont('assets/fonts/zilla-slab.ttf')

		# antialiasing
		self.render.setAntialias(AntialiasAttrib.MAuto)
		
		self.render.setShaderAuto()

		# camera
		self.camLens.setNearFar(1, 1000)
		#video before main menu
		self.mainMenu()

	fullscreen = False
	def toggleFullscreen(self):
		props = WindowProperties()
		if (self.fullscreen == False):
			props.setFullscreen(True)
		else:
			props.setFullscreen(False)
		self.win.request_properties(props)
		self.fullscreen = not self.fullscreen
	
	def loadScene(self, scene, playerPos, lightPos, doors=False, customTask=False, playerRot=False, collisionMap=False):
		self.accept("h", self.helpMenu)
		self.stamina = self.staminaCap
		self.music.stop()
		self.disable_mouse()
		
		self.sceneObjects = []

		# antialiasing
		self.render.setAntialias(AntialiasAttrib.MAuto)
		
		self.render.setShaderAuto()

		# camera
		self.camLens.setNearFar(0.1, 10000000)

		# scene
		self.scene = self.loader.loadModel(scene)
		self.sceneObjects.append(self.scene)
		self.scene.reparentTo(self.render)
		self.scene.setScale(self.sceneScale)
		#self.scene.setPos(0, 128, 6.8)
		self.scene.setShaderOff()
		self.scene.setTwoSided(False)


		if (doors != False):
			self.doorRot = True
			self.doors = self.loader.loadModel(doors)
			self.sceneObjects.append(self.doors)
			self.doors.reparentTo(self.render)
			self.doors.setScale(self.sceneScale)
			self.doors.setShaderOff()

			# booleans are a mystery to humankind
			if (self.scene_rot == True):
				self.doors.setHpr(0, 90, 0)

		# for some reason the scene is rotated 90 degrees on one computer but normal on the other
		if (self.scene_rot == True):
			self.scene.setHpr(0, 90, 0)

		if (collisionMap == False):
			self.scene.setCollideMask(BitMask32.bit(0))
		else:
			self.collisionMap = self.loader.loadModel(collisionMap)
			self.sceneObjects.append(self.collisionMap)
			self.collisionMap.reparentTo(self.render)
			self.collisionMap.setScale(self.sceneScale)
			self.collisionMap.setShaderOff()
			self.collisionMap.hide()
			self.collisionMap.setCollideMask(BitMask32.bit(0))
		self.enableParticles()

		self.staminaBar = DirectWaitBar(text="", value=100, pos=(-0.89, 0, -0.85), scale=(0.3), range=self.staminaCap)
		self.staminaBar["barColor"] = (0.1, 1, 0.2, 1)
		self.sceneObjects.append(self.staminaBar)

		# lights and shadows
		alight = AmbientLight("alight1")
		alnp = self.render.attachNewNode(alight)
		alight.setColor((.35, .45, .5, 1))
		self.sceneObjects.append(alnp)

		self.slight = PointLight('slight')
		self.slight.setColor((1, 1, 1, 1))
		#self.lens = PerspectiveLens()
		#self.slight.setLens(self.lens)
		#self.slight.attenuation = (0, 0, 1)
		self.slnp = self.render.attachNewNode(self.slight)
		self.sceneObjects.append(self.slnp)
		self.slnp.node().setShadowCaster(True, 1024, 1024)
		self.slnp.setPos(lightPos)
		self.slnp.setHpr(0, -90, 0)
		#self.lens.setNearFar(1, 1000000)

		self.render.setLight(self.slnp)
		self.render.setLight(alnp)
		self.setBackgroundColor(self.fog_color)

		self.sunActor = Actor("assets/models/ball.glb")
		self.sceneObjects.append(self.sunActor)

		self.sunActor.reparentTo(self.slnp)
		self.sunActor.setColor(600, 600, 600)

		# remove the shader for the sun because the sun shouldnt have a shadow
		self.sunActor.setShaderOff()

		# player + physics
		self.playerCharacter = Actor()
		self.sceneObjects.append(self.playerCharacter)

		self.playerPhysics = ActorNode("player-physics")
		self.ppnp = self.render.attachNewNode(self.playerPhysics)
		if (playerRot != False):
			self.camera.setHpr(playerRot)
		self.physicsMgr.attachPhysicalNode(self.playerPhysics)
		self.colliderNode = self.ppnp.attachNewNode(CollisionNode('colNode'))
		self.colliderNode.node().addSolid(CollisionTube(0, 0, 0, 0, 0, 3, 0.5))

		self.gravity = ForceNode("gravity")
		self.gnp = self.render.attachNewNode(self.gravity)
		self.gravity_amt = LinearVectorForce(0, 0, -10)
		self.gravity.addForce(self.gravity_amt)
		self.physicsMgr.addLinearForce(self.gravity_amt)
		self.playerPhysics.getPhysicsObject().setMass(45)

		self.playerCharacter.reparentTo(self.ppnp)
		
		self.ppnp.setPos(playerPos)
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
		if (customTask != False):
			self.taskMgr.add(customTask, "customTask")
		
		# filters 
		self.filters = CommonFilters(self.win, self.cam)
		self.filters.setAmbientOcclusion(numsamples=128, amount=2, strength=5)
		#filters.setBloom(intensity=0.1)

		# fog
		fog = Fog("Fog")
		fog.setColor(LVecBase4f(self.fog_color))
		fog.setExpDensity(0.2)
		self.render.setFog(fog)

		# text
		
		self.textNodePath = aspect2d.attachNewNode(self.game_text.ctlText)
		self.textNodePath.setScale(0.07)
		self.textNodePath.setPos(-1.2, 0, 0.85)
		self.game_text.ctlText.setFont(self.font)
		self.sceneObjects.append(self.textNodePath)
		
		self.stmTxtNode = aspect2d.attachNewNode(self.game_text.stmText)
		self.stmTxtNode.setScale(0.07)
		self.stmTxtNode.setPos(-1.2, 0, -0.78)
		self.game_text.stmText.setFont(self.font)
		self.sceneObjects.append(self.stmTxtNode)

		self.interactNode = aspect2d.attachNewNode(self.game_text.itcText)
		self.interactNode.setScale(0.14)
		self.interactNode.setPos(0, 0, 0)
		self.sceneObjects.append(self.interactNode)
		self.game_text.itcText.setFont(self.font)

		self.itmTxtNode = aspect2d.attachNewNode(self.game_text.itmText)
		self.itmTxtNode.setScale(0.07)
		self.itmTxtNode.setPos(1, 0, 0.85)
		self.sceneObjects.append(self.itmTxtNode)
		self.game_text.itmText.setFont(self.font)
		print("X:", round(self.ppnp.getX(), 3), "Y:", round(self.ppnp.getY(), 3), "Z:", round(self.ppnp.getZ(), 3))


	def unloadScene(self):
		self.accelX = 0
		self.accelY = 0
		self.accelZ = 0
		self.taskMgr.remove("moveTask")
		self.taskMgr.remove("customTask")
		self.ignore("h")
		self.filters.cleanup()
		self.game_text.itcText.setTextColor(1, 1, 1, 1)
		for node in self.sceneObjects:
			try:
				node.cleanup()
				print("cleaned up")
			except:
				print("can't cleanup")
			node.remove_node()

	timer = 0
	sprintable = False
	barColored = 0
	# "basic" player movement
	def moveTask(self, task):
		button_down = self.mouseWatcherNode.is_button_down

		# print current position for debugging
		if (button_down(KB_BUTTON('p'))):
			print("X:", round(self.ppnp.getX(), 3), "Y:", round(self.ppnp.getY(), 3), "Z:", round(self.ppnp.getZ(), 3))
		if (button_down(KB_BUTTON('l'))):
			print("H:", round(self.camera.getH(), 3), "P:", round(self.camera.getP(), 3), "R:", round(self.camera.getR(), 3))

		has_mouse = self.mouseWatcherNode.hasMouse()
		rot_x = self.camera.getH()
		rot_y = self.camera.getP()
		rot_z = self.camera.getR()

		sensitivity = 30
		
		props = WindowProperties()
		if (button_down(KB.escape())):
			props.setCursorHidden(False)
			self.win.requestProperties(props)
			props = self.win.getProperties()
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
			if (not self.speedStop):
				if (rot_y+mouse_y > 90):
					self.camera.setHpr(rot_x-mouse_x, 90, 0)
				elif (rot_y+mouse_y < -90):
					self.camera.setHpr(rot_x-mouse_x, -90, 0)
				else:
					self.camera.setHpr(rot_x-mouse_x, rot_y+mouse_y, 0)

		posX = self.ppnp.getX()
		posY = self.ppnp.getY()

		self.speed = 0.025

		# sprinting and stamina
		if (button_down(KB.shift()) and self.stamina >= 0 and self.sprintable):
			self.speed = 0.1
			if (button_down(KB_BUTTON('w')) or button_down(KB_BUTTON('a')) or button_down(KB_BUTTON('s')) or button_down(KB_BUTTON('d'))):
				self.stamina -= 0.05
		if (self.stamina <= 0.01):
			self.sprintable = False

		if (self.stamina < 0):
			self.stamina = 0

		if (self.speedStop):
			self.speed = 0

		if (self.sprintable == False and not self.barColored == 1):
			self.staminaBar["barColor"] = (1, 0.4, 0.2, 1)
			self.barColored = 1
		elif (self.sprintable == True and not self.barColored == 2):
			self.staminaBar["barColor"] = (0.1, 1, 0.2, 1)
			self.barColored = 2
		# primitive ground collision checking
		#if (posZ < GROUND_POS):
		#	posZ = GROUND_POS
		#	self.accelZ = 0
		# movement with smooth acceleration
		# hala may math ew
		staminaGain = True
		if (button_down(KB_BUTTON('w'))):
			self.accelY += self.speed * cos(rot_x * (pi/180))
			self.accelX -= self.speed * sin(rot_x * (pi/180))
			staminaGain = False
		if (button_down(KB_BUTTON('s'))):
			self.accelY -= self.speed * cos(rot_x * (pi/180))
			self.accelX += self.speed * sin(rot_x * (pi/180))
			staminaGain = False
		if (button_down(KB_BUTTON('d'))):
			self.accelY += self.speed * sin(rot_x * (pi/180))
			self.accelX += self.speed * cos(rot_x * (pi/180))
			staminaGain = False
		if (button_down(KB_BUTTON('a'))):
			self.accelY -= self.speed * sin(rot_x * (pi/180))
			self.accelX -= self.speed * cos(rot_x * (pi/180))
			staminaGain = False

		if (self.staminaCap > self.stamina and staminaGain):
			self.stamina += 0.025
		elif (self.stamina >= self.staminaCap):
			self.stamina = self.staminaCap
			self.sprintable = True
		# jumping (note, for debugging purposes only)
		if (button_down(KB.space()) and not self.speedStop):
			self.ppnp.setZ(self.ppnp.getZ()+0.1)

		# misc
		#if (button_down(KB_BUTTON('m'))):
		#	gametext.Text.hideText(self.game_text)
		#	self.unloadScene()
		#if (button_down(KB_BUTTON('n'))):
		#	gametext.Text.showText(self.game_text)
		# fix for bug
		if (button_down(KB_BUTTON('o')) and self.timer <= 0):
			if (self.scene_rot):
				self.scene.setHpr(0, 0, 0)
				if (self.doorRot):
					self.doors.setHpr(0, 0, 0)
			else:
				self.scene.setHpr(0, 90, 0)
				if (self.doorRot):
					self.doors.setHpr(0, 90, 0)
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
		if ((self.accelX * self.accelX) + (self.accelY * self.accelY) > 0.01):
			while ((self.accelX * self.accelX) + (self.accelY * self.accelY) > 0.01): 
				self.accelY *= 0.9
				self.accelX *= 0.9
				
				
		# see if the player has fallen off of the world
		if (self.ppnp.getZ() < -5):
			self.ppnp.setZ(10)
		self.ppnp.setX(posX)
		self.ppnp.setY(posY)
		self.camera.setPos(self.ppnp.getPos())
		self.camera.setZ(self.ppnp.getZ() + self.cameraOffset)

		self.staminaBar["value"] = self.stamina

		return Task.cont
		
	helpDisplay = False
	def helpMenu(self):
		self.helpDisplay = not self.helpDisplay
		if (self.helpDisplay):
			self.helpMenuImg = OnscreenImage(image='assets/media/helpMenu.png', scale=(16/9, 1, 1))
			self.helpMenuImg.setTransparency(TransparencyAttrib.MAlpha)
			self.textNodePath.hide()
		else:
			self.helpMenuImg.destroy()
			self.textNodePath.show()


	def mainMenu(self):
		self.sensitivity = 0.025
		self.scaleFactor = 3
		self.scaleFactorLogo = 0.2
	
		self.cm = CardMaker('video')
		self.video = self.aspect2d.attachNewNode(self.cm.generate())
		self.video.setScale((2))
		self.tex = self.loader.loadTexture('assets/media/helloworld.avi')
		self.video.setTexture(self.tex)
		
		self.music = self.loader.loadSfx("assets/sound/main_menu.mp3")
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

		self.tex = self.loader.loadTexture('assets/media/bkgnew.png')
		self.card.setTexture(self.tex)
		self.tex = self.loader.loadTexture('assets/media/logo.png')
		self.logo.setTexture(self.tex)

		# these are the centers of the images
		self.background_x = (-16/18)*self.scaleFactor
		self.background_y = -0.5*self.scaleFactor
		self.logo_x = (-746/168/2)*self.scaleFactorLogo
		self.logo_y = -0.5*self.scaleFactorLogo

		self.card.setPos(self.background_x, 0, self.background_y)
		self.logo.setPos(self.logo_x + x_offset, 0, self.logo_y + 0.5)
		self.logo.setTransparency(TransparencyAttrib.MAlpha)

		# buttons
		playTexture = (self.loader.loadTexture("assets/buttons/play_normal.png"), self.loader.loadTexture("assets/buttons/play_normal.png"), self.loader.loadTexture("assets/buttons/play_hover.png"), self.loader.loadTexture("assets/buttons/play_normal.png"))
		self.startGameButton = DirectButton(command=self.initGame, frameTexture=playTexture, relief='flat', pressEffect=0, frameSize=(-1, 1, -1,1))
		self.startGameButton.setTransparency(True)
		self.startGameButton.setSx(482/226)

		# unused for the time being
		self.settingsButton = DirectButton(text="Settings")

		exitGameTexture = (self.loader.loadTexture("assets/buttons/exit_normal.png"), self.loader.loadTexture("assets/buttons/exit_normal.png"), self.loader.loadTexture("assets/buttons/exit_hover.png"), self.loader.loadTexture("assets/buttons/exit_normal.png"))
		self.exitGameButton = DirectButton(command=self.exitGame, frameTexture=exitGameTexture, relief='flat', pressEffect=0, frameSize=(-1, 1, -1,1))
		self.exitGameButton.setTransparency(True)
		self.exitGameButton.setSx(482/226)

		
		self.muteTexture = (self.loader.loadTexture("assets/buttons/mute.png"))
		self.unmuteTexture = (self.loader.loadTexture("assets/buttons/unmute.png"))
		self.muteButton = DirectButton(command=self.mute, frameTexture=self.muteTexture, relief='flat', pressEffect=0, frameSize=(-1, 1, -1,1))
		self.muteButton.setTransparency(True)
		self.muteButton.setSx(1)

		# y'know what'd be better
		# positioning the offsets to be relative to the window bounds
		# but noooooooooo i guess we have to do it this way
		# :( 
		self.startGameButton.setPos(x_offset, 0, 0)
		self.settingsButton.setPos(x_offset, 0, -0.2)
		self.exitGameButton.setPos(x_offset, 0, -0.4)
		self.muteButton.setPos(1.575, -1.5, -0.8)

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
		self.background_move_x = self.background_x
		self.background_move_y = self.background_y
		if (self.mouseWatcherNode.hasMouse()):
			self.background_move_x += (-self.mouseWatcherNode.getMouseX() * self.sensitivity)
			self.background_move_y += (-self.mouseWatcherNode.getMouseY() * self.sensitivity)
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
		self.sensitivity = 0.005
		self.scaleFactorCS = 2.25
		self.background_x = (-16/18)*self.scaleFactorCS
		self.background_y = -0.5*self.scaleFactorCS
		self.card = self.aspect2d.attachNewNode(self.cm.generate())
		self.card.setScale((16/9)*self.scaleFactorCS, 1, 1*self.scaleFactorCS)

		self.tex = self.loader.loadTexture('assets/charselect/background.png')
		self.card.setTexture(self.tex)
		self.card.setPos(self.background_x, 0, self.background_y)

		self.boyPreview = (self.loader.loadTexture("assets/charselect/boy.png"))
		self.girlPreview = (self.loader.loadTexture("assets/charselect/girl.png"))

		self.boySelect = DirectButton(frameTexture=self.boyPreview, relief='flat', pressEffect=0, frameSize=(-1, 1, -1, 1))
		self.girlSelect = DirectButton(frameTexture=self.girlPreview, relief='flat', pressEffect=0, frameSize=(-1, 1, -1, 1))
		charDistance = 1.05
		self.boySelect.setPos(charDistance, 0, -0.25)
		self.girlSelect.setPos(-charDistance, 0, -0.25)

		self.charButtons = [self.boySelect, self.girlSelect]
		self.charNodes = [self.boySelect, self.girlSelect, self.card]

		self.taskMgr.add(self.moveBackground, "moveBackground")

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
		
		self.taskMgr.remove("moveBackground")
		for node in self.charNodes:
			node.removeNode()

		# bed scene
		self.cameraOffset = 4
		self.loadScene("assets/models/bed.glb", (3.5, 6, 1.42), (0, 0, 10), doors=False, customTask=self.bedDoor, playerRot=(180, -90, 0))
		self.helpMenu()
		self.taskMgr.add(self.backstory, "backstory")

	isPlaying = False
	def backstory(self, task):
		self.staminaBar.hide()
		if (not self.isPlaying):
			self.playVid()

		button_down = self.mouseWatcherNode.is_button_down

		if (task.time >= 47 or button_down(KB_BUTTON('e'))):
			self.video.removeNode()
			gametext.Text.showCH(self.game_text)
			self.speedStop = False
			self.skipText.setText("")
			self.blackBg.destroy()
			self.sound.stop()
			self.staminaBar.show()
			return Task.done
		return Task.cont

	def playVid(self):
		self.isPlaying = True
		gametext.Text.hideCH(self.game_text)
		self.speedStop = True
		# this bg is here to prevent 3d game from being shown
		self.blackBg = OnscreenImage(image='assets/backstories/black.png', scale=(1000, 1, 1000))
		self.cm = CardMaker('card')
		self.cm.setFrameFullscreenQuad()
		self.scaleFactorVid = 1.9
		self.video = self.aspect2d.attachNewNode(self.cm.generate())
		self.video.setScale(self.scaleFactorVid, 1, self.scaleFactorVid)

		self.tex = MovieTexture("backstory")
		if (self.character == 1):
			self.tex.read('assets/backstories/Girl.avi')
			self.sound = self.loader.loadSfx('assets/backstories/Girl.avi')
			self.sound.play()
		else:
			self.tex.read('assets/backstories/Boy.avi')
			self.sound = self.loader.loadSfx('assets/backstories/Boy.avi')
			self.sound.play()
		self.cm.setUvRange(self.tex)
		self.video.setTexture(self.tex)

		self.background_x = 0.115
		self.background_y = 0.899

		self.video.setPos(self.background_x, 0, self.background_y)
		self.skipText = TextNode('items')
		self.skipText.setText("Press E to skip intro.")
		self.skipText.setShadow(0.15, 0.15)
		self.skipText.setFont(self.font)
		self.stnp = aspect2d.attachNewNode(self.skipText)
		self.stnp.setPos(-1.2, 0, 0.85)
		self.stnp.setScale(0.07)

	def bedDoor(self, task):
		rot = self.camera.getH()
		crosshair = self.game_text.itcText
		#chnp = aspect2d.attachNewNode(self.game_text.itcText)
		while rot > 360:
			rot -= 360
		while rot < 0:
			rot += 360
		# X: 1.5 -> -2.5
		# Y: < -4
		posX = self.camera.getX()
		posY = self.camera.getY()
		#print(posX, posY)
		doorInteract = False
		if ((posX >= -2.5 and posX <= 1.5) and posY <= -4):
			crosshair.setTextColor(1, 0.5, 0, 1)
			doorInteract = True
		else:
			crosshair.setTextColor(1, 1, 1, 1)
			doorInteract = False
			
		button_down = self.mouseWatcherNode.is_button_down
		if (button_down(KB_BUTTON('e')) and doorInteract):
			self.unloadScene()
			self.cameraOffset = 4
			self.loadScene("assets/models/inf.glb", (-17.0, 6.25, 5.414), (0, 0, 10.5), "assets/models/door.glb", self.mission)
		return Task.cont
	
	missionShow = False
	initItemsDone = False
	missionDone = False
	itemsGotten = 0
	def mission(self, task):
		crosshair = self.game_text.itcText
		button_down = self.mouseWatcherNode.is_button_down
		if (not self.missionShow):
			self.missionShow = True
			self.speedStop = True
			self.showMission()
		
		if (button_down(KB_BUTTON('e')) and self.missionShow and self.speedStop == True and task.time >= 0.1):
			self.speedStop = False
			self.missionImg.removeNode()
			gametext.Text.showText(self.game_text)
		
		if (not self.initItemsDone):
			self.initItems()
		else:
			posX = self.ppnp.getX()
			posY = self.ppnp.getY()
			#posZ = self.ppnp.getZ() # no z axis atm because it'll be a hassle
			i = 0
			for itemPos in self.itemList:
				if (abs(itemPos[1][0] - posX) <= 2 and abs(itemPos[1][1] - posY) <= 2 and itemPos[2] != None):
					pickup = self.loader.loadSfx('assets/sound/pickup.wav')
					pickup.setLoop(False)
					pickup.play()
					self.items[i].removeNode()
					self.itemsGotten += 1
					self.game_text.itmText.setText(self.game_text.itmText.getText() + "\n" + itemPos[2])
					itemPos[2] = None
				i += 1

		posX = self.camera.getX()
		posY = self.camera.getY()
		if (self.itemsGotten >= 5 and not self.missionDone):
			doneSound = self.loader.loadSfx('assets/sound/done.mp3')
			doneSound.setLoop(False)
			doneSound.play()
			self.missionDone = True
			self.game_text.itmText.setTextColor(0, 1, 0.5, 1)
			self.game_text.itmText.setText(self.game_text.itmText.getText() + "\n" + "You can escape through the door now!")
		if ((posX >= 11 and posX <= 17) and posY <= -20 and self.itemsGotten >= 5):
			crosshair.setTextColor(1, 0.5, 0, 1)
			doorInteract = True
		else: 
			crosshair.setTextColor(1, 1, 1, 1)
			doorInteract = False

		if (button_down(KB_BUTTON('e')) and doorInteract):
			self.unloadScene()
			self.game_text.ctlText.setText("")
			self.interactNode = aspect2d.attachNewNode(self.game_text.itcText)
			self.interactNode.setScale(0.14)
			self.interactNode.setPos(-0.5, 0, 0)
			self.sceneObjects.append(self.interactNode)
			self.game_text.itcText.setText("Level 1 Complete!")

		return Task.cont
	
	def initItems(self):
		self.initItemsDone = True
		self.scaleFactorItem = 4
		# filename, position, human readable name
		self.itemList = [['1_mask', (4.4, 17.5, 0), 'Mask'], ['2_cert', (-7.25, -18.25, 0), 'Medical Certificate'], ['3_excuse', (-9.5, 12.65, 0), 'Excuse Letter'], ['4_meds', (20, -20, 0), 'Medicine'], ['5_prescription', (-15, -7.8, 0), 'Doctor\'s Prescription']]
		self.items = []
		self.cm = CardMaker('card')
		for itemPath in self.itemList:
			item = self.render.attachNewNode(self.cm.generate())
			item.setScale(self.scaleFactorItem, 1, self.scaleFactorItem)

			tex = self.loader.loadTexture('assets/items/' + itemPath[0] + '.png')
			item.setTexture(tex)

			item.setPos(itemPath[1])
			item.setTransparency(TransparencyAttrib.MAlpha)

			item.setBillboardAxis()

			self.items.append(item)


	def showMission(self):
		gametext.Text.hideText(self.game_text)
		self.scaleFactorMission = 7/4
		self.cm = CardMaker('card')
		self.missionImg = self.aspect2d.attachNewNode(self.cm.generate())
		self.missionImg.setScale((16/9)*self.scaleFactorMission, 1, self.scaleFactorMission)

		self.tex = self.loader.loadTexture('assets/missions/1.png')
		self.missionImg.setTexture(self.tex)

		# these are the centers of the image
		self.mission_x = (-16/9/2)*self.scaleFactorMission
		self.mission_y = -0.5*self.scaleFactorMission

		self.missionImg.setPos(self.mission_x, 0, self.mission_y)
		self.missionImg.setTransparency(TransparencyAttrib.MAlpha)

	def exitGame(self):
		exit()