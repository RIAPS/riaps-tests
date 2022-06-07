"""RIAPS Timer Port Tests
"""
import riaps_testing

def test_Timer():
    """
    Verify that test results match the expected behavior of the Timer ports
    """
    results = riaps_testing.runTest("Timer", "testTimer", "timer.riaps", "timer.depl")
    print(results)
    assert results != {}, "Logs are empty or not collected!"
    for key in results:
        if key.find("CompTimerPer") != -1:
            assert results[key][0].find("Starting") != -1, "First line of %s isn't starting!" % key
            assert results[key][-1].find("Stopping") != -1, "Last line of %s isn't stopping!" % key
            periodicTimerCounter = 0
            timerRunning = True
            lastTime = 0.0
            currTime = 0.0
            for line in results[key]:
                if line.find("Periodic") != -1:
                    assert timerRunning, "Periodic timer fired while halted!"
                    periodicTimerCounter += 1
                    parts = line.split(" ")
                    lastTime = currTime
                    currTime = float(parts[1])
                    if periodicTimerCounter < 10:
                        assert parts[2] == '1.0', "getPeriod() returned wrong value: %d" % int(parts[2])
                        if periodicTimerCounter > 3:
                            assert abs(currTime - lastTime -1.0) < 0.5, "Timer error greater than 0.5s"
                    if periodicTimerCounter < 12:
                        assert parts[2] == '5.0', "getPeriod() returned wrong value(%d) or setPeriod() failed" % int(parts[2])
                        if periodicTimerCounter > 10:
                            assert abs(currTime - lastTime - 5.0) < 0.5, "Timer error greater than 0.5s"
                elif line.find("Halt"):
                    timerRunning = False
                elif line.find("Launch"):
                    timerRunning = True
        elif key.find("CompTimerSpor") != -1:
            assert results[key][0].find("Starting") != -1, "First line of %s isn't starting!" % key
            assert results[key][-1].find("Stopping") != -1, "Last line of %s isn't stopping!" % key
            sporadicTimerCounter = 0
            timerRunning = True
            lastTime = 0.0
            currTime = 0.0
            for line in results[key]:
                if line.find("Ticker") != -1:
                    assert timerRunning, "Sporadic timer fired while halted!"
                    # sporadicTimerCounter += 1
                    parts = line.split(" ")
                    # if sporadicTimerCounter < 12:
                    assert parts[1] == '0.5', "getDelay() returned wrong value (%d) or setDelay() failed" % int(parts[2])
                    assert parts[2] == '4.0', "getDelay() returned wrong value (%d) or setDelay() failed" % int(parts[2])
                    assert float(parts[3]) <= 4.0 + 0.5, "sporadic timer launch() call failed or ignored"
                elif line.find("Sporadic") != -1:
                    parts = line.split(" ")
                    assert float(parts[2]) > 4 - 0.5, "sporadic timer cancel() call failed or ignored"
                elif line.find("Halt"):
                    timerRunning = False
                elif line.find("Launch"):
                    timerRunning = True
