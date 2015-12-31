import time
import plumbing.controlloop
import routeControl


def testRouteControl():

    routeController = plumbing.controlloop.ControlLoop( routeControl.routeState, routeControl.routeControlUpdate, 1.0, 1.1)
    print "t1"
    ### test environment
    print "t2"
    testRouteObsTr = plumbing.controlloop.ControlObserverTranslator(routeController, routeControl.testRouteObsTranStub) 
    print "t3"
    routeControl.routeState.attach(testRouteObsTr)
    ### test environment
    print "t4"

    routeController.start()
    print "t5"
    #raw_input("Press enter to exit")


import trackControl
def testRouteTrackControl(uiObserver):

    routeController = plumbing.controlloop.ControlLoop( routeControl.routeState, routeControl.routeControlUpdate, 0.5, 0.5)
    trackController = plumbing.controlloop.ControlLoop( trackControl.trackState, trackControl.trackControlUpdate, 0.1, 0.1)
    routeTrackObsTr = plumbing.controlloop.ControlObserverTranslator(trackController, routeControl.routeToTrackTranslator)
    trackRouteObsTr = plumbing.controlloop.ControlObserverTranslator(routeController, trackControl.trackToRouteTranslator)
    routeControl.routeState.attach(routeTrackObsTr)
    trackControl.trackState.attach(trackRouteObsTr)

    ### test environment
    testTrackObsTr = plumbing.controlloop.ControlObserverTranslator(trackController, trackControl.testTrackObsTranStub)
    trackControl.trackState.attach(testTrackObsTr)
    ### test environment
    if uiObserver != None: trackControl.trackState.attach(uiObserver)
    
    trackController.start()
    routeController.start()
    
import odoControl
def testRouteTrackOdoControl(uiObserver):

    routeController = plumbing.controlloop.ControlLoop( routeControl.routeState, routeControl.routeControlUpdate, 0.5, 0.5)
    trackController = plumbing.controlloop.ControlLoop( trackControl.trackState, trackControl.trackControlUpdate, 0.1, 0.1)
    odoController = plumbing.controlloop.ControlLoop( odoControl.odoState, odoControl.odoControlUpdate, 0.05, 0.05)
    routeTrackObsTr = plumbing.controlloop.ControlObserverTranslator(trackController, routeControl.routeToTrackTranslator)
    trackRouteObsTr = plumbing.controlloop.ControlObserverTranslator(routeController, trackControl.trackToRouteTranslator)
    odoTrackObsTr = plumbing.controlloop.ControlObserverTranslator(trackController, odoControl.odoToTrackTranslator)
    routeControl.routeState.attach(routeTrackObsTr)
    trackControl.trackState.attach(trackRouteObsTr)
    odoControl.odoState.attach(odoTrackObsTr)

    ### test environment
    testOdoObsTr = plumbing.controlloop.ControlObserverTranslator(odoController, odoControl.testOdoObsTranStub)
    odoControl.odoState.attach(testOdoObsTr)
    ### test environment
    if uiObserver != None: trackControl.trackState.attach(uiObserver)
    
    trackController.start()
    routeController.start()
    odoController.start()



import rcChanControl
import vsimControl
import math
def testControlLoops(uiObserver):

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
   # testRouteControl()
   # testRouteTrackControl(None)
   # testRouteTrackOdoControl(None)
   testControlLoops(None)
