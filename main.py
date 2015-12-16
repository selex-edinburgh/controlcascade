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
def testRouteTrackControl():

    routeController = plumbing.controlloop.ControlLoop( routeControl.routeState, routeControl.routeControlUpdate, 1.0, 1.1)
    trackController = plumbing.controlloop.ControlLoop( trackControl.trackState, trackControl.trackControlUpdate, 0.1, 0.11)
    routeTrackObsTr = plumbing.controlloop.ControlObserverTranslator(trackController, routeControl.routeToTrackTranslator)
    trackRouteObsTr = plumbing.controlloop.ControlObserverTranslator(routeController, trackControl.trackToRouteTranslator)
    routeControl.routeState.attach(routeTrackObsTr)
    trackControl.trackState.attach(trackRouteObsTr)

    ### test environment
    testTrackObsTr = plumbing.controlloop.ControlObserverTranslator(trackController, trackControl.testTrackObsTranStub)
    trackControl.trackState.attach(testTrackObsTr)
    ### test environment
    
    trackController.start()
    routeController.start()
    



if __name__ == '__main__':
   # testRouteControl()
    testRouteTrackControl()
