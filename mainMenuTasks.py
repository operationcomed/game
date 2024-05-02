from direct.task import Task
from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *

class MainMenuTasks():
	def moveBackground(self, game, task):
		game.background_move_x = game.background_x
		game.background_move_y = game.background_y
		if (game.mouseWatcherNode.hasMouse()):
			game.background_move_x += (-game.mouseWatcherNode.getMouseX() * game.MMsensitivity)
			game.background_move_y += (-game.mouseWatcherNode.getMouseY() * game.MMsensitivity)
			game.card.setPos(game.background_move_x, 0, game.background_move_y)
		return Task.cont
	
	buttonHoverScale = 1.2
	def hoverEffect(self, game, task):
		for button in game.buttonList:
			if (button.node().getState() == 2 and button.hover != True):
				self.initHover(self, button)
			elif (button.node().getState() == 0 and button.hover != False):
				self.deinitHover(self, button)
		return Task.cont
	
	def initHover(self, button):
		button.hover = True
		button.sc2.start()

	def deinitHover(self, button):
		button.hover = False
		button.sc1.start()
		

mm_tasks = MainMenuTasks