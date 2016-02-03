import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class ScanSimState(ObservableState):
    def __init__(self):
        
        
        
def scanSimControlUpdate(state, batchdata):
    for item in batchdata:
        if item['messageType'] == 'control':
            pass
            
        elif item['messageType'] == 'sense':
            #TODO
            pass
            
    if len(batchdata) == 0: return
    
    
def scanSimToSensorTranslator( sourceState, destState, destQueue):
    message = {'messageType':'sense','sensedPos'sourceState.polePos}
    destQueue.put(message)
