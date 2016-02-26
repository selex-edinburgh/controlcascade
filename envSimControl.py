import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class EnvSimState(ObservableState):
    def __init__(self):
        super(EnvSimState,self).__init__()
        self.poleList = [(130,60),(150,60),(170,60),(310,60),(330,60),
                        (350,60),(190,150),(210,150),(230,150),(250,150),(270,150),
                        (290,150),(130,240),(150,240),(170,240),(310,240),
                        (330,240),(350,240),(190,330),(210,330),(230,330),
                        (250,330),(270,330),(290,330),(140,615),(340,615)]
        self.wallList = [ 
            (120,0, 120,240), (120,240, 0,240), 
            (0,240, 0,720), (0,720, 480,720),
            (480,720, 480,240), (480,240, 360,240), 
            (360,240, 360,0), (360,0, 120,0)]
        self.barrelList = []
        self.rampList = []
        self.doorList = []
        self.goalList = []
        self.ballList = []
        
def envSimControlUpdate(state, batchdata):

    for item in batchdata:
        if item['messageType'] == 'control':
            pass
            
        elif item['messageType'] == 'sense':

            pass
  
    if len(batchdata) == 0: return
    
    
def envSimToSensorTranslator(sourceState, destState, destQueue):
    message = {'messageType':'sense',
               'sensedPole':sourceState.poleList,
               'sensedWall':sourceState.wallList}
    destQueue.put(message)
    
def envToVisualTranslator(sourceState, destState, destQueue):
    message = {'messageType':'obstacle',
               'poleList':sourceState.poleList,
               'wallList':sourceState.wallList,
               'barrelList':sourceState.barrelList,
               'rampList':sourceState.rampList,
               'doorList':sourceState.doorList,
               'goalList':sourceState.goalList,
               'ballList':sourceState.ballList}
    destQueue.put(message)
    
def envToScanSimControl(sourceState, destState, destQueue):
    message = {'messageType': 'obstacle',
                'poleList': sourceState.poleList}
    destQueue.put(message)