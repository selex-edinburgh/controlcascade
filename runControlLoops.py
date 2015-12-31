import time
import math
import plumbing.controlloop

import routeControl
import trackControl
import odoControl
import rcChanControl
import vsimControl

def runControlLoops(uiObserver):

    timeScale = 1.0
    
    routeController = plumbing.controlloop.ControlLoop( routeControl.routeState, routeControl.routeControlUpdate,       0.2 * timeScale,    0.2 * timeScale)
    trackController = plumbing.controlloop.ControlLoop( trackControl.trackState, trackControl.trackControlUpdate,       0.03  * timeScale,  0.03 * timeScale)
    odoController = plumbing.controlloop.ControlLoop( odoControl.odoState, odoControl.odoControlUpdate,                 0.06 * timeScale,   3.0 * timeScale)
    rcChanController = plumbing.controlloop.ControlLoop( rcChanControl.rcChanState, rcChanControl.rcChanControlUpdate,  0.06 * timeScale,   0.06 * timeScale)
    vsimController = plumbing.controlloop.ControlLoop( vsimControl.vsimState, vsimControl.vsimControlUpdate,            0.06 * timeScale,   0.06 * timeScale)

    routeTrackObsTr = plumbing.controlloop.ControlObserverTranslator(trackController, routeControl.routeToTrackTranslator)
    routeControl.routeState.attach(routeTrackObsTr)
    trackRcChanObsTr = plumbing.controlloop.ControlObserverTranslator(rcChanController, trackControl.trackToRcChanTranslator)
    trackControl.trackState.attach(trackRcChanObsTr)
    rcChanVsimObsTr = plumbing.controlloop.ControlObserverTranslator(vsimController, rcChanControl.rcChanToVsimTranslator)
    rcChanControl.rcChanState.attach(rcChanVsimObsTr)
    vsimOdoObsTr = plumbing.controlloop.ControlObserverTranslator(odoController, vsimControl.vsimToOdoTranslator)
    vsimControl.vsimState.attach(vsimOdoObsTr)
    odoTrackObsTr = plumbing.controlloop.ControlObserverTranslator(trackController, odoControl.odoToTrackTranslator)
    odoControl.odoState.attach(odoTrackObsTr)
    trackRouteObsTr = plumbing.controlloop.ControlObserverTranslator(routeController, trackControl.trackToRouteTranslator)
    trackControl.trackState.attach(trackRouteObsTr)
    
    
    if uiObserver != None: trackControl.trackState.attach(uiObserver)

    vsimController.start()
    rcChanController.start()
    odoController.start()
    trackController.start()
    routeController.start()
    
if __name__ == '__main__':

   runControlLoops(None)
