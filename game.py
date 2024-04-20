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
import movement as mv
import mainMenu as mm
import mainMenuTasks as mmt
import charSelect as chs
import video as vd
import l0
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

	accelZ = 0
	#accelZCap = 1

	accelX = 0
	#accelXCap = 0.4
	accelY = 0
	#accelYCap = 0.4

	# class instances
	game_text = gametext.game_text
	movement_inst = mv.movement
	mainmenu_inst = mm.main_menu
	mainmenutasks_inst = mmt.mm_tasks
	charsel_inst = chs.ch_select
	video_inst = vd.video

	# levels
	l0 = l0.l0

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

	staminaRed = (1, 0.4, 0.2, 1)
	staminaGreen = (0.3, 1, 0.5, 1)
	
	skipTextLabel = "Press E to skip intro."
	volume = 0.75

	def __init__(self):
		ShowBase.__init__(self)
		self.accept("f11", self.toggleFullscreen)
		self.accept("x", self.exitGame)
		self.accept("shift-x", self.exitGame)

		self.scene_rot = open("assets/ROT_SCENE", "r").read()

		if (self.scene_rot == "True"):
			self.scene_rot = True
		else:
			self.scene_rot = False

		props = WindowProperties()
		props.set_icon_filename("icon.ico")
		self.win.request_properties(props)
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
			self.skipText.setText("")
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
	
	# scene loading
	def loadScene(self, scene, playerPos, lightPos, doors=False, customTask=False, playerRot=False, collisionMap=False):
		self.accept("h", self.helpMenu)
		self.stamina = self.staminaCap
		self.music.stop()
		self.music = self.loader.loadSfx("assets/sound/ambient.mp3")
		self.music.setVolume(self.volume)
		self.music.setLoop(True)
		self.music.play()
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
		staminaBg = loader.loadTexture("assets/buttons/stm_bkg.png")
		staminaFg = loader.loadTexture("assets/buttons/stm_fg.png")
		self.staminaBar = DirectWaitBar(frameSize=(0, 2, 0, 0.2), text="", value=100, pos=(-1.2, 0, -0.85), scale=(0.4), range=self.staminaCap, frameColor=(1, 1, 1, 0.8), frameTexture=staminaBg)
		
		self.staminaBar.setTransparency(TransparencyAttrib.MAlpha)
		self.staminaBar["barColor"] = self.staminaGreen
		self.staminaBar.barStyle.setTexture(staminaFg)
		self.staminaBar.updateBarStyle()

		ts = TextureStage.getDefault()
		self.staminaBar.setTexGen(ts, TexGenAttrib.MWorldPosition)
		self.staminaBar.setTexProjector(ts, self.render2d, self.staminaBar)
		self.staminaBar.setTexHpr(ts, 0, -90, 0)
		self.staminaBar.setTexScale(ts, 1/2, 1, 1/0.2)

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
		self.stmTxtNode.setPos(-1.2, 0, -0.73)
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
		mv.Movement.movement(self.movement_inst, self)
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
	isPlaying = False
	def backstory(self, task):
		return l0.Level0.backstory(self.l0, self, task)
	
	def bedDoor(self, task):
		return l0.Level0.bedDoor(self.l0, self, task)

	
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
			self.staminaBar.hide()
		
		if (button_down(KB_BUTTON('e')) and self.missionShow and self.speedStop == True and task.time >= 0.1):
			self.speedStop = False
			self.missionImg.removeNode()
			self.staminaBar.show()
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
					pickup.setVolume(self.volume)
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