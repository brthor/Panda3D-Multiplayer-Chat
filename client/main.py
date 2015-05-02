import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from pandac.PandaModules import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator 
from direct.actor.Actor import Actor
from client import *
from MapObjects import *
import sys

#Just some groundwork

base.disableMouse()
base.camera.setPos(0,0,10)
#establish connection > send/receive updates > update world
worldClient = Client(9099,"192.168.2.13")
Terrain = Terrain()
N = PlayerReg()
me = Me(Terrain)
keys = Keys()
w = World()
chatReg = chatRegulator(worldClient,keys)

taskMgr.add(N.updatePlayers,"keep every player where they are supposed to be",extraArgs = [me])
taskMgr.add(me.move,"move our penguin", extraArgs = [keys,Terrain])
taskMgr.add(worldClient.tskReaderPolling,"Poll the connection reader",extraArgs = [me,N,chatReg])
taskMgr.add(w.UpdateWorld,"keep the world up to date",extraArgs = [me,worldClient])

#=============================================================================#
#test code for lighting, normal mapping, etc...#
#ambient light
alight = AmbientLight('alight')
alight.setColor(Vec4(0.2, 0.2, 0.2, 1))
alnp = render.attachNewNode(alight)
render.setLight(alnp)
me.model.setShaderAuto()
#me.model.setNormalMap("models/nskinrd-normal.jpg")


lightpivot = render.attachNewNode("lightpivot")
lightpivot.setPos(0,0,25)
plight = PointLight('plight')
plight.setColor(Vec4(1, 1, 1, 1))
plnp = lightpivot.attachNewNode(plight)
render.setLight(plnp)
me.model.setShaderInput("light", plnp)
#=============================================================================#
#Castle = Castle(Vec3(288.96,294.45,30.17), Vec3(119.05,270,0),0.08)
run()

