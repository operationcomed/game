from direct.gui.OnscreenImage import OnscreenImage

class HelpMenu():
	helpDisplay = False
	def helpMenu(self, game):
		self.helpDisplay = not self.helpDisplay
		if (self.helpDisplay):
			game.helpMenuImg = OnscreenImage(image='assets/media/helpMenu.png', scale=(16/9, 1, 1))
			game.helpMenuImg.setTransparency(True)
			game.textNodePath.hide()
		else:
			game.helpMenuImg.destroy()
			game.textNodePath.show()

hm = HelpMenu