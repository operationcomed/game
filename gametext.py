from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from math import pi, sin, cos
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import *

class Text():
	escText = TextNode('esc')
	escText.setText("Hold escape to let go of mouse.\nPress X to exit.")
	escText.setShadow(0.15, 0.15)

	ctlText = TextNode('controls')
	ctlText.setText("Use WASD to move. Space to jump.")
	ctlText.setShadow(0.15, 0.15)

	def hideText(self):
		# 100% easier by loading and unloading these procedurally thru a text file
		self.escText.setText("")
		self.ctlText.setText("")

	def showText(self):
		# 100% easier by loading and unloading these procedurally thru a text file
		self.escText.setText("Hold escape to let go of mouse.\nPress X to exit.")
		self.ctlText.setText("Use WASD to move. Space to jump.")

# gametext instance
game_text = Text