from direct.showbase.ShowBase import ShowBase
from direct.showbase import Audio3DManager
from math import pi, sin, cos
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from direct.gui.OnscreenText import OnscreenText
from direct.filter.CommonFilters import CommonFilters
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import *
from direct.gui.DirectGui import *
from panda3d.physics import ActorNode, ForceNode, LinearVectorForce, PhysicsCollisionHandler
import time
import gametext

KB_BUTTON = KeyboardButton.ascii_key
KB = KeyboardButton

class Level0():
	def backstory(self, game, task):
		game.staminaBar.hide()
		if (not game.isPlaying):
			gametext.Text.hideCH(game.game_text)
			game.speedStop = True
			game.music.stop()
			game.playVid(game.backstoryVideo)

		button_down = game.mouseWatcherNode.is_button_down

		if (task.time >= 47 or button_down(KB_BUTTON('e'))):
			game.music.play()
			game.video.removeNode()
			gametext.Text.showCH(game.game_text)
			game.speedStop = False
			game.skipText.setText("")
			game.blackBg.destroy()
			game.sound.stop()
			game.staminaBar.show()
			game.isPlaying = False
			return Task.done
		
		return Task.cont

l0 = Level0