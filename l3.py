from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *
import math
import gametext

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Level3():

	cutsceneDone = False
	def l3Cutscene(self, game, task):
		game.fog.setExpDensity(0.025)
		if (not game.isPlaying):
			game.level = 3
			game.timeStart = 0
			gametext.Text.hideCH(game.game_text)
			game.fade.setColor(0, 0, 0, 0)
			game.speedStop = True
			game.music.stop()
			game.camera.setHpr(270, 0, 0)
			game.video_inst.playVid(game.video_inst, game, game.l3Video)
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
			game.setBarVisibility(True)
			self.cutsceneOver(self, game)
			return Task.done
		
		return Task.cont
	
	def cutsceneOver(self, game):
		self.hallText = TextNode('escapenow')
		self.hallText.setAlign(TextNode.ACenter)
		self.hallText.setText("ESCAPE MSU\nNOW!")
		self.hallText.setShadow(0.07, 0.07)
		self.hallTxtNode = game.aspect2d.attachNewNode(self.hallText)
		game.attachTextToHUD(self.hallTxtNode, self.hallText, (0, 0, 0), 0.15, game.font)
		fadeout = Sequence(Wait(2.5), LerpColorScaleInterval(self.hallTxtNode, 2.5, (1, 1, 1, 0), blendType='easeIn')).start()
	
	fadeInit = False
	l3Init = False
	l3_1stInit = False # :)
	timeEnd = 0
	deltaTime = 0
	timeElapsed = 0
	minigameSelect = 0
	def mission(self, game, task):
		crosshair = game.game_text.itcText
		button_down = game.mouseWatcherNode.is_button_down

		if (not self.l3_1stInit):
			self.l3_1stInit = True
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

		if ((game.damaging and not self.damager.isPlaying()) and ((1, round(game.render.getColorScale()[1], 2), round(game.render.getColorScale()[2], 2), 1) == (1, 1, 1, 1))):
				self.damager.start()
		elif ((not self.undamager.isPlaying()) and ((1, round(game.render.getColorScale()[1], 2), round(game.render.getColorScale()[2], 2), 1) == (1, 0.1, 0, 1))):
				self.undamager.start()

		if (game.anagramRunning == True or game.isPlaying):
			game.ppnp.setZ(-0.45)
		elif (not self.l3Init and self.cutsceneDone):
			game.timeStart = task.time
			self.timeText = TextNode('interact')
			self.timeText.setAlign(TextNode.ACenter)
			self.timeText.setText("1:00")
			self.timeText.setShadow(0.07, 0.07)
			self.timeTxtNode = game.aspect2d.attachNewNode(self.timeText)
			game.attachTextToHUD(self.timeTxtNode, self.timeText, (0, 0, 0.85), 0.15, game.font)
			self.l3Init = True
		if (self.l3Init):
			game.timeElapsed = task.time - game.timeStart
			timeMinutes = math.floor(game.timeElapsed/60)
			timeSeconds = math.floor(game.timeElapsed)
			while (timeSeconds >= 60):
				timeSeconds -= 60
			if (game.timeElapsed <= 60):
				self.timeText.setText(str(1-timeMinutes) + ":" + f"{59-timeSeconds:02}")
			else:
				self.timeText.setText("0:00")
				props = WindowProperties()
				props.setCursorHidden(False)
				game.win.requestProperties(props)
				props = game.win.getProperties()
				game.music.stop()
				game.resetMinigames()
				game.unloadScene()
				game.mainMenu()
		if (posX >= 40):
			game.setBarVisibility(False)
			game.unloadScene()
			game.level = 3
			game.timeStart = 0
			gametext.Text.hideCH(game.game_text)
			game.fade.setColor(0, 0, 0, 0)
			game.speedStop = True
			game.music.stop()
			game.camera.setHpr(270, 0, 0)
			game.video_inst.playVid(game.video_inst, game, game.esVideo)
			game.skipText.setText('')
			if (not game.video.isPlaying):
				props = WindowProperties()
				props.setCursorHidden(False)
				game.win.requestProperties(props)
				props = game.win.getProperties()
				game.music.stop()
				game.resetMinigames()
				game.unloadScene()
				game.mainMenu()
				
		return Task.cont

	itemNo = 0
	def addItem(self, game, item):
		self.itemNo += 1
		image = OnscreenImage(image='assets/img/l3/collect/' + item +'.png', pos=(-0.07+(self.itemNo*0.25), 0, 0.7), scale=(0.15))
		image.setTransparency(TransparencyAttrib.MAlpha)
		game.itemsImg.append(image)

l3 = Level3