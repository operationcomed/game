from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.LerpInterval import *
from direct.interval.IntervalGlobal import *

class Bars():
	def setBarVisibility(self, game, visible):
		anim = []
		game.barsVisible = visible
		for bar in game.bars:
			if (visible):
				try:
					anim.append(LerpColorScaleInterval(bar, 0.25, (1, 1, 1, 1), bar.getColorScale(), blendType='easeOut'))
				except:
					pass
			else:
				try:
					anim.append(LerpColorScaleInterval(bar, 0.25, (1, 1, 1, 0), bar.getColorScale(), blendType='easeOut'))
				except:
					pass
		fader = Parallel(*anim, name="fade")
		fader.start()

bs = Bars