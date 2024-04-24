from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
import gametext

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Level2():
	def l2Cutscene(self, game, task):
		game.setBarVisibility(False)
		if (not game.isPlaying):
			gametext.Text.hideCH(game.game_text)
			game.speedStop = True
			game.music.stop()
			game.video_inst.playVid(game.video_inst, game, game.l2Video)

		button_down = game.mouseWatcherNode.is_button_down

		if (task.time >= 44 or (button_down(KB_BUTTON('e')) and task.time >= 0.5)):
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
	
	def mission(self, game, task):
		posX = game.ppnp.getX()
		posY = game.ppnp.getY()
		if (posX >= 20 and game.health >= 1):
			game.health -= 0.25
		return Task.cont


l2 = Level2