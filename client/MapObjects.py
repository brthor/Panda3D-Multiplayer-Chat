from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

class Castle(DirectObject):
	def __init__(self, pos,hpr,sc):
		self.model = loader.loadModel("models/castle")
		self.model.setPos(pos.getX(),pos.getY(),pos.getZ())
		self.model.setHpr(hpr.getX(),hpr.getY(),hpr.getZ())
		self.model.setScale(sc)
		self.model.reparentTo(render)