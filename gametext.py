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
			node.hide()
			hide.append(LerpFunc(self.fade,
        	    extraArgs=[node],
        	    fromData=node.getColorScale()[3],
        	    toData=0,
        	    duration=0.25,
				blendType='easeOut',
        	    name="fadeo"))
		fader = Parallel(*hide, name='fader')
		fader.start()

	def showText(self, game):
		#show = []
		for node in game.textObjects:
			node.show()
			node.setColorScale(1,1,1,1)
			#show.append(LerpFunc(self.fade,
        	#    extraArgs=[node],
        	#    fromData=node.getColorScale()[3],
        	#    toData=1,
        	#    duration=0.25,
			#	blendType='easeOut',
        	#    name="fadei"))
		#fader = Parallel(*show, name='fader')
		#fader.start()

	def fade(t, node):
		node.setColorScale(1, 1, 1, t)

	def hideCH(self):
		self.itcText.setText("")

	def showCH(self):
		self.itcText.setText("+")

# gametext instance
game_text = Text