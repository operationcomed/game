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

	ctlText = TextNode('controls')
	ctlText.setText("Press H for help menu.")
	ctlText.setShadow(0.15, 0.15)

	stmText = TextNode('controls')
	stmText.setText("Stamina:")
	stmText.setShadow(0.15, 0.15)

	itmText = TextNode('items')
	itmText.setText("Items obtained:")
	itmText.setShadow(0.15, 0.15)
	itmText.setAlign(TextNode.ARight)

	itcText = TextNode('interact')
	itcText.setText("+")
	itcText.setShadow(0.07, 0.07)


	def hideText(self):
		# 100% easier by loading and unloading these procedurally thru a text file
		self.ctlText.setText("")
		self.stmText.setText("")

	def showText(self):
		# 100% easier by loading and unloading these procedurally thru a text file
		self.ctlText.setText("Press H for help menu.")
		self.stmText.setText("Stamina:")

	def hideCH(self):
		self.itcText.setText("")

	def showCH(self):
		self.itcText.setText("+")

# gametext instance
game_text = Text