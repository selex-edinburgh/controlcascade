import time
import plumbing.controlloop
import routeControl


def testRouteControl():

    routeController = plumbing.controlloop.ControlLoop( routeControl.routeState, routeControl.routeControlUpdate, 1.0, 1.1)

    ### test environment
    testRouteObsTr = plumbing.controlloop.ControlObserverTranslator(routeController, routeControl.testRouteObsTranStub) 
    routeControl.routeState.attach(testRouteObsTr)
    ### test environment

    routeController.start()



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
