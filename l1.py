from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import *
import gametext

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Level1():
	missionShow = False
	initItemsDone = False
	missionDone = False
	itemsGotten = 0

	levelDone = False
	timeEnd = 0
	deltaTime = 0
	def fadeOut(t, self, game):
		if (t <= 0):
			game.missionImg.removeNode()
			return
		game.missionImg.setColorScale(1, 1, 1, t)
		game.missionImg.setScale(min(16/9*t*game.scaleFactorMission, 16/9*game.scaleFactorMission), min(t*game.scaleFactorMission, 1*game.scaleFactorMission), min(t*game.scaleFactorMission, 1*game.scaleFactorMission))

	def mission(self, game, task):
		crosshair = game.game_text.itcText
		button_down = game.mouseWatcherNode.is_button_down

		if (min((task.time*0.4), 0) == 0):
			game.filters.setBlurSharpen(min((task.time*0.4), 1))
		elif ((task.time*0.2) >= -0.1):
			game.filters.delBlurSharpen()
		if (min(2-(task.time*0.8), 0) == 0):
			game.fade.setColor(0, 0, 0, 2-(task.time*0.8))
		elif (2-(task.time*0.8) >= -0.1):
			game.fade.setColor(0, 0, 0, 0)
			print("done")

		if (not self.missionShow):
			doorSound = game.loader.loadSfx("assets/sound/doorClose.mp3")
			doorSound.setVolume(game.volume)
			doorSound.play()
			self.missionShow = True
			game.speedStop = True
			self.showMission(self, game)
		
		if (button_down(KB_BUTTON('e')) and self.missionShow and game.speedStop == True and task.time >= 0.1):
			game.itmTxtNode.show()
			game.speedStop = False
			game.setBarVisibility(True)
			for img in game.itemsImg:
				img["scale"] = 0.15
			gametext.Text.showText(game.game_text, game)
			self.popout = LerpFunc(self.fadeOut,
        	    extraArgs=[self, game],
        	    fromData=1,
        	    toData=0,
        	    duration=0.25,
				blendType='easeOut',
        	    name="fadeo")
			self.popout.start()
			dismiss = game.loader.loadSfx("assets/sound/dismiss.mp3")
			dismiss.setVolume(game.volume)
			dismiss.play()
		
		if (not self.initItemsDone):
			self.initItems(self, game)
		else:
			posX = game.ppnp.getX()
			posY = game.ppnp.getY()
			#posZ = game.ppnp.getZ() # no z axis atm because it'll be a hassle
			i = 0
			for itemPos in game.itemList:
				if (abs(itemPos[1][0] - posX) <= 2 and abs(itemPos[1][1] - posY) <= 2 and itemPos[2] != None):
					pickup = game.loader.loadSfx('assets/sound/pickup.wav')
					pickup.setLoop(False)
					pickup.setVolume(game.volume)
					pickup.play()
					game.items[i].removeNode()
					self.itemsGotten += 1
					#game.game_text.itmText.setText(game.game_text.itmText.getText() + "\n" + itemPos[2])
					game.itemsImg[i].setColorScale(1, 1, 1, 1)
					itemPos[2] = None
				i += 1
		
		posX = game.camera.getX()
		posY = game.camera.getY()
		if (self.itemsGotten >= 5 and not self.missionDone):
			doneSound = game.loader.loadSfx('assets/sound/done.mp3')
			doneSound.setLoop(False)
			doneSound.play()
			self.missionDone = True
			game.game_text.itmText.setTextColor(0, 1, 0.5, 1)
			game.game_text.itmText.setText(game.game_text.itmText.getText() + "\n\n\n\n" + "You can escape through the door now!")
			for img in game.itemsImg:
				img.setColorScale(0, 1, 0.5, 1)
		if ((posX >= 11 and posX <= 17) and posY <= -20 and self.itemsGotten >= 5):
			crosshair.setTextColor(1, 0.5, 0, 1)
			doorInteract = True
		else: 
			crosshair.setTextColor(1, 1, 1, 1)
			doorInteract = False

		if (((button_down(KB_BUTTON('e')) and doorInteract) or (button_down(KB_BUTTON('2')) and game.debug)) and self.levelDone != True):
			for img in game.itemsImg:
				img.destroy()
			if (game.debug):
				for item in game.items:
					item.removeNode()
			self.levelDone = True
			game.setBarVisibility(False)
			self.timeEnd = task.time
			doorSound = game.loader.loadSfx("assets/sound/door.mp3")
			doorSound.setVolume(game.volume)
			doorSound.play()

		if (self.levelDone):
			self.deltaTime = task.time - self.timeEnd
			game.fade.setColor(0, 0, 0, min(self.deltaTime*2, 1))
			if (self.deltaTime >= 1):
				game.unloadScene()
				game.game_text.itmText.setTextColor(1, 1, 1, 1)
				game.game_text.itmText.setText("Items obtained:")
				game.loadScene("assets/models/msu.glb", (-3.2, -12.8, -0.45), (0, 0, 1000.5), customTask=game.missionLevel2)
				game.taskMgr.add(game.l2Cutscene, "l2Cutscene")

		return Task.cont
	
	def initItems(self, game):
		self.initItemsDone = True
		game.scaleFactorItem = 4
		# filename, position, human readable name
		game.itemList = [['1_mask', (4.4, 17.5, 0), 'Mask'], ['2_cert', (-7.25, -18.25, 0), 'Medical Certificate'], ['3_excuse', (-9.5, 12.65, 0), 'Excuse Letter'], ['4_meds', (18, -18, 0), 'Medicine'], ['5_prescription', (-15, -7.8, 0), 'Doctor\'s Prescription']]
		game.items = []
		game.itemsImg = []
		game.cm = CardMaker('card')
		i = 0
		for itemPath in game.itemList:
			item = game.render.attachNewNode(game.cm.generate())
			item.setScale(game.scaleFactorItem, 1, game.scaleFactorItem)

			tex = game.loader.loadTexture('assets/items/' + itemPath[0] + '.png')
			image = OnscreenImage(image='assets/items/' + itemPath[0] + '.png', pos=(-0.07+(i*0.25), 0, 0.7), scale=(0))
			image.setColorScale(0.25, 0.25, 0.25, 0.5)
			image.setTransparency(TransparencyAttrib.MAlpha)
			item.setTexture(tex)

			item.setPos(itemPath[1])
			item.setTransparency(TransparencyAttrib.MAlpha)

			item.setBillboardAxis()

			game.items.append(item)
			game.itemsImg.append(image)
			i += 1

	def showMission(self, game):
		gametext.Text.hideText(game.game_text, game)
		game.scaleFactorMission = 7/4
		game.cm = CardMaker('card')
		game.missionImg = game.aspect2d.attachNewNode(game.cm.generate())
		game.missionImg.setScale((16/9)*game.scaleFactorMission, 1, game.scaleFactorMission)

		game.tex = game.loader.loadTexture('assets/missions/1.png')
		game.missionImg.setTexture(game.tex)

		# these are the centers of the image
		game.mission_x = (-16/9/2)*game.scaleFactorMission
		game.mission_y = -0.5*game.scaleFactorMission

		game.missionImg.setPos(game.mission_x, 0, game.mission_y)
		game.missionImg.setTransparency(TransparencyAttrib.MAlpha)


l1 = Level1