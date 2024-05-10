from panda3d.core import *
from panda3d.core import ColorScaleAttrib
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *

class Text():

	ctlText = TextNode('controls')
	ctlText.setText("Press H for help menu.")
	ctlText.setShadow(0.15, 0.15)

	stmText = TextNode('controls')
	stmText.setText("Stamina:")
	stmText.setShadow(0.15, 0.15)

	hltText = TextNode('controls')
	hltText.setText("Health:")
	hltText.setShadow(0.15, 0.15)

	itmText = TextNode('items')
	itmText.setText("Items obtained:")
	itmText.setShadow(0.15, 0.15)
	itmText.setAlign(TextNode.ARight)

	itcText = TextNode('interact')
	itcText.setText("+")
	itcText.setShadow(0.07, 0.07)

	text_list = [ctlText, stmText, itmText, hltText] 

	def hideText(self, game):
		hide = []
		for node in game.textObjects:
			try:
				hide.append(LerpColorScaleInterval(node, 0.25, (1, 1, 1, 0), node.getColorScale(), blendType='easeOut'))
			except:
				print("oh")
		fader = Parallel(*hide, name='fader')
		fader.start()

	def showText(self, game):
		show = []
		for node in game.textObjects:
			try:
				show.append(LerpColorScaleInterval(node, 0.25, (1, 1, 1, 1), node.getColorScale(), blendType='easeOut'))
			except:
				print("oh")
		fader = Parallel(*show, name='fader')
		fader.start()

	def hideCH(self):
		self.itcText.setText("")

	def showCH(self):
		self.itcText.setText("+")

# gametext instance
game_text = Text