from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
import gametext

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Level0():
	def backstory(self, game, task):
		game.setBarVisibility(False)
		if (not game.isPlaying):
			gametext.Text.hideCH(game.game_text)
			game.speedStop = True
			game.music.stop()
			game.video_inst.playVid(game.video_inst, game, game.backstoryVideo)

		button_down = game.mouseWatcherNode.is_button_down

		if (task.time >= 47 or button_down(KB_BUTTON('e'))):
			game.music.play()
			game.video.removeNode()
			gametext.Text.showCH(game.game_text)
			game.speedStop = False
			game.blackBg.destroy()
			game.sound.stop()
			game.setBarVisibility(True)
			game.isPlaying = False
			game.skipText.setText("")
			return Task.done
		
		return Task.cont
	
	def bedDoor(self, game, task):
		rot = game.camera.getH()
		crosshair = game.game_text.itcText
		#chnp = aspect2d.attachNewNode(game.game_text.itcText)
		while rot > 360:
			rot -= 360
		while rot < 0:
			rot += 360
		# X: 1.5 -> -2.5
		# Y: < -4
		posX = game.camera.getX()
		posY = game.camera.getY()
		#print(posX, posY)
		doorInteract = False
		if ((posX >= -2.5 and posX <= 1.5) and posY <= -4):
			crosshair.setTextColor(1, 0.5, 0, 1)
			doorInteract = True
		else:
			crosshair.setTextColor(1, 1, 1, 1)
			doorInteract = False
			
		button_down = game.mouseWatcherNode.is_button_down
		if ((button_down(KB_BUTTON('e')) and doorInteract) or (button_down(KB_BUTTON('1')) and game.debug)):
			game.unloadScene()
			game.cameraOffset = 4
			game.loadScene("assets/models/inf.glb", (-17.0, 6.25, 5.414), (0, 0, 100.5), "assets/models/door.glb", game.missionLevel1)
		return Task.cont

l0 = Level0