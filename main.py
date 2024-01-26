from direct.showbase.ShowBase import ShowBase
from math import pi, sin, cos
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *

# function shorthand
KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton
# tentative jumping solution
GROUND_POS = 3

# antialiasing
loadPrcFileData("", "framebuffer-multisample 1")
loadPrcFileData("", "multisamples 16")

# window title
loadPrcFileData("", "window-title game of the year 2024")

class game(ShowBase):

	accelZ = 0
	#accelZCap = 1

	accelX = 0
	#accelXCap = 0.4
	accelY = 0
	#accelYCap = 0.4

	def __init__(self):
		ShowBase.__init__(self)

		# disable panda3d default mouse input
		self.disable_mouse()

		# antialiasing
		self.render.setAntialias(AntialiasAttrib.MAuto)
		
		self.render.setShaderAuto()

		# camera
		self.camLens.setFocalLength(1)

		self.camLens.setNearFar(1, 1000)

		# lights and shadows
		alight = AmbientLight("alight1")
		alnp = self.render.attachNewNode(alight)
		alight.setColor((.25, .25, .25, .1))

		slight = Spotlight('slight')
		slight.setColor((100, 100, 100, 1))
		lens = PerspectiveLens()
		slight.setLens(lens)
		slnp = self.render.attachNewNode(slight)
		slnp.setPos(0, -15, 2)

		# tentative scene
		self.scene = self.loader.loadModel("models/environment")

		self.scene.reparentTo(self.render)

		self.scene.setScale(0.125, 0.125, 0.125)
		self.scene.setPos(-8, 42, 0)

		self.render.setLight(slnp)
		self.render.setLight(alnp)

		# tentative pandas
		self.pandaActor = Actor("models/panda-model", {"walk": "models/panda-walk4"})

		self.pandaActor.setScale(0.005, 0.005, 0.005)
		self.pandaActor.reparentTo(self.render)
		self.pandaActor.setPos(0, 10, 0)
		self.pandaActor.loop("walk")

		# this panda is u ;) baby panda
		global pandaActor2
		pandaActor2 = Actor("models/panda-model", {"walk": "models/panda-walk4"})

		pandaActor2.setScale(0.0025, 0.0025, 0.0025)
		pandaActor2.reparentTo(self.camera)
		pandaActor2.setPos(0, 5, -2)
		pandaActor2.setHpr(180, 0, 0)
		pandaActor2.loop("walk")

		# tasks
		self.taskMgr.add(self.moveTask, "moveTask")
		self.taskMgr.add(self.coordinateTask, "coordinateTask")

		# text
		ctlText = TextNode('controls')
		ctlText.setText("Use WASD to move. Space to jump.")
		self.textNodePath = aspect2d.attachNewNode(ctlText)
		self.textNodePath.setScale(0.07)
		self.textNodePath.setPos(-1.2, 0, 0.9)
		ctlText.setShadow(0.15, 0.15)

		escText = TextNode('esc')
		escText.setText("Hold escape to let go of mouse.\nPress X to exit.")
		self.textNodePath = aspect2d.attachNewNode(escText)
		self.textNodePath.setScale(0.07)
		self.textNodePath.setPos(-1.2, 0, -0.85)
		escText.setShadow(0.15, 0.15)

		global coordinateText
		coordinateText = TextNode('ctext')
		coordinateText.setText("X:0 Y:0 Z:0")
		self.textNodePath = aspect2d.attachNewNode(coordinateText)
		self.textNodePath.setScale(0.07)
		self.textNodePath.setPos(-1.2, 0, 0.8)
		coordinateText.setShadow(0.15, 0.15)

	# basic player movement
	def moveTask(self, task):
		button_down = self.mouseWatcherNode.is_button_down
		if (button_down(KB_BUTTON('x'))):
			exit()

		has_mouse = self.mouseWatcherNode.hasMouse()
		rot_x = self.camera.getH()
		rot_y = self.camera.getP()
		rot_z = self.camera.getR()

		sensitivity = 20
		
		props = WindowProperties()
		if (button_down(KB.escape())):
			has_mouse = False

		# move screen with mouse
		if (has_mouse):
			# hides cursor
			props.setCursorHidden(True)
			self.win.requestProperties(props)
			props = base.win.getProperties()

			# limits cursor to the middle
			self.win.movePointer(0, props.getXSize() // 2, props.getYSize() // 2)
			mouse_x = self.mouseWatcherNode.getMouseX() * sensitivity
			mouse_y = self.mouseWatcherNode.getMouseY() * sensitivity
			self.camera.setHpr(rot_x-mouse_x, rot_y+mouse_y, 0)

		posX = self.camera.getX()
		posY = self.camera.getY()
		posZ = self.camera.getZ()

		# movement with smooth acceleration
		# hala may math ew
		if (button_down(KB_BUTTON('w'))):
			self.accelY += 0.05 * cos(rot_x * (pi/180))
			self.accelX -= 0.05 * sin(rot_x * (pi/180))
		if (button_down(KB_BUTTON('s'))):
			self.accelY -= 0.05 * cos(rot_x * (pi/180))
			self.accelX += 0.05 * sin(rot_x * (pi/180))
		if (button_down(KB_BUTTON('d'))):
			self.accelY += 0.05 * sin(rot_x * (pi/180))
			self.accelX += 0.05 * cos(rot_x * (pi/180))
		if (button_down(KB_BUTTON('a'))):
			self.accelY -= 0.05 * sin(rot_x * (pi/180))
			self.accelX -= 0.05 * cos(rot_x * (pi/180))
		# jumping
		if (button_down(KB.space()) and posZ < GROUND_POS + 0.5):
			self.accelZ += 0.1

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
		
		# don't rotate the panda
		pandaActor2.setP(rot_y)
		return Task.cont
	
	def coordinateTask(self, task):
		posX = round(self.camera.getX())
		posY = round(self.camera.getY())
		posZ = round(self.camera.getZ())
		coordinateText.setText("X:" + str(posX) + " Y:" + str(posY) + "  Z:" + str(posZ))
		return Task.cont
app = game()
app.run()