from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
import gametext
import anagram as ag

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Level2():

	ag = ag.ag

	def l2Cutscene(self, game, task):
		game.fog.setExpDensity(0.15)
		game.setBarVisibility(False)
		if (not game.isPlaying):
			gametext.Text.hideCH(game.game_text)
			game.fade.setColor(0, 0, 0, 0)
			game.speedStop = True
			game.music.stop()
			game.video_inst.playVid(game.video_inst, game, game.l2Video)

		button_down = game.mouseWatcherNode.is_button_down

		if (task.time >= 36.48 or (button_down(KB_BUTTON('e')) and task.time >= 0.5)):
			game.music.play()
			game.video.removeNode()
			gametext.Text.showCH(game.game_text)
			game.speedStop = False
			game.blackBg.destroy()
			game.sound.stop()
			game.setBarVisibility(True)
			game.isPlaying = False
			game.skipText.setText("")
			self.cutsceneOver(self, game)
			return Task.done
		
		return Task.cont
	
	def cutsceneOver(self, game):
		ag.Anagram.anagram(self.ag, game, self)
	
	def mission(self, game, task):
		posX = game.ppnp.getX()
		posY = game.ppnp.getY()
		if (posX >= 20 and game.health >= 1):
			game.health -= 0.25
		if (game.anagramRunning == True):
			game.ppnp.setZ(-0.46)
		return Task.cont


l2 = Level2