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
    
if __name__ == '__main__':
   # testRouteControl()
   # testRouteTrackControl(None)
    testRouteTrackOdoControl(None)
