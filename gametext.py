from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from math import pi, sin, cos
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import *

class text(ShowBase):
	SHOW_TEXT = True

	coordinateText = TextNode('ctext')
	coordinateText.setText("X:0 Y:0 Z:0")
	coordinateText.setShadow(0.15, 0.15)

	escText = TextNode('esc')
	escText.setText("Hold escape to let go of mouse.\nPress X to exit.")
	escText.setShadow(0.15, 0.15)

	ctlText = TextNode('controls')
	ctlText.setText("Use WASD to move. Space to jump.")
	ctlText.setShadow(0.15, 0.15)

	escapeText = TextNode('efschool')
	escapeText.setText("Escape from MSU")
	escapeText.setShadow(0.15, 0.15)

	def hideText(self):
		global SHOW_TEXT 
		SHOW_TEXT = False
		# 100% easier by loading and unloading these procedurally thru a text file
		self.escText.setText("")
		self.ctlText.setText("")
		self.escapeText.setText("")

	def showText(self):
		global SHOW_TEXT 
		SHOW_TEXT = True
		# 100% easier by loading and unloading these procedurally thru a text file
		self.escText.setText("Hold escape to let go of mouse.\nPress X to exit.")
		self.ctlText.setText("Use WASD to move. Space to jump.")
		self.escapeText.setText("Escape from MSU")