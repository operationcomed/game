from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *
from direct.actor.Actor import Actor
from panda3d.ai import *
import math
import gametext

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Level3():

	cutsceneDone = False
	def l3Cutscene(self, game, task):
		if (not game.isPlaying):
			game.itemList = [['1', (-32, -50, 0), 'Key 1', 2], ['2', (-50, -633, 0), 'Key 2', 1], ['3', (185, -64, 0), 'Key 3', 0]]
			game.level = 3
			game.timeStart = 0
			gametext.Text.hideCH(game.game_text)
			game.fade.setColor(0, 0, 0, 0)
			game.speedStop = True
			game.music.stop()
			game.camera.setHpr(270, 0, 0)
			game.video_inst.playVid(game.video_inst, game, game.l3Video)
			game.speed1 = 0.05
			if (game.debug):
				game.fog.setExpDensity(0.0)
			else:
				game.fog.setExpDensity(0.035)
			game.alight.setColor((.15, .25, .35, 1))
		button_down = game.mouseWatcherNode.is_button_down

		if (task.time >= 36.55 or (button_down(KB_BUTTON('e')) and task.time >= 0.5)):
			game.health = 100
			game.music.play()
			game.video.removeNode()
			gametext.Text.showCH(game.game_text)
			gametext.Text.showText(game.game_text, game)
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
	
	def showNote(self, game, note):
		game.mouseLetGo = True
		gametext.Text.hideText(game.game_text, game)
		game.setBarVisibility(False)
		game.speedStop = True
		game.scaleFactorNote = 7/4
		game.noteImg = game.aspect2d.attachNewNode(game.cm.generate())
		game.noteImg.setScale((16/9)*game.scaleFactorNote, 1, game.scaleFactorNote)
		# these are the centers of the image
		game.note_x = (-16/9/2)*game.scaleFactorNote
		game.note_y = -0.5*game.scaleFactorNote
		game.noteImg.setPos(game.note_x, 0, game.note_y)
		game.noteImg.setTexture(game.loader.loadTexture('assets/img/l3/' + str(note) + '.png'))

		game.noteImg.setTransparency(TransparencyAttrib.MAlpha)
		game.acceptOnce("e", self.hideNote, [self, game])

	def fadeOut(t, self, game):
		if (t <= 0):
			game.noteImg.removeNode()
			return
		game.noteImg.setColorScale(1, 1, 1, t)
		game.noteImg.setScale(min(16/9*t*game.scaleFactorNote, 16/9*game.scaleFactorNote), min(t*game.scaleFactorNote, 1*game.scaleFactorNote), min(t*game.scaleFactorNote, 1*game.scaleFactorNote))

	def hideNote(self, game):
		dismiss = game.loader.loadSfx("assets/sound/dismiss.mp3")
		dismiss.setVolume(game.volume)
		dismiss.play()
		self.popout = LerpFunc(self.fadeOut,
            extraArgs=[self, game],
            fromData=1,
            toData=0,
            duration=0.25,
			blendType='easeOut',
            name="fadeo")
		self.popout.start()
		game.mouseLetGo = False
		gametext.Text.showText(game.game_text, game)
		game.setBarVisibility(True)
		game.speedStop = False
		self.note1Showing = False
	
	def cutsceneOver(self, game):
		#self.hallText = TextNode('escapenow')
		#self.hallText.setAlign(TextNode.ACenter)
		#self.hallText.setText("ESCAPE MSU\nNOW!")
		#self.hallText.setShadow(0.07, 0.07)
		#self.hallTxtNode = game.aspect2d.attachNewNode(self.hallText)
		#game.attachTextToHUD(self.hallTxtNode, self.hallText, (0, 0, 0), 0.15, game.font)
		#fadeout = Sequence(Wait(2.5), LerpColorScaleInterval(self.hallTxtNode, 2.5, (1, 1, 1, 0), blendType='easeIn')).start()
		self.initItems(self, game)
		self.note1Showing = True
		self.showNote(self, game, 0)

		ghostStartPos = Vec3(-21.93, -207.53, 0)
		self.seeker = Actor("models/camera")
		self.seeker.reparentTo(game.render)
		self.seeker.setScale(0.5)
		self.seeker.setPos(ghostStartPos)
		self.seeker.setR(180)

		self.AIworld = AIWorld(game.render)

		self.AIchar = AICharacter("seeker", self.seeker, 100, 0.8, 13)
		self.AIworld.addAiChar(self.AIchar)
		self.AIbehaviors = self.AIchar.getAiBehaviors()

		#AI World update
		self.AIbehaviors.pursue(game.ppnp)
		self.seeker.loop("run")

	#to update the AIWorld
	def AIUpdate(self, game, task):
		self.AIworld.update()
		return Task.cont
	
	def initItems(self, game):
		game.scaleFactorItem = 4
		# filename, position, human readable name
		game.items = []
		game.itemsImg = []
		game.cm = CardMaker('card')
		i = 0
		for itemPath in game.itemList:
			item = game.render.attachNewNode(game.cm.generate())
			item.setScale(game.scaleFactorItem, 1, game.scaleFactorItem)

			tex = game.loader.loadTexture('assets/items/l3/' + itemPath[0] + '.png')
			image = OnscreenImage(image='assets/items/l3/' + itemPath[0] + '.png', pos=(0.43+(i*0.25), 0, 0.7), scale=0.125)
			image.setColorScale(0.25, 0.25, 0.25, 0.5)
			image.setTransparency(TransparencyAttrib.MAlpha)
			item.setTexture(tex)

			item.setPos(itemPath[1])
			item.setTransparency(TransparencyAttrib.MAlpha)

			item.setBillboardAxis()

			game.items.append(item)
			game.itemsImg.append(image)
			i += 1
		
	
	fadeInit = False
	l3Init = False
	l3_1stInit = False # :)
	timeEnd = 0
	deltaTime = 0
	timeElapsed = 0
	minigameSelect = 0
	itemsGotten = 0
	missionDone = False
	taskTime = 0
	note1Showing = False
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

		i = 0
		for itemPos in game.itemList:
			if (abs(itemPos[1][0] - posX) <= 2 and abs(itemPos[1][1] - posY) <= 2 and itemPos[2] != None):
				if (itemPos[i][0] == '1'):	
					game.taskMgr.add(game.AIUpdate, "AIUpdate")
				self.itemsGotten += 1
				if (not (self.itemsGotten >= len(game.itemList))):
					self.showNote(self, game, itemPos[3])
				pickup = game.loader.loadSfx('assets/sound/pickup.wav')
				pickup.setLoop(False)
				pickup.setVolume(game.volume)
				pickup.play()
				game.items[i].removeNode()
				game.itemsImg[i].setColorScale(1, 1, 1, 1)
				itemPos[2] = None
				game.timeStart += 60
				game.speed1 += 0.01
				game.speed2 += 0.05
			i += 1

		if (self.itemsGotten >= 3 and not self.missionDone):
			doneSound = game.loader.loadSfx('assets/sound/done.mp3')
			doneSound.setLoop(False)
			doneSound.setVolume(game.volume)
			doneSound.play()
			self.missionDone = True
			game.game_text.itmText.setTextColor(0, 1, 0.5, 1)
			game.game_text.itmText.setText(game.game_text.itmText.getText() + "\n\n\n\n" + "You have all the keys.\nESCAPE MSU!")
			for img in game.itemsImg:
				img.setColorScale(0, 1, 0.5, 1)

		if (game.anagramRunning == True or game.isPlaying):
			game.ppnp.setZ(-0.45)
		elif (not self.l3Init and self.cutsceneDone and not self.note1Showing):
			game.timeStart = task.time
			self.timeText = TextNode('interact')
			self.timeText.setAlign(TextNode.ACenter)
			self.timeText.setText("5:00")
			self.timeText.setShadow(0.07, 0.07)
			self.timeTxtNode = game.aspect2d.attachNewNode(self.timeText)
			game.attachTextToHUD(self.timeTxtNode, self.timeText, (0, 0, 0.85), 0.15, game.font)
			self.l3Init = True
		if (self.l3Init and not self.note1Showing):
			game.timeElapsed = task.time - game.timeStart
			timeMinutes = math.floor(game.timeElapsed/60)
			timeSeconds = math.floor(game.timeElapsed)
			while (timeSeconds >= 60):
				timeSeconds -= 60
			while (timeSeconds < 0):
				timeSeconds += 60
			if (game.timeElapsed <= 600):
				self.timeText.setText(str(4-timeMinutes) + ":" + f"{59-timeSeconds:02}")
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

		if (posX >= 215 and posY >= -280 and posY <= -233 and game.isPlaying == False and self.missionDone):
			crosshair.setTextColor(1, 0.5, 0, 1)
			if (button_down(KB_BUTTON('e'))):
				self.timeEnd = task.time
				game.setBarVisibility(False)
				game.level = 3
				game.timeStart = 0
				gametext.Text.hideCH(game.game_text)
				game.fade.setColor(0, 0, 0, 0)
				game.speedStop = True
				game.music.stop()
				game.camera.setHpr(270, 0, 0)
				game.isPlaying = True
				game.video_inst.playVid(game.video_inst, game, game.esVideo)
				game.skipText.setText('')
		elif (game.isPlaying == False and self.missionDone):
			crosshair.setTextColor(1, 1, 1, 1)

		if (game.isPlaying):
			self.deltaTime = task.time - self.timeEnd
			print('wow', self.deltaTime)
			if (self.deltaTime >= 37):
				game.isPlaying == False
				props = WindowProperties()
				props.setCursorHidden(False)
				game.win.requestProperties(props)
				props = game.win.getProperties()
				game.music.stop()
				game.resetMinigames()
				game.unloadScene()
				game.mainMenu()
				
		return Task.cont

l3 = Level3