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
import visualControl
import statsControl
import scanSimControl

def runControlLoops():

    timeScale = 1
    guiTimeScale = 0.5
    
    trackSpeedMin = 0.0016
    trackSpeedMax =   1
    
    odoSpeedMin = 0.0016
    odoSpeedMax =  1
    
    rcChanSpeedMin = 0.0016
    rcChanSpeedMax = 0.09
    
    vsimSpeedMin = 0.0016
    vsimSpeedMax = 0.06
    
    routeState  = routeControl.RouteState(120.0)        #RouteState(near)
    odoState    = odoControl.OdoState(0.3,32768,0,0,0, "fifo.tmp", 16000)    #OdoState(mmPerPulse,rolloverRange,rolloverCountL,rolloverCountR,initTheta, odoFilename, odoReadRate)
    rcChanState = rcChanControl.RcChanState(40, 80, "/dev/ttyS0")    #RcChanState(limitChange, speedLimit)
    trackState  = trackControl.TrackState(155,500)      #TrackState(trackWidth,movementBudget)
    vsimState   = vsimControl.VsimState(1.5,1.0,600.0) #VsimState(fricEffectPerSec,lrBias,speedMax)
    envSimState = envSimControl.EnvSimState()
    sensorState = sensorControl.SensorState(30,5)
    visualState = visualControl.VisualState()
    statsState = statsControl.StatsState()
    scanSimState = scanSimControl.ScanSimState(65, 10)        # scanSimState (scanRange, turnSpeed)
    
    routeController  = plumbing.controlloop.ControlLoop( routeState,  routeControl.routeControlUpdate,   0.20 * timeScale,  0.20 * timeScale)
    trackController  = plumbing.controlloop.ControlLoop( trackState,  trackControl.trackControlUpdate,   trackSpeedMin * timeScale,  trackSpeedMax * timeScale)
    odoController    = plumbing.controlloop.ControlLoop( odoState,    odoControl.realUpdate,              odoSpeedMin * timeScale,  odoSpeedMax * timeScale)
    rcChanController = plumbing.controlloop.ControlLoop( rcChanState, rcChanControl.realMotor,            rcChanSpeedMin * timeScale,  rcChanSpeedMax * timeScale)
    vsimController   = plumbing.controlloop.ControlLoop( vsimState,   vsimControl.vsimControlUpdate,     vsimSpeedMin * timeScale,  vsimSpeedMax * timeScale)
    envSimController = plumbing.controlloop.ControlLoop( envSimState, envSimControl.envSimControlUpdate, 0.06 * timeScale,  0.06 * timeScale)
    sensorController = plumbing.controlloop.ControlLoop( sensorState, sensorControl.sensorControlUpdate, 0.06 * timeScale,  0.06 * timeScale)
    visualController = plumbing.controlloop.ControlLoop( visualState, visualControl.visualControlUpdate, 0.06 * guiTimeScale,  0.16 * guiTimeScale)
    statsController  = plumbing.controlloop.ControlLoop( statsState,  statsControl.statsControlUpdate,   2.00 * timeScale,  2.00 * timeScale)
    scanSimController = plumbing.controlloop.ControlLoop( scanSimState, scanSimControl.scanSimControlUpdate, 0.09 * timeScale, 0.09 * timeScale)
    
    routeController.connectTo(trackController,  routeControl.routeToTrackTranslator)
    trackController.connectTo(rcChanController, trackControl.trackToRcChanTranslator)
    rcChanController.connectTo(vsimController, rcChanControl.rcChanToVsimTranslator)
    vsimController.connectTo(odoController, vsimControl.vsimToOdoTranslator)
    odoController.connectTo(trackController, odoControl.odoToTrackTranslator)
    #trackController.connectTo(routeController, trackControl.trackToRouteTranslator)
    #envSimController.connectTo(sensorController, envSimControl.envSimToSensorTranslator)
    sensorController.connectTo(trackController, sensorControl.sensorToTrackTranslator)
    envSimController.connectTo(visualController, envSimControl.envToVisualTranslator)
    #trackController.connectTo(visualController, trackControl.trackToVisualTranslator)
    visualController.connectTo(routeController, visualControl.visualToRouteTranslator)
    #routeController.connectTo(statsController, statsControl.toStatsTranslator)
    trackController.connectTo(statsController, statsControl.toStatsTranslator)
    
    statsController.connectTo(visualController, statsControl.statsToVisualTranslator)
    #trackController.connectTo(scanSimController, trackControl.trackToScanSimTranslator)
    envSimController.connectTo(scanSimController, envSimControl.envToScanSimControl)
    scanSimController.connectTo(visualController, scanSimControl.scanSimToVisualTranslator)
    scanSimController.connectTo(sensorController, scanSimControl.scanSimToSensorTranslator)
    rcChanController.connectTo(visualController, rcChanControl.rcChanToVsimTranslator)
    odoController.connectTo(visualController, odoControl.odoToVisualTranslator)
    
    visualController.connectTo(trackController, visualControl.visualToAppManager)       # application manager to pause loops
    visualController.connectTo(odoController, visualControl.visualToAppManager)
   # visualController.connectTo(rcChanController, visualControl.visualToAppManager)
   # visualController.connectTo(envSimController, visualControl.visualToAppManager)
   # visualController.connectTo(sensorController, visualControl.visualToAppManager)
   # visualController.connectTo(routeController, visualControl.visualToAppManager)
   # visualController.connectTo(scanSimController, visualControl.visualToAppManager)
   # visualController.connectTo(routeController, visualControl.visualToAppManager)
    
    routeController.start()
    trackController.start()
    rcChanController.start()
    vsimController.start()
    odoController.start()
    envSimController.start()
    sensorController.start()
    statsController.start()
    scanSimController.start()
    visualController.run()
 
if __name__ == '__main__':

   runControlLoops()
