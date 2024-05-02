from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
import gametext

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Level0():
	backstoryDone = False
	def backstory(self, game, task):
		button_down = game.mouseWatcherNode.is_button_down

		if (task.time <= 0.5):
			game.music.setVolume((1-task.time)*game.volume)
			game.fade.setColor(0, 0, 0, task.time*2)
			return Task.cont

		if (not game.isPlaying):
			for node in game.charNodes:
				node.removeNode()
			game.loadScene("assets/models/bed.glb", (3.5, 6, 1.42), (0, 0, 10), doors=False, customTask=game.bedDoor, collisionMap="assets/models/bed.glb", playerRot=(180, -90, 0), startDark=True)
			game.helpMenu()
			game.itmTxtNode.hide()
			game.fade.setColor(0, 0, 0, 0)
			gametext.Text.hideCH(game.game_text)
			game.speedStop = True
			game.music.stop()
			game.video_inst.playVid(game.video_inst, game, game.backstoryVideo)
		else:
			game.ppnp.setPos(3.5, 6, 1.42)

		button_down = game.mouseWatcherNode.is_button_down

		if (task.time >= 47 or button_down(KB_BUTTON('e'))):
			game.music.play()
			game.video.removeNode()
			gametext.Text.showCH(game.game_text)
			game.speedStop = False
			game.blackBg.destroy()
			game.sound.stop()
			game.isPlaying = False
			game.skipText.setText("")
			self.backstoryDone = True
			game.fade.setColor(0, 0, 0, 1)
			return Task.done

		return Task.cont
	
	levelDone = False
	fadeInit = False
	timeEnd = 0
	deltaTime = 0
	def bedDoor(self, game, task):
		if (self.backstoryDone and not self.fadeInit):
			self.timeEnd = task.time
			game.setBarVisibility(True)
			self.fadeInit = True
		elif (self.backstoryDone):
			self.deltaTime = task.time - self.timeEnd
			game.fade.setColor(0, 0, 0, max(1-self.deltaTime*1, 0))
			if (max(1-self.deltaTime*1, 0) == 0):
				self.backstoryDone = False
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
		if (((button_down(KB_BUTTON('e')) and doorInteract) or (button_down(KB_BUTTON('1')) and game.debug)) and self.levelDone == False):
			if (game.helpDisplay):
				game.helpMenu()
			self.levelDone = True
			self.timeEnd = task.time
			game.setBarVisibility(False)
			doorSound = game.loader.loadSfx("assets/sound/door.mp3")
			doorSound.setVolume(game.volume)
			doorSound.play()
		if ((button_down(KB_BUTTON('2')) and game.debug)):
			game.itmTxtNode.show()
			if (game.helpDisplay):
				game.helpMenu()
			self.timeEnd = task.time
			game.setBarVisibility(False)
			doorSound = game.loader.loadSfx("assets/sound/door.mp3")
			doorSound.setVolume(game.volume)
			doorSound.play()
			game.unloadScene()
			game.game_text.itmText.setTextColor(1, 1, 1, 1)
			game.game_text.itmText.setText("Items obtained:")
			game.loadScene("assets/models/msu.glb", (-3.2, -12.8, -0.45), (0, 0, 1000.5), customTask=game.missionLevel2, collisionMap="assets/collisionmaps/msu.glb", noCache=True)
			game.taskMgr.add(game.l2Cutscene, "l2Cutscene")

		if (self.levelDone):
			self.deltaTime = task.time - self.timeEnd
			game.fade.setColor(0, 0, 0, min(self.deltaTime*2, 1))
			game.filters.setBlurSharpen(max(1-(self.deltaTime*2), 0))
			if (self.deltaTime >= 1):
				game.unloadScene()
				game.cameraOffset = 4
				game.loadScene("assets/models/inf.glb", (-17.0, 6.25, 5.414), (0, 0, 100.5), "assets/models/door.glb", game.missionLevel1, collisionMap="assets/collisionmaps/inf.glb")
		return Task.cont

l0 = Level0