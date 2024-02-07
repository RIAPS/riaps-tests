"""RIAPS Timer Port Tests
"""
import riaps_testing
import pytest
import riaps_fixtures_library.utils as utils

log_server_ip = utils.get_ip_address("riaps-VirtualBox.local")

@pytest.mark.parametrize('log_server', [{'server_ip': log_server_ip}], indirect=True)
def test_Timer():
    """
    Verify that test results match the expected behavior of the Timer ports
    """
    results = riaps_testing.runTest("Timer", "testTimer", "timer.riaps", "timer.depl")
    print(results)
    assert results != {}, "Logs are empty or not collected!"
    for key in results:
        assert len(results[key]) > 0, "no log entry captured for %s" % key
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
                        assert parts[2] == '1.0', "getPeriod() returned wrong value: %f" % float(parts[2])
                        if periodicTimerCounter > 3:
                            assert abs(currTime - lastTime -1.0) < 0.5, "Timer error greater than 0.5s"
                    elif periodicTimerCounter < 12:
                        assert parts[2] == '5.0', "getPeriod() returned wrong value(%f) or setPeriod() failed" % float(parts[2])
                        if periodicTimerCounter > 10:
                            assert abs(currTime - lastTime - 5.0) < 0.5, "Timer error greater than 0.5s"
                elif line.find("Halt") != -1:
                    timerRunning = False
                elif line.find("Launch") != -1:
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
                    sporadicTimerCounter += 1
                    parts = line.split(" ")
                    assert parts[1] == '0.5', "getDelay() returned wrong value (%f) or setDelay() failed" % float(parts[2])
                    assert parts[2] == '4.0', "getDelay() returned wrong value (%f) or setDelay() failed" % float(parts[2])
                    if sporadicTimerCounter < 13:
                        assert float(parts[3]) <= 4.0 + 0.5, "sporadic timer launch() call failed or ignored"
                elif line.find("Sporadic") != -1:
                    parts = line.split(" ")
                    assert float(parts[2]) > 4 - 0.5, "sporadic timer cancel() call failed or ignored"
                elif line.find("Halt") != -1:
                    timerRunning = False
                elif line.find("Launch") != -1:
                    timerRunning = True
