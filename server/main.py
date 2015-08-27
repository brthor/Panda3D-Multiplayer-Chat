#dont open the render window
from pandac.PandaModules import * 
ConfigVariableString("window-type","none").setValue("none")

from direct.showbase import ShowBase
from direct.task.Task import Task
from pandac.PandaModules import *
from direct.distributed.PyDatagram import PyDatagram

from direct.showbase.DirectObject import DirectObject
from Server import *
import sys 
ShowBase.ShowBase() 

#TODO: Make it so when a player disconnects he is removed from the game

#receive connection > create Player > send Player initializing info > receive updates from Player and adjust data accordingly > send update to all Players(all positions)

#Create the server
worldServer = Server(9099,1000)

Active = PlayerReg()

taskMgr.add(worldServer.tskListenerPolling,"Poll the connection listener",extraArgs = [Active])
taskMgr.add(worldServer.tskReaderPolling,"Poll the connection reader",extraArgs = [Active])
taskMgr.add(Active.updatePlayers,"Update Every Player",extraArgs = [worldServer,None,"positions"])

#print "successful"
run()
