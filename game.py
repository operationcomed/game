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
import time
import gametext

# function shorthand
KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton
# tentative jumping solution
GROUND_POS = 3

# antialiasing
loadPrcFileData("", "framebuffer-multisample 1")
loadPrcFileData("", "multisamples 4")

# window
loadPrcFileData("", "window-title Escape MSU")
loadPrcFileData('', 'win-size 1024 720') 
loadPrcFileData("", "default-fov 60")

class Game(ShowBase):

	accelZ = 0
	#accelZCap = 1

	accelX = 0
	#accelXCap = 0.4
	accelY = 0
	#accelYCap = 0.4
	game_text = gametext.game_text
	
	
	def __init__(self):
		ShowBase.__init__(self)
		# antialiasing
		self.render.setAntialias(AntialiasAttrib.MAuto)
		
		self.render.setShaderAuto()

		# camera
		self.camLens.setNearFar(1, 1000)

		#self.taskMgr.add(self.startTask, "startTask")
		self.mainMenu()
	
	def loadScene(self):
		self.music.stop()
		self.disable_mouse()

		# antialiasing
		self.render.setAntialias(AntialiasAttrib.MAuto)
		
		self.render.setShaderAuto()

		# camera
		self.camLens.setNearFar(1, 10000)

		# lights and shadows
		alight = AmbientLight("alight1")
		alnp = self.render.attachNewNode(alight)
		alight.setColor((.35, .45, .5, 1))

		self.slight = Spotlight('slight')
		self.slight.setColor((125, 110, 100, 1))
		self.lens = PerspectiveLens()
		self.slight.setLens(self.lens)
		self.slnp = self.render.attachNewNode(self.slight)
		self.slnp.node().setShadowCaster(True, 2048, 2048)
		self.slnp.setPos(0, -15, 15)
		self.slnp.setHpr(0, -10, 0)
		self.lens.setNearFar(1, 1000000)

		self.render.setLight(self.slnp)
		self.render.setLight(alnp)

		# tentative scene
		self.scene = self.loader.loadModel("msu_tri.glb")

		self.scene.reparentTo(self.render)

		self.scene.setScale(0.4, 0.4, 0.4)
		self.scene.setPos(0, 128, 6.1)
		self.scene.setHpr(0, 90, 0)

		self.setBackgroundColor(144/255, 195/255, 249/255)

		# tentative pandas
		self.pandaActor = Actor("models/panda-model", {"walk": "models/panda-walk4"})

		self.pandaActor.setScale(0.005, 0.005, 0.005)
		self.pandaActor.reparentTo(self.render)
		self.pandaActor.setPos(0, 10, 0)
		self.pandaActor.loop("walk")

		self.sunActor = Actor("models/smiley")

		self.sunActor.reparentTo(self.slnp)
		self.sunActor.setColor(600, 450, 1)

		# remove the shader for the sun because the sun shouldnt have a shadow
		self.sunActor.setShaderOff()

		# this panda is u ;) baby panda
		self.pandaActor2 = Actor()

		self.pandaActor2.setScale(0.0025, 0.0025, 0.0025)
		self.pandaActor2.reparentTo(self.render)
		self.pandaActor2.setHpr(180, 0, 0)
		self.pandaActor2.loop("walk")

		# tasks
		self.taskMgr.add(self.moveTask, "moveTask")
		#self.taskMgr.add(self.coordinateTask, "coordinateTask")
		
		# filters 
		filters = CommonFilters(self.win, self.cam)
		filters.setAmbientOcclusion()
		filters.setBloom(intensity=0.1)

		# fog
		#fog = Fog("Fog Name")
		#fog.setColor(0.1, 0.15, 0.175)
		#fog.setExpDensity(0.001)
		#self.render.setFog(fog)

		# text
		
		self.textNodePath = aspect2d.attachNewNode(self.game_text.ctlText)
		self.textNodePath.setScale(0.07)
		self.textNodePath.setPos(-1.2, 0, 0.9)

		self.textNodePath = aspect2d.attachNewNode(self.game_text.escText)
		self.textNodePath.setScale(0.07)
		self.textNodePath.setPos(-1.2, 0, -0.85)

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

		posX = self.camera.getX()
		posY = self.camera.getY()
		posZ = self.camera.getZ()
		self.speed = 0.05

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
		# jumping
		if (button_down(KB.space()) and posZ < GROUND_POS + 0.1):
			self.accelZ += 0.25
		# misc
		if (button_down(KB_BUTTON('m'))):
			gametext.Text.hideText(self.game_text)
		if (button_down(KB_BUTTON('n'))):
			gametext.Text.showText(self.game_text)

		# deceleration bcoz of gravity
		self.accelZ -= 0.01
		# deceleration bcoz of friction
		self.accelY *= 0.8
		self.accelX *= 0.8

		# apply acceleration to position
		posZ += self.accelZ
		posY += self.accelY
		posX += self.accelX

		# the speed is faster when you're going diagonally since we apply the acceleration like a square instead of a circle (?)
		if ((self.accelX * self.accelX) + (self.accelY * self.accelY) > 0.04):
			while ((self.accelX * self.accelX) + (self.accelY * self.accelY) > 0.04): 
				self.accelY *= 0.9
				self.accelX *= 0.9

		# primitive ground collision checking
		if (posZ < GROUND_POS):
			posZ = GROUND_POS
			self.accelZ = 0

		self.camera.setPos(posX, posY, posZ)
		# panda
		self.pandaActor2.setPos(posX - 2 * sin(rot_x * (pi/180)), posY + 2 * cos(rot_x * (pi/180)), posZ-3)
		self.pandaActor2.setHpr(rot_x+180, 0, 0)

		return Task.cont

	def mainMenu(self):
		self.music = self.loader.loadSfx("main_menu.mp3")
		self.music.setLoop(True)
		self.music.play()

		self.scaleFactor = 2.5
		self.scaleFactorLogo = 0.35
		x_offset = -0.6
		
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
		self.logo.setPos(self.logo_x + x_offset, 0, self.logo_y + 0.5)
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

		self.startGameButton.setPos(x_offset, 0, 0.1)
		self.settingsButton.setPos(x_offset, 0, -0.2)
		self.exitGameButton.setPos(x_offset, 0, -0.3) # -0.5 with settings button

		self.menuItems = [self.startGameButton, self.settingsButton, self.exitGameButton, self.card, self.logo]

		self.buttonList = [self.startGameButton, self.settingsButton, self.exitGameButton]
		self.buttonScale = 0.15

		# laziness will consume
		for button in self.buttonList:
			button.setScale(button.getSx()*self.buttonScale, self.buttonScale, self.buttonScale)

		self.startGameButton.scale = self.startGameButton.getScale()
		# hide non-functional settings button
		self.settingsButton.setScale(0, 0, 0)
		#self.settingsButton.scale = self.settingsButton.getScale()
		self.exitGameButton.scale = self.exitGameButton.getScale()

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
	
	def initGame(self):
		for node in self.menuItems:
			node.removeNode()
		self.taskMgr.remove("mainMenu")
		self.loadScene()

	def exitGame(self):
		exit()