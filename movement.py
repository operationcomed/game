from math import pi, sin, cos
from panda3d.core import *
from direct.gui.DirectGui import *

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Movement():
	accelZ = 0
	accelX = 0
	accelY = 0
	staminaDecay = 0.05
	def movement(self, game):
		button_down = game.mouseWatcherNode.is_button_down

		# print current position for debugging
		if (button_down(KB_BUTTON('p'))):
			print("X:", round(game.ppnp.getX(), 3), "Y:", round(game.ppnp.getY(), 3), "Z:", round(game.ppnp.getZ(), 3))
		if (button_down(KB_BUTTON('l'))):
			print("H:", round(game.camera.getH(), 3), "P:", round(game.camera.getP(), 3), "R:", round(game.camera.getR(), 3))

		has_mouse = game.mouseWatcherNode.hasMouse()
		rot_x = game.camera.getH()
		rot_y = game.camera.getP()
		rot_z = game.camera.getR()
		
		props = WindowProperties()
		if (game.settingsShow or game.mouseLetGo):
			props.setCursorHidden(False)
			game.win.requestProperties(props)
			props = game.win.getProperties()
			has_mouse = False

		# move screen with mouse
		if (has_mouse):
			# hides cursor
			props.setCursorHidden(True)
			game.win.requestProperties(props)
			props = game.win.getProperties()

			# limits cursor to the middle
			game.win.movePointer(0, props.getXSize() // 2, props.getYSize() // 2)
			mouse_x = game.mouseWatcherNode.getMouseX() * game.sensitivity
			mouse_y = game.mouseWatcherNode.getMouseY() * game.sensitivity

			# prevent camera from going upside down
			if (not game.speedStop):
				if (rot_y+mouse_y > 90):
					game.camera.setHpr(rot_x-mouse_x, 90, 0)
				elif (rot_y+mouse_y < -90):
					game.camera.setHpr(rot_x-mouse_x, -90, 0)
				else:
					game.camera.setHpr(rot_x-mouse_x, rot_y+mouse_y, 0)

		posX = game.ppnp.getX()
		posY = game.ppnp.getY()

		game.speed = 0.025

		if (game.debug):
			self.staminaDecay = 0.001
		# sprinting and stamina
		if (button_down(KB.shift()) and game.stamina >= 0 and game.sprintable):
			game.speed = 0.1
			if (button_down(KB_BUTTON('w')) or button_down(KB_BUTTON('a')) or button_down(KB_BUTTON('s')) or button_down(KB_BUTTON('d'))):
				game.stamina -= self.staminaDecay
		if (game.stamina <= 0.01):
			game.sprintable = False

		if (game.stamina < 0):
			game.stamina = 0

		if (game.speedStop):
			game.speed = 0

		if (game.sprintable == False and not game.barColored == 1):
			game.staminaBar["barColor"] = game.staminaRed
			game.barColored = 1
		elif (game.sprintable == True and not game.barColored == 2):
			game.staminaBar["barColor"] = game.staminaGreen
			game.barColored = 2
			
		# movement with smooth acceleration
		staminaGain = True
		if (button_down(KB_BUTTON('w')) and game.input == False):
			self.accelY += game.speed * cos(rot_x * (pi/180))
			self.accelX -= game.speed * sin(rot_x * (pi/180))
			staminaGain = False
		if (button_down(KB_BUTTON('s')) and game.input == False):
			self.accelY -= game.speed * cos(rot_x * (pi/180))
			self.accelX += game.speed * sin(rot_x * (pi/180))
			staminaGain = False
		if (button_down(KB_BUTTON('d')) and game.input == False):
			self.accelY += game.speed * sin(rot_x * (pi/180))
			self.accelX += game.speed * cos(rot_x * (pi/180))
			staminaGain = False
		if (button_down(KB_BUTTON('a')) and game.input == False):
			self.accelY -= game.speed * sin(rot_x * (pi/180))
			self.accelX -= game.speed * cos(rot_x * (pi/180))
			staminaGain = False

		if (not staminaGain and not game.speedStop):
			game.footsteps.setVolume(game.volume*0.2)
		else:
			game.footsteps.setVolume(0)
		if (game.staminaCap > game.stamina and staminaGain):
			game.stamina += 0.025
		elif (game.stamina >= game.staminaCap):
			game.stamina = game.staminaCap
			game.sprintable = True
		# jumping
		if (button_down(KB.space()) and not game.speedStop):
			game.ppnp.setZ(game.ppnp.getZ()+0.1)

		# fix for bug
		if (button_down(KB_BUTTON('o')) and game.timer <= 0 and game.input == False and game.debug == True and game.mouseLetGo == False):
			if (game.scene_rot):
				game.scene.setHpr(0, 0, 0)
				if (game.doorRot):
					try:
						game.doors.setHpr(0, 0, 0)
					except:
						''''''
				if (game.collisionMap != False):
					game.collisionMap.setHpr(0, 0, 0)
			else:
				game.scene.setHpr(0, 90, 0)
				if (game.doorRot):
					try:
						game.doors.setHpr(0, 90, 0)
					except:
						''''''
				if (game.collisionMap != False):
					game.collisionMap.setHpr(0, 90, 0)
			game.scene_rot = not game.scene_rot
			game.timer = 10
		game.timer -= 1
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
		if (game.ppnp.getZ() < -5):
			game.ppnp.setZ(10)
		game.ppnp.setX(posX)
		game.ppnp.setY(posY)
		game.camera.setPos(game.ppnp.getPos())
		game.camera.setZ(game.ppnp.getZ() + game.cameraOffset)

		game.staminaBar["value"] = game.stamina
		game.healthBar["value"] = game.health

		if (game.health <= 1):
			game.speedStop = True
			pickup = game.loader.loadSfx('assets/sound/pickup.wav')
			pickup.setLoop(False)
			pickup.setVolume(game.volume)
			pickup.play()

movement = Movement