from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *

class Bars():
	def setBarVisibility(self, game, visible):
		anim = []
		for bar in game.bars:
			if (visible):
				anim.append(LerpColorScaleInterval(bar, 0.25, (1, 1, 1, 1), bar.getColorScale()))
			else:
				anim.append(LerpColorScaleInterval(bar, 0.25, (1, 1, 1, 0), bar.getColorScale()))
		fader = Parallel(*anim, name="fade")
		fader.start()

bs = Bars