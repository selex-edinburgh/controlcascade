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

    trackUpdateRateMin = 0.016
    trackUpdateRateMax =   1

    odoUpdateRateMin = 0.016
    odoUpdateRateMax =  1

    rcChanUpdateRateMin = 0.016
    rcChanUpdateRateMax = 0.09

    vsimUpdateRateMin = 0.016
    vsimUpdateRateMax = 0.06

    '''
    Explaination of the next block
    Green block
    '''
    routeState  = routeControl.RouteState(120.0)        #RouteState(near)
    odoState    = odoControl.OdoState()    #OdoState(mmPerPulse,initTheta)
    rcChanState = rcChanControl.RcChanState(40, 40, 0.4)    #RcChanState(lrChange, fwdbkChange, speedScaling)
    trackState  = trackControl.TrackState(200,237,500)      #TrackState(wheelBase,trackWidth,movementBudget)
    vsimState   = vsimControl.VsimState(1.5,1.0,600.0) #VsimState(fricEffectPerSec,lrBias,speedMax)
    envSimState = envSimControl.EnvSimState()
    sensorState = sensorControl.SensorState(30,5)
    visualState = visualControl.VisualState()
    statsState = statsControl.StatsState()
    scanSimState  = scanSimControl.ScanSimState('IR', 0,  45,  0, 45, 65, 10)  # scanSimState (sensorID, pointAOffset, frontConeWidth, frontLineWidth,  scanAngle, scanRange, turnSpeed)
    scanSimState2 = scanSimControl.ScanSimState('US', 0, 202, 180, 21, 65, 10)  # scanSimState (sensorID, pointAOffset,  backConeWidth,  backLineWidth, scanAngle, scanRange, turnSpeed)

    '''
    Explaination of next block
    Amber block
    '''
    routeController  = plumbing.controlloop.ControlLoop( routeState,  routeControl.routeControlUpdate,   0.20 * timeScale,  0.20 * timeScale)
    trackController  = plumbing.controlloop.ControlLoop( trackState,  trackControl.trackControlUpdate,   trackUpdateRateMin * timeScale,  trackUpdateRateMax * timeScale)
    odoController    = plumbing.controlloop.ControlLoop( odoState,    odoControl.simUpdate,              odoUpdateRateMin * timeScale,  odoUpdateRateMax * timeScale)
    rcChanController = plumbing.controlloop.ControlLoop( rcChanState, rcChanControl.simMotor,            rcChanUpdateRateMin * timeScale,  rcChanUpdateRateMax * timeScale)
#    odoController    = plumbing.controlloop.ControlLoop( odoState,    odoControl.realUpdate,              odoUpdateRateMin * timeScale,  odoUpdateRateMax * timeScale)
#    rcChanController = plumbing.controlloop.ControlLoop( rcChanState, rcChanControl.realMotor,            rcChanUpdateRateMin * timeScale,  rcChanUpdateRateMax * timeScale)
    vsimController   = plumbing.controlloop.ControlLoop( vsimState,   vsimControl.vsimControlUpdate,     vsimUpdateRateMin * timeScale,  vsimUpdateRateMax * timeScale)
    envSimController = plumbing.controlloop.ControlLoop( envSimState, envSimControl.envSimControlUpdate, 0.06 * timeScale,  0.06 * timeScale)
    sensorController = plumbing.controlloop.ControlLoop( sensorState, sensorControl.sensorControlUpdate, 0.06 * timeScale,  0.06 * timeScale)
    visualController = plumbing.controlloop.ControlLoop( visualState, visualControl.visualControlUpdate, 0.06 * guiTimeScale,  0.16 * guiTimeScale)
    statsController  = plumbing.controlloop.ControlLoop( statsState,  statsControl.statsControlUpdate,   0.5 * timeScale,  0.5 * timeScale)
    scanSimController = plumbing.controlloop.ControlLoop( scanSimState, scanSimControl.scanSimControlUpdate, 0.09 * timeScale, 0.09 * timeScale)
    scanSimController2 = plumbing.controlloop.ControlLoop( scanSimState2, scanSimControl.scanSimControlUpdate, 0.09 * timeScale, 0.09 * timeScale)

    '''
    Explaination of next block
    Green block
    '''
    routeController.connectTo(trackController,  routeControl.routeToTrackTranslator)
    trackController.connectTo(rcChanController, trackControl.trackToRcChanTranslator)
    rcChanController.connectTo(vsimController, rcChanControl.rcChanToVsimTranslator)
    vsimController.connectTo(odoController, vsimControl.vsimToOdoTranslator)
    odoController.connectTo(trackController, odoControl.odoToTrackTranslator)
    trackController.connectTo(routeController, trackControl.trackToRouteTranslator)
    #envSimController.connectTo(sensorController, envSimControl.envSimToSensorTranslator)
    sensorController.connectTo(trackController, sensorControl.sensorToTrackTranslator)
    envSimController.connectTo(visualController, envSimControl.envToVisualTranslator)
    trackController.connectTo(visualController, trackControl.trackToVisualTranslator)
    visualController.connectTo(routeController, visualControl.visualToRouteTranslator)
    #routeController.connectTo(statsController, statsControl.toStatsTranslator)
    trackController.connectTo(statsController, statsControl.toStatsTranslator)

    statsController.connectTo(visualController, statsControl.statsToVisualTranslator)
    trackController.connectTo(scanSimController, trackControl.trackToScanSimTranslator)
    envSimController.connectTo(scanSimController, envSimControl.envToScanSimControl)
    scanSimController.connectTo(visualController, scanSimControl.scanSimToVisualTranslator)
    #scanSimController.connectTo(sensorController, scanSimControl.scanSimToSensorTranslator)
    trackController.connectTo(scanSimController2, trackControl.trackToScanSimTranslator)
    envSimController.connectTo(scanSimController2, envSimControl.envToScanSimControl)
    scanSimController2.connectTo(visualController, scanSimControl.scanSimToVisualTranslator)
    #scanSimController2.connectTo(sensorController, scanSimControl.scanSimToSensorTranslator)
    rcChanController.connectTo(visualController, rcChanControl.rcChanToVsimTranslator)
    odoController.connectTo(visualController, odoControl.odoToVisualTranslator)

    
    visualController.connectTo(trackController, visualControl.visualToAppManager)       # application manager to stop loops
    visualController.connectTo(odoController, visualControl.visualToAppManager)
    #visualController.connectTo(statsController, visualControl.visualToAppManager)
    #visualController.connectTo(rcChanController, visualControl.visualToAppManager)
    #visualController.connectTo(envSimController, visualControl.visualToAppManager)
    #visualController.connectTo(sensorController, visualControl.visualToAppManager)
    #visualController.connectTo(routeController, visualControl.visualToAppManager)
    #visualController.connectTo(scanSimController, visualControl.visualToAppManager)
    #visualController.connectTo(scanSimController2, visualControl.visualToAppManager)
    #visualController.connectTo(routeController, visualControl.visualToAppManager)

    '''
    sets going the loops for all the different controllers
    Green block
    '''
    routeController.start()
    trackController.start()
    rcChanController.start()
    vsimController.start()
    odoController.start()
    envSimController.start()
    sensorController.start()
    statsController.start()
    scanSimController.start()
    scanSimController2.start()
    visualController.run()


if __name__ == '__main__':

   runControlLoops()
