from direct.showbase.ShowBase import ShowBase
from direct.showbase import Audio3DManager
from math import pi, sin, cos
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from direct.gui.OnscreenText import OnscreenText
from direct.filter.CommonFilters import CommonFilters
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import *
from direct.gui.DirectGui import *
from panda3d.physics import ActorNode, ForceNode, LinearVectorForce, PhysicsCollisionHandler
import time
import gametext

class MainMenuTasks():
	def moveBackground(self, game, task):
		game.background_move_x = game.background_x
		game.background_move_y = game.background_y
		if (game.mouseWatcherNode.hasMouse()):
			game.background_move_x += (-game.mouseWatcherNode.getMouseX() * game.sensitivity)
			game.background_move_y += (-game.mouseWatcherNode.getMouseY() * game.sensitivity)
			game.card.setPos(game.background_move_x, 0, game.background_move_y)
		return Task.cont
	
	buttonHoverScale = 1.2
	def hoverEffect(self, game, task):
		for button in game.buttonList:
			if (button.node().getState() == 2):
				button.setScale(game.buttonHoverScale*button.scale[0], game.buttonHoverScale*button.scale[1], game.buttonHoverScale*button.scale[2])
			else:
				button.setScale(button.scale)
		return Task.cont

mm_tasks = MainMenuTasks