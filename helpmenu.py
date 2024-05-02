from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.LerpInterval import *

class HelpMenu():
	helpDisplay = False
	def helpMenu(self, game):
		self.helpDisplay = not self.helpDisplay
		game.helpDisplay = self.helpDisplay
		self.popout = LerpFunc(self.fadeOut,
            extraArgs=[self, game],
            fromData=1,
            toData=0,
            duration=0.25,
			blendType='easeIn',
            name="fadeo")
		if (self.helpDisplay and not self.popout.isPlaying()):
			game.helpMenuImg = OnscreenImage(image='assets/media/helpMenu.png', scale=(16/9, 1, 1))
			game.helpMenuImg.setTransparency(True)
			popup = LerpFunc(self.fadeIn,
        	    extraArgs=[self, game],
        	    fromData=0,
        	    toData=1,
        	    duration=0.25,
				blendType='easeOut',
        	    name="fadei")
			popup.start()
		elif (not self.popout.isPlaying()):
			self.popout.start()

	def fadeIn(t, self, game):
		game.textNodePath.setColorScale(1, 1, 1, min(1-t, 1))
		game.helpMenuImg.setColorScale(1, 1, 1, t)
		game.helpMenuImg.setScale(min(16/9*t, 16/9), min(t, 1), min(t, 1))

	def fadeOut(t, self, game):
		game.textNodePath.setColorScale(1, 1, 1, max(1-t, 0))
		game.helpMenuImg.setColorScale(1, 1, 1, t)
		game.helpMenuImg.setScale(min(16/9*t, 16/9), min(t, 1), min(t, 1))
		

hm = HelpMenu