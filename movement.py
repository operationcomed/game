from math import pi, sin, cos
from panda3d.core import *
from direct.gui.DirectGui import *
import direct.particles

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Movement():
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

		sensitivity = 30
		
		props = WindowProperties()
		if (button_down(KB.escape())):
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
			mouse_x = game.mouseWatcherNode.getMouseX() * sensitivity
			mouse_y = game.mouseWatcherNode.getMouseY() * sensitivity

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

		# sprinting and stamina
		if (button_down(KB.shift()) and game.stamina >= 0 and game.sprintable):
			game.speed = 0.1
			if (button_down(KB_BUTTON('w')) or button_down(KB_BUTTON('a')) or button_down(KB_BUTTON('s')) or button_down(KB_BUTTON('d'))):
				game.stamina -= 0.05
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
		# primitive ground collision checking
		#if (posZ < GROUND_POS):
		#	posZ = GROUND_POS
		#	game.accelZ = 0
		# movement with smooth acceleration
		# hala may math ew
		staminaGain = True
		if (button_down(KB_BUTTON('w'))):
			game.accelY += game.speed * cos(rot_x * (pi/180))
			game.accelX -= game.speed * sin(rot_x * (pi/180))
			staminaGain = False
		if (button_down(KB_BUTTON('s'))):
			game.accelY -= game.speed * cos(rot_x * (pi/180))
			game.accelX += game.speed * sin(rot_x * (pi/180))
			staminaGain = False
		if (button_down(KB_BUTTON('d'))):
			game.accelY += game.speed * sin(rot_x * (pi/180))
			game.accelX += game.speed * cos(rot_x * (pi/180))
			staminaGain = False
		if (button_down(KB_BUTTON('a'))):
			game.accelY -= game.speed * sin(rot_x * (pi/180))
			game.accelX -= game.speed * cos(rot_x * (pi/180))
			staminaGain = False

		if (game.staminaCap > game.stamina and staminaGain):
			game.stamina += 0.025
		elif (game.stamina >= game.staminaCap):
			game.stamina = game.staminaCap
			game.sprintable = True
		# jumping (note, for debugging purposes only)
		if (button_down(KB.space()) and not game.speedStop):
			game.ppnp.setZ(game.ppnp.getZ()+0.1)

		# misc
		#if (button_down(KB_BUTTON('m'))):
		#	gametext.Text.hideText(game.game_text)
		#	game.unloadScene()
		#if (button_down(KB_BUTTON('n'))):
		#	gametext.Text.showText(game.game_text)
		# fix for bug
		if (button_down(KB_BUTTON('o')) and game.timer <= 0):
			if (game.scene_rot):
				game.scene.setHpr(0, 0, 0)
				if (game.doorRot):
					game.doors.setHpr(0, 0, 0)
			else:
				game.scene.setHpr(0, 90, 0)
				if (game.doorRot):
					game.doors.setHpr(0, 90, 0)
			game.scene_rot = not game.scene_rot
			game.timer = 10
		game.timer -= 1
		# deceleration bcoz of gravity
		# game.accelZ -= game.gravity
		# deceleration bcoz of friction
		game.accelY *= 0.8
		game.accelX *= 0.8

		# apply acceleration to position
		posY += game.accelY
		posX += game.accelX

		# the speed is faster when you're going diagonally since we apply the acceleration like a square instead of a circle (?)
		if ((game.accelX * game.accelX) + (game.accelY * game.accelY) > 0.01):
			while ((game.accelX * game.accelX) + (game.accelY * game.accelY) > 0.01): 
				game.accelY *= 0.9
				game.accelX *= 0.9
				
				
		# see if the player has fallen off of the world
		if (game.ppnp.getZ() < -5):
			game.ppnp.setZ(10)
		game.ppnp.setX(posX)
		game.ppnp.setY(posY)
		game.camera.setPos(game.ppnp.getPos())
		game.camera.setZ(game.ppnp.getZ() + game.cameraOffset)

		game.staminaBar["value"] = game.stamina

movement = Movement