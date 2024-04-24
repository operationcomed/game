from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import *
from direct.gui.DirectGui import *
from panda3d.physics import ActorNode, ForceNode, LinearVectorForce, PhysicsCollisionHandler
import gametext
import direct.particles
import movement as mv
import mainMenu as mm
import mainMenuTasks as mmt
import charSelect as chs
import video as vd
import helpmenu as hm
import l0
import l1
# i don't ever plan on using tkinter (for gui purposes) lol
import tkinter as tk

root = tk.Tk()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# function shorthand
KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton
# tentative jumping solution
#GROUND_POS = 2

# antialiasing
loadPrcFileData("", "framebuffer-multisample 1")
loadPrcFileData("", "multisamples 4")

# window
width, height = 1366, 720
loadPrcFileData("", "window-title Escape MSU")
loadPrcFileData("", 'win-size ' + str(width) + ' ' + str(height)) 
loadPrcFileData("", "default-fov 60")
loadPrcFileData("", "show-frame-rate-meter true")

loadPrcFileData("", "shadow-cube-map-filter true")
loadPrcFileData("", """
    text-minfilter linear
    text-magfilter linear
    text-pixels-per-unit 32
""")

class Game(ShowBase):

	# class instances
	game_text = gametext.game_text
	movement_inst = mv.movement
	mainmenu_inst = mm.main_menu
	mainmenutasks_inst = mmt.mm_tasks
	charsel_inst = chs.ch_select
	video_inst = vd.video
	help_inst = hm.hm

	# levels
	l0 = l0.l0
	l1 = l1.l1

	fog_color = (0.1, 0.15, 0.175)
	
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

	health = 100
	healthCap = 100

	sceneScale = (1.5, 1.5, 1.5)

	healthRed = (1, 0.0, 0.4, 1)

	staminaRed = (1, 0.4, 0.2, 1)
	staminaGreen = (0.3, 1, 0.5, 1)
	
	skipTextLabel = "Press E to skip intro."
	volume = 0.75

	isPlaying = False


	sensitivity = 30

	def __init__(self):
		ShowBase.__init__(self)
		props = WindowProperties()
		props.set_icon_filename("icon.ico")
		self.win.request_properties(props)

		self.accept("f11", self.toggleFullscreen)
		self.accept("x", self.exitGame)
		self.accept("shift-x", self.exitGame)

		self.scene_rot = open("assets/ROT_SCENE", "r").read()

		if (self.scene_rot == "True"):
			self.scene_rot = True
		else:
			self.scene_rot = False

		self.font = self.loader.loadFont('assets/fonts/zilla-slab.ttf')

		self.font.setPixelsPerUnit(64)

		# antialiasing
		self.render.setAntialias(AntialiasAttrib.MAuto)
		
		self.render.setShaderAuto()

		# camera
		self.camLens.setNearFar(1, 1000)
		#video before main menu
		self.taskMgr.add(self.splashScreen, "splashScreen")

	def splashScreen(self, task):
		button_down = self.mouseWatcherNode.is_button_down
		if (task.time >= 23 or button_down(KB_BUTTON('e'))):
			self.sound.stop()
			self.video.removeNode()
			self.skipText.setText("")
			self.blackBg.destroy()
			self.isPlaying = False
			self.mainMenu()
			return Task.done
		if (not self.isPlaying):
			vd.Video.playVid(self.video_inst, self, 'assets/media/spash.avi')
		return Task.cont

	fullscreen = False
	def toggleFullscreen(self):
		props = WindowProperties()
		if (self.fullscreen == False):
			props.setFullscreen(True)
			props.setSize(screen_width, screen_height)
		elif (self.fullscreen == True):
			props.setFullscreen(False)
			props.setSize(width, height)
		self.win.request_properties(props)
		self.fullscreen = not self.fullscreen
	
	def helpMenu(self):
		hm.HelpMenu.helpMenu(self.help_inst, self)

	def setBarVisibility(self, visible):
		for bar in self.bars:
			if (visible):
				bar.show()
			else:
				bar.hide()

	settingsShow = False
	def settingsIG(self):
		if (not self.settingsShow):
			self.filters.setBlurSharpen(0.0)
			mm.MainMenu.settingsIG(self.mainmenu_inst, self)

	# scene loading
	def loadScene(self, scene, playerPos, lightPos, doors=False, customTask=False, playerRot=False, collisionMap=False, level=False):
		self.accept("h", self.helpMenu)
		self.stamina = self.staminaCap
		self.music.stop()
		self.music = self.loader.loadSfx("assets/sound/ambient.mp3")
		self.music.setVolume(self.volume)
		self.music.setLoop(True)
		self.music.play()
		self.disable_mouse()

		self.accept("escape", self.settingsIG)
		
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
		self.scene.setShaderOff()
		#self.scene.applyTextureColors()
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
			print("rot")
			self.scene.setHpr(0, 90, 0)
		else:
			print("no rot")

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

		# https://discourse.panda3d.org/t/directgui-directwaitbar/1761/2 (from 2006!)
		barBg = loader.loadTexture("assets/buttons/stm_bkg.png")
		barFg = loader.loadTexture("assets/buttons/stm_fg.png")
		self.staminaBar = DirectWaitBar(frameSize=(0, 2, 0, 0.2), text="", value=self.staminaCap, pos=(-1.2, 0, -0.85), scale=(0.4), range=self.staminaCap, frameColor=(1, 1, 1, 0.8), frameTexture=barBg)
		self.staminaBar["barColor"] = self.staminaGreen

		self.healthBar = DirectWaitBar(frameSize=(0, 2, 0, 0.2), text="", value=100, pos=(-1.2, 0, -0.65), scale=(0.4), range=self.healthCap, frameColor=(1, 1, 1, 0.8), frameTexture=barBg)
		self.healthBar["barColor"] = self.healthRed
		
		self.bars = [self.staminaBar, self.healthBar]

		for bar in self.bars:
			bar.setTransparency(TransparencyAttrib.MAlpha)
			bar.barStyle.setTexture(barFg)
			bar.updateBarStyle()

			ts = TextureStage.getDefault()
			bar.setTexGen(ts, TexGenAttrib.MWorldPosition)
			bar.setTexProjector(ts, self.render2d, bar)
			bar.setTexHpr(ts, 0, -90, 0)
			bar.setTexScale(ts, 1/2, 1, 1/0.2)
			self.sceneObjects.append(bar)


		# lights and shadows
		alight = AmbientLight("alight1")
		alnp = self.render.attachNewNode(alight)
		alight.setColor((.35, .45, .5, 1))
		self.sceneObjects.append(alnp)

		self.slight = PointLight('slight')
		self.slight.setColor((1, 1, 1, 1))
		self.slnp = self.render.attachNewNode(self.slight)
		self.sceneObjects.append(self.slnp)
		self.slnp.node().setShadowCaster(True, 1024, 1024)
		self.slnp.setPos(lightPos)
		self.slnp.setHpr(0, -90, 0)

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

		# fog
		fog = Fog("Fog")
		fog.setColor(LVecBase4f(self.fog_color))
		fog.setExpDensity(0.3)
		self.render.setFog(fog)

		# text
		def attachTextToHUD(text, gtext, pos, scale, font=self.font):
			text.setScale(scale)
			text.setPos(pos)
			gtext.setFont(font)
			self.sceneObjects.append(text)

		self.textNodePath = aspect2d.attachNewNode(self.game_text.ctlText)
		attachTextToHUD(self.textNodePath, self.game_text.ctlText, (-1.2, 0, 0.85), 0.07)
		
		self.stmTxtNode = aspect2d.attachNewNode(self.game_text.stmText)
		attachTextToHUD(self.stmTxtNode, self.game_text.stmText, (-1.2, 0, -0.73), 0.07)

		self.hltTxtNode = aspect2d.attachNewNode(self.game_text.hltText)
		attachTextToHUD(self.hltTxtNode, self.game_text.hltText, (-1.2, 0, -0.53), 0.07)

		self.interactNode = aspect2d.attachNewNode(self.game_text.itcText)
		attachTextToHUD(self.interactNode, self.game_text.itcText, (0, 0, 0), 0.14)

		self.itmTxtNode = aspect2d.attachNewNode(self.game_text.itmText)
		attachTextToHUD(self.itmTxtNode, self.game_text.itmText, (1, 0, 0.85), 0.07)

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
		mv.Movement.movement(self.movement_inst, self)
		return Task.cont

	musicPlaying = False
	def mainMenu(self):
		mm.MainMenu.mainInit(self.mainmenu_inst, self)
		
	def settings(self):
		mm.MainMenu.settings(self.mainmenu_inst, self)

	def moveBackground(self, task):
		return mmt.MainMenuTasks.moveBackground(self.mainmenutasks_inst, self, task)
	
	buttonHoverScale = 1.2
	def hoverEffect(self, task):
		return mmt.MainMenuTasks.hoverEffect(self.mainmenutasks_inst, self, task)

	def initGame(self):
		for node in self.menuItems:
			node.removeNode()
		self.taskMgr.remove("mainMenu")
		chs.CharSelect.characterSelect(self.charsel_inst, self)

	# level 0
	def backstory(self, task):
		return l0.Level0.backstory(self.l0, self, task)
	
	def bedDoor(self, task):
		return l0.Level0.bedDoor(self.l0, self, task)
	
	# level 1
	def missionLevel1(self, task):
		return l1.Level1.mission(self.l1, self, task)

	def exitGame(self):
		exit()