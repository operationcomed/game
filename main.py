from direct.showbase.ShowBase import ShowBase
from math import pi, sin, cos
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from direct.gui.OnscreenText import OnscreenText
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import *

# function shorthand
KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton
# tentative jumping solution
GROUND_POS = 3

# antialiasing
loadPrcFileData("", "framebuffer-multisample 1")
loadPrcFileData("", "multisamples 4")

# window title
loadPrcFileData("", "window-title game of the year 2024")
loadPrcFileData("", "default-fov 60")

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
		self.camLens.setNearFar(1, 1000)

		# lights and shadows
		alight = AmbientLight("alight1")
		alnp = self.render.attachNewNode(alight)
		alight.setColor((.35, .5, .7, 1))

		self.slight = Spotlight('slight')
		self.slight.setColor((125, 110, 100, 1))
		self.lens = PerspectiveLens()
		self.slight.setLens(self.lens)
		self.slnp = self.render.attachNewNode(self.slight)
		self.slnp.node().setShadowCaster(True, 2048, 2048)
		self.slnp.setPos(0, -6, 15)
		self.slnp.setHpr(0, -30, 0)
		self.lens.setNearFar(1, 1000000)

		self.render.setLight(self.slnp)
		self.render.setLight(alnp)

		# tentative scene
		self.scene = self.loader.loadModel("models/environment")

		self.scene.reparentTo(self.render)

		self.scene.setScale(0.125, 0.125, 0.125)
		self.scene.setPos(-8, 32, 0)

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
		self.pandaActor2 = Actor("models/panda-model", {"walk": "models/panda-walk4"})

		self.pandaActor2.setScale(0.0025, 0.0025, 0.0025)
		self.pandaActor2.reparentTo(self.render)
		self.pandaActor2.setHpr(180, 0, 0)
		self.pandaActor2.loop("walk")

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

		self.coordinateText = TextNode('ctext')
		self.coordinateText.setText("X:0 Y:0 Z:0")
		self.textNodePath = aspect2d.attachNewNode(self.coordinateText)
		self.textNodePath.setScale(0.07)
		self.textNodePath.setPos(-1.2, 0, 0.8)
		self.coordinateText.setShadow(0.15, 0.15)

		self.escapeText = TextNode('efschool')
		self.escapeText.setText("Escape from MSU")
		self.textNodePath = aspect2d.attachNewNode(self.escapeText)
		self.textNodePath.setScale(0.07)
		self.textNodePath.setPos(0.6, 0, 0.9)
		self.escapeText.setShadow(0.15, 0.15)
		
		# filters 
		filters = CommonFilters(self.win, self.cam)
		filters.setAmbientOcclusion()
		filters.setBloom(intensity=0.1)

		# fog
		fog = Fog("Fog Name")
		fog.setColor(0.1, 0.15, 0.175)
		fog.setExpDensity(0.01)
		self.render.setFog(fog)

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
		if (button_down(KB.space()) and posZ < GROUND_POS + 0.1):
			self.accelZ += 0.25

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
	
	def coordinateTask(self, task):
		posX = round(self.camera.getX())
		posY = round(self.camera.getY())
		posZ = round(self.camera.getZ())
		self.coordinateText.setText("X:" + str(posX) + " Y:" + str(posY) + "  Z:" + str(posZ))

		if (abs(posX) > 80 or abs(posY) > 30):
			self.escapeText.setText("YOU HAVE ESCAPED\nfrom msu!")
		return Task.cont
app = game()
app.run()