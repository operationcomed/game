from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *
import math
import gametext
import anagram as ag
import r1

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Level2():

	ag = ag.ag
	r1 = r1.r1

	cutsceneDone = False
	def l2Cutscene(self, game, task):
		game.fog.setExpDensity(0.1)
		if (not game.isPlaying):
			game.level = 2
			game.timeStart = 0
			gametext.Text.hideCH(game.game_text)
			game.fade.setColor(0, 0, 0, 0)
			game.speedStop = True
			game.music.stop()
			game.video_inst.playVid(game.video_inst, game, game.l2Video)

		button_down = game.mouseWatcherNode.is_button_down

		if (task.time >= 36.55 or (button_down(KB_BUTTON('e')) and task.time >= 0.5)):
			game.music.play()
			game.video.removeNode()
			gametext.Text.showCH(game.game_text)
			game.speedStop = False
			game.blackBg.destroy()
			game.sound.stop()
			game.isPlaying = False
			self.cutsceneDone = True
			game.skipText.setText("")
			self.cutsceneOver(self, game)
			return Task.done
		
		return Task.cont
	
	def cutsceneOver(self, game):
		ag.Anagram.anagram(self.ag, game, self)
	
	fadeInit = False
	l2Init = False
	l2_1stInit = False # :)
	timeEnd = 0
	deltaTime = 0
	timeElapsed = 0
	minigameSelect = 0
	def mission(self, game, task):
		crosshair = game.game_text.itcText
		button_down = game.mouseWatcherNode.is_button_down

		if (not self.l2_1stInit):
			self.l2_1stInit = True
			self.damager = LerpColorScaleInterval(game.render, 0.25, (1, 0.1, 0, 1), (1, 1, 1, 1))
			self.undamager = LerpColorScaleInterval(game.render, 0.25, (1, 1, 1, 1), (1, 0.1, 0, 1))

		if (self.cutsceneDone and not self.fadeInit):
			self.timeEnd = task.time
			self.fadeInit = True
		elif (self.cutsceneDone):
			self.deltaTime = task.time - self.timeEnd
			game.fade.setColor(0, 0, 0, max(1-self.deltaTime*1, 0))
			if (max(1-self.deltaTime*1, 0) == 0):
				self.backstoryDone = False
		posX = game.ppnp.getX()
		posY = game.ppnp.getY()
		if ((posX >= 35 or posY >= 0) and game.health >= 1):
			game.health -= 0.25
			game.damaging = True
		else:
			game.damaging = False

		# minigames
		if (posX <= -32.5):
			# minigame 1
			if (posY <= -99 and posY >= -126 and not game.r1Done and not game.r1Running):
				crosshair.setTextColor(1, 0.5, 0, 1)
				self.minigameSelect = 1
		else:
			crosshair.setTextColor(1, 1, 1, 1)
			self.minigameSelect = 0

		if (self.minigameSelect == 1 and not game.r1Done and not game.r1Running and button_down(KB_BUTTON('e'))):
			mov = game.ppnp.posInterval(0.5, (-34.75, -112.636, -0.477))
			rot = game.camera.hprInterval(0.5, (270, 0, 0))
			move = Parallel(mov, rot, name="move")
			move.start()
			r1.Room1.mensa(self.r1, game, self)

		if ((game.damaging and not self.damager.isPlaying()) and ((1, round(game.render.getColorScale()[1], 2), round(game.render.getColorScale()[2], 2), 1) == (1, 1, 1, 1))):
				self.damager.start()
		elif ((not self.undamager.isPlaying()) and ((1, round(game.render.getColorScale()[1], 2), round(game.render.getColorScale()[2], 2), 1) == (1, 0.1, 0, 1))):
				self.undamager.start()

		if (game.anagramRunning == True or game.isPlaying):
			game.ppnp.setZ(-0.45)
		elif (not self.l2Init and self.cutsceneDone):
			game.timeStart = task.time
			self.timeText = TextNode('interact')
			self.timeText.setAlign(TextNode.ACenter)
			self.timeText.setText("10:00")
			self.timeText.setShadow(0.07, 0.07)
			self.timeTxtNode = game.aspect2d.attachNewNode(self.timeText)
			game.attachTextToHUD(self.timeTxtNode, self.timeText, (0, 0, 0.85), 0.15, game.font)
			self.l2Init = True
		if (self.l2Init):
			game.timeElapsed = task.time - game.timeStart
			timeMinutes = math.floor(game.timeElapsed/60)
			timeSeconds = math.floor(game.timeElapsed)
			while (timeSeconds >= 60):
				timeSeconds -= 60
			if (game.timeElapsed <= 600):
				self.timeText.setText(str(9-timeMinutes) + ":" + f"{59-timeSeconds:02}")
			else:
				self.timeText.setText("0:00")
		return Task.cont


l2 = Level2