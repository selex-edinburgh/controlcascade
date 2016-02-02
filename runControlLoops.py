import time
import math
import plumbing.controlloop

import routeControl
import trackControl
import odoControl
import rcChanControl
import vsimControl
import envSimControl
import sensorControl

def runControlLoops(uiObserver, guiObserver):

    timeScale = 1.0
    
    routeState  = routeControl.RouteState(120.0)        #RouteState(near)
    odoState    = odoControl.OdoState(0.1,32768,0,0,0)    #OdoState(mmPerPulse,rolloverRange,rolloverCountL,rolloverCountR,initTheta)
    rcChanState = rcChanControl.RcChanState(60, 120)    #RcChanState(limitChange, speedLimit)
    trackState  = trackControl.TrackState(310,500)      #TrackState(trackWidth,movementBudget)
    vsimState   = vsimControl.VsimState(0.95,1.0,600.0) #VsimState(fricEffectPerSec,lrBias,speedMax)
    envSimState = envSimControl.EnvSimState()
    sensorState = sensorControl.SensorState(30,5)
    
    routeController  = plumbing.controlloop.ControlLoop( routeState,  routeControl.routeControlUpdate,   0.2  * timeScale,  0.2  * timeScale)
    trackController  = plumbing.controlloop.ControlLoop( trackState,  trackControl.trackControlUpdate,   0.03 * timeScale,  0.03 * timeScale)
    odoController    = plumbing.controlloop.ControlLoop( odoState,    odoControl.odoControlUpdate,       0.06 * timeScale,  3.0  * timeScale)
    rcChanController = plumbing.controlloop.ControlLoop( rcChanState, rcChanControl.rcChanControlUpdate, 0.06 * timeScale,  0.06 * timeScale)
    vsimController   = plumbing.controlloop.ControlLoop( vsimState,   vsimControl.vsimControlUpdate,     0.06 * timeScale,  0.06 * timeScale)
    envSimController = plumbing.controlloop.ControlLoop( envSimState, envSimControl.envSimControlUpdate, 0.06 * timeScale, 0.06 * timeScale)
    sensorController = plumbing.controlloop.ControlLoop( sensorState, sensorControl.sensorControlUpdate, 0.06 * timeScale, 0.06 * timeScale)
    
    routeController.connectTo(trackController,  routeControl.routeToTrackTranslator)
    trackController.connectTo(rcChanController, trackControl.trackToRcChanTranslator)
    rcChanController.connectTo(vsimController, rcChanControl.rcChanToVsimTranslator)
    vsimController.connectTo(odoController, vsimControl.vsimToOdoTranslator)
    odoController.connectTo(trackController, odoControl.odoToTrackTranslator)
    trackController.connectTo(routeController, trackControl.trackToRouteTranslator)
    envSimController.connectTo(sensorController, envSimControl.envSimToSensorTranslator)
    sensorController.connectTo(trackController, sensorControl.sensorToTrackTranslator)
    
    if uiObserver != None: 
        trackState.attach(uiObserver)
    if guiObserver != None:
        envSimState.attach(guiObserver)
    
    routeController.start()
    trackController.start()
    rcChanController.start()
    vsimController.start()
    odoController.start()
    envSimController.start()
    sensorController.start()
    
if __name__ == '__main__':

   runControlLoops(None)
