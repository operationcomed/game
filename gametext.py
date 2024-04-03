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

	text_list = [ctlText, stmText, itmText] 


	def hideText(self):
		for node in self.text_list:
			node.setTextColor(1, 1, 1, 0)
			node.setShadowColor(0, 0, 0, 0)

	def showText(self):
		for node in self.text_list:
			node.setTextColor(1, 1, 1, 1)
			node.setShadowColor(0, 0, 0, 1)

	def hideCH(self):
		self.itcText.setText("")

	def showCH(self):
		self.itcText.setText("+")

# gametext instance
game_text = Text