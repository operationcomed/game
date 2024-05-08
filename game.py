from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import *
from panda3d.ai import *
from direct.gui.DirectGui import *
from panda3d.physics import ActorNode, ForceNode, LinearVectorForce, PhysicsCollisionHandler
from direct.interval.LerpInterval import *
import json
import gametext
import direct.particles
import movement as mv
import mainMenu as mm
import mainMenuTasks as mmt
import charSelect as chs
import video as vd
import helpmenu as hm
import bars as bs
import l0
import l1
import l2
import l3
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
width, height = 1280, 720
loadPrcFileData("", "window-title Escape MSU")
loadPrcFileData("", 'win-size ' + str(width) + ' ' + str(height)) 
loadPrcFileData("", "default-fov 60")
loadPrcFileData("", "show-frame-rate-meter true")

loadPrcFileData("", "shadow-cube-map-filter true")
loadPrcFileData("", "icon-filename icon.ico")
loadPrcFileData("", """
	text-minfilter linear
	text-magfilter linear
	text-pixels-per-unit 32
	text-kerning true
	text-use-harfbuzz true
""")

loadPrcFileData("", "texture-minfilter mipmap")
loadPrcFileData("", "texture-maxfilter trilinear")
loadPrcFileData("", "texture-anisotropic-degree 8")
loadPrcFileData("", "threading-model Cull/Draw")

class Game(ShowBase):

	# class instances
	game_text = gametext.game_text
	movement_inst = mv.movement
	mainmenu_inst = mm.main_menu
	mainmenutasks_inst = mmt.mm_tasks
	charsel_inst = chs.ch_select
	video_inst = vd.video
	help_inst = hm.hm
	bars_inst = bs.bs

	# levels
	l0 = l0.l0
	l1 = l1.l1
	l2 = l2.l2
	l3 = l3.l3

	fog_color = (0.1, 0.05, 0)
	
	scene_rot = False

	speedStop = False
	speed1 = 0.025
	barsVisible = False

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

	healthRed = (1, 0.3, 0.15, 1)

	staminaRed = (1, 0.4, 0.2, 1)
	staminaGreen = (0.3, 1, 0.5, 1)
	
	skipTextLabel = "Press E to skip."
	volume = 0.75

	isPlaying = False

	debug = False

	input = False
	mouseLetGo = False

	sensitivity = 30

	# minigame
	anagramRunning = False
	r1Running = False
	r2Running = False
	r3Running = False
	r4Running = False
	r5Running = False
	ptRunning = False
	r1Done = False
	r2Done = False
	r3Done = False
	r4Done = False
	r5Done = False
	ptDone = False
	def resetMinigames(self):
		self.r1Running = False
		self.r2Running = False
		self.r3Running = False
		self.r4Running = False
		self.r5Running = False
		self.ptRunning = False
		self.r1Done = False
		self.r2Done = False
		self.r3Done = False
		self.r4Done = False
		self.r5Done = False
		self.ptDone = False

	mistakes = 0

	barFade = False
	damaging = False

	level = 0

	def __init__(self):
		ShowBase.__init__(self)

		self.accept("f11", self.toggleFullscreen)
		self.accept("x", self.exitGame)
		self.accept("shift-x", self.exitGame)

		# settings loading
		self.scene_rot = open("assets/ROT_SCENE", "r").read()

		if (self.scene_rot == "True"):
			self.scene_rot = True
		else:
			self.scene_rot = False

		settings = json.load(open("assets/SETTINGS", "r"))
		self.volume = settings["volume"]
		self.sensitivity = settings["sensitivity"]
		self.debug = bool(settings["debug"])
		
		#font
		self.font = self.loader.loadFont('assets/fonts/zilla-slab.ttf')

		self.font.setPixelsPerUnit(64)

		# antialiasing
		self.render.setAntialias(AntialiasAttrib.MAuto)
		
		self.render.setShaderAuto()

		# camera
		self.camLens.setNearFar(1, 1000)

		# sound
		self.footsteps = self.loader.loadSfx("assets/sound/footsteps.ogg")

		# fade
		self.fade = OnscreenImage(image='assets/backstories/black.png', scale=(512), sort=999)
		self.fade.setTransparency(True)
		self.fade.setColor(0, 0, 0, 0)

		#video before main menu
		self.taskMgr.add(self.splashScreen, "splashScreen")

	splashDone = False
	timeEnd = 0
	deltaTime = 0
	def splashScreen(self, task):
		button_down = self.mouseWatcherNode.is_button_down
		if ((task.time >= 23 or button_down(KB_BUTTON('e'))) and not self.splashDone):
			self.fade.setColor(0, 0, 0, 1)
			self.sound.stop()
			self.video.removeNode()
			self.skipText.setText("")
			self.blackBg.destroy()
			self.isPlaying = False
			self.splashDone = True
			self.timeEnd = task.time
			self.mainMenu()
		if (not self.isPlaying and not self.splashDone):
			vd.Video.playVid(self.video_inst, self, 'assets/media/spash.avi')
		if (self.splashDone):
			self.deltaTime = task.time - self.timeEnd
			self.fade.setColor(0, 0, 0, max(3-self.deltaTime*2, 0))
			if (max(3-self.deltaTime*2, 0) == 0):
				self.fade.setColor(0, 0, 0, 0)
				return Task.done

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
		if (not self.mouseLetGo):
			hm.HelpMenu.helpMenu(self.help_inst, self)

	def setBarVisibility(self, visible):
		bs.Bars.setBarVisibility(self.bars_inst, self, visible)

	settingsShow = False
	def settingsIG(self):
		if (not self.settingsShow):
			self.filters.setBlurSharpen(0.0)
			mm.MainMenu.settingsIG(self.mainmenu_inst, self)

	# scene loading
	def loadScene(self, scene, playerPos, lightPos, doors=False, customTask=False, playerRot=False, collisionMap=False, level=False, noCache=False, startDark=False):
		if (startDark):
			self.fade.setColor(0, 0, 0, 1)
		self.accept("h", self.helpMenu)
		self.stamina = self.staminaCap

		self.music.stop()
		self.music = self.loader.loadSfx("assets/sound/ambient.mp3")
		self.music.setVolume(self.volume)
		self.music.setLoop(True)
		self.music.play()
		
		self.footsteps.stop()
		self.footsteps.setVolume(0)
		self.footsteps.setLoop(True)
		self.footsteps.play()
		self.disable_mouse()
		
		self.sceneObjects = []
		
		# player + physics
		self.playerCharacter = Actor()
		self.sceneObjects.append(self.playerCharacter)

		self.playerPhysics = ActorNode("player-physics")
		self.ppnp = self.render.attachNewNode(self.playerPhysics)
		if (playerRot != False):
			self.camera.setHpr(playerRot)
		
		self.ppnp.setPos(playerPos)
		self.playerCharacter.loop("walk")

		# https://discourse.panda3d.org/t/directgui-directwaitbar/1761/2 (from 2006!)
		barBg = loader.loadTexture("assets/buttons/stm_bkg.png")
		barFg = loader.loadTexture("assets/buttons/stm_fg.png")
		self.staminaBar = DirectWaitBar(frameSize=(0, 2, 0, 0.2), text="", value=self.staminaCap, pos=(-1.2, 0, -0.85), scale=(0.4), range=self.staminaCap, frameColor=(1, 1, 1, 0.8), frameTexture=barBg)
		self.staminaBar["barColor"] = self.staminaGreen

		self.healthBar = DirectWaitBar(frameSize=(0, 2, 0, 0.2), text="", value=self.healthCap, pos=(-1.2, 0, -0.65), scale=(0.4), range=self.healthCap, frameColor=(1, 1, 1, 0.8), frameTexture=barBg)
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
			bar.setColorScale(1, 1, 1, 0)
			self.sceneObjects.append(bar)
		
		self.setBarVisibility(False)

		self.collisionMap = False
		if (collisionMap != False):
			self.collisionMap = self.loader.loadModel(collisionMap, noCache=noCache, callback=self.finishLoadCollision, extraArgs=[playerRot, playerPos])
		self.scene = self.loader.loadModel(scene, noCache=noCache, callback=self.finishLoadScene, extraArgs=[lightPos, doors, customTask])

		# fog
		self.fog = Fog("Fog")
		self.fog.setColor(LVecBase4f(self.fog_color))
		self.fog.setExpDensity(0.3)
		self.render.setFog(self.fog)

		# text
		self.textObjects = []

		self.textNodePath = aspect2d.attachNewNode(self.game_text.ctlText)
		self.attachTextToHUD(self.textNodePath, self.game_text.ctlText, (-1.2, 0, 0.85), 0.07, self.font)
		
		self.stmTxtNode = aspect2d.attachNewNode(self.game_text.stmText)
		self.attachTextToHUD(self.stmTxtNode, self.game_text.stmText, (-1.2, 0, -0.73), 0.07, self.font)

		self.hltTxtNode = aspect2d.attachNewNode(self.game_text.hltText)
		self.attachTextToHUD(self.hltTxtNode, self.game_text.hltText, (-1.2, 0, -0.53), 0.07, self.font)

		self.interactNode = aspect2d.attachNewNode(self.game_text.itcText)
		self.attachTextToHUD(self.interactNode, self.game_text.itcText, (0, 0, 0), 0.14, self.font)

		self.itmTxtNode = aspect2d.attachNewNode(self.game_text.itmText)
		self.attachTextToHUD(self.itmTxtNode, self.game_text.itmText, (1, 0, 0.85), 0.07, self.font)

		self.accept("escape", self.settingsIG)

		# antialiasing
		self.render.setAntialias(AntialiasAttrib.MAuto)
		
		self.render.setShaderAuto()

		# camera
		self.camLens.setNearFar(0.1, 10000000)

	def finishLoadCollision(self, model, playerRot, playerPos):
		self.collisionMap = model
		self.sceneObjects.append(self.collisionMap)
		self.collisionMap.reparentTo(self.render)
		self.collisionMap.setScale(self.sceneScale)
		self.collisionMap.setShaderOff()
		self.collisionMap.setTextureOff()
		self.collisionMap.hide()
		if (self.scene_rot == True):
			self.collisionMap.setHpr(0, 90, 0)
		self.collisionMap.setCollideMask(BitMask32.bit(0))
		self.enableParticles()

		self.gravity = ForceNode("gravity")
		self.gnp = self.render.attachNewNode(self.gravity)
		self.gravity_amt = LinearVectorForce(0, 0, -10)
		self.gravity.addForce(self.gravity_amt)
		self.physicsMgr.addLinearForce(self.gravity_amt)
		self.physicsMgr.attachPhysicalNode(self.playerPhysics)
		self.colliderNode = self.ppnp.attachNewNode(CollisionNode('colNode'))
		self.colliderNode.node().addSolid(CollisionCapsule(0, 0, 0, 0, 0, 3, 0.5))

		self.playerPhysics.getPhysicsObject().setMass(45)

		self.playerCharacter.reparentTo(self.ppnp)

		# https://arsthaumaturgis.github.io/Panda3DTutorial.io/tutorial/tut_lesson06.html
		self.cTrav = CollisionTraverser()
		self.pusher = PhysicsCollisionHandler()
		self.pusher.addCollider(self.colliderNode, self.ppnp)
		self.cTrav.addCollider(self.colliderNode, self.pusher)

		print("X:", round(self.ppnp.getX(), 3), "Y:", round(self.ppnp.getY(), 3), "Z:", round(self.ppnp.getZ(), 3))

	def finishLoadScene(self, model, lightPos, doors, customTask):
		# scene
		self.scene = model
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

		# lights and shadows
		self.alight = AmbientLight("self.alight1")
		alnp = self.render.attachNewNode(self.alight)
		self.alight.setColor((.35, .45, .5, 1))
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

		if (not self.isPlaying and not (self.input == False or self.mouseLetGo == False)):
			self.setBarVisibility(True)

		self.sunActor = self.loader.loadModel("assets/models/ball.glb")
		self.sceneObjects.append(self.sunActor)

		self.sunActor.reparentTo(self.slnp)
		self.sunActor.setColor(600, 600, 600)

		self.sunActor.setShaderOff()
		# for some reason the scene is rotated 90 degrees on one computer but normal on the other
		if (self.scene_rot == True):
			print("rot")
			self.scene.setHpr(0, 90, 0)
			self.sunActor.reparentTo(self.slnp)
		else:
			print("no rot")
		# tasks
		self.taskMgr.add(self.moveTask, "moveTask")
		if (customTask != False):
			self.taskMgr.add(customTask, "customTask")
		
		# filters 
		self.filters = CommonFilters(self.win, self.cam)
	#	
	#	ralphStartPos = Vec3(-10, 0, 0)
	#	self.seeker = Actor("models/camera")
	#	self.seeker.reparentTo(self.render)
	#	self.seeker.setScale(0.5)
	#	self.seeker.setPos(ralphStartPos)
#
	#	self.filters.setAmbientOcclusion(numsamples=128, amount=2, strength=5)
#
	#	self.AIworld = AIWorld(self.render)
#
	#	self.AIchar = AICharacter("seeker", self.seeker, 100, 0.05, 5)
	#	self.AIworld.addAiChar(self.AIchar)
	#	self.AIbehaviors = self.AIchar.getAiBehaviors()
#
	#	#AI World update
	#	self.taskMgr.add(self.AIUpdate, "AIUpdate")
	#	self.AIbehaviors.pursue(self.ppnp)
	#	self.seeker.loop("run")
#
	##to update the AIWorld
	#def AIUpdate(self, task):
	#	self.AIworld.update()
	#	return Task.cont
	
	def attachTextToHUD(self, text, gtext, pos, scale, font):
		text.setScale(scale)
		text.setPos(pos)
		gtext.setFont(font)
		self.sceneObjects.append(text)
		self.textObjects.append(text)

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

	def hoverEffectCHS(self, task):
		return chs.CharSelect.hoverEffect(self.charsel_inst, self, task)
	
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
	
	# level 2
	def l2Cutscene(self, task):
		return l2.Level2.l2Cutscene(self.l2, self, task)
	
	def missionLevel2(self, task):
		return l2.Level2.mission(self.l2, self, task)

	# level 3
	def l3Cutscene(self, task):
		return l3.Level3.l3Cutscene(self.l3, self, task)
	
	def missionLevel3(self, task):
		return l3.Level3.mission(self.l3, self, task)

	def exitGame(self):
		try:
			self.scene.cancel()
		except:
			pass
		if (self.input == False and self.mouseLetGo == False):
			exit()