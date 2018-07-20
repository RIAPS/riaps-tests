import riaps_testing

def test_LimitCPU():
    """Test RIAPS CPU limit handler
    """
    results = riaps_testing.runTest("test_LimitCPU", "testLimitCPU", "cpulimit.riaps", "cpulimit.depl")
    for key in results.keys():
        log = results[key]
        assert log[0].find("Starting") != -1, "First line of %s isn't starting!" % key
        assert log[-1].find("Stopping") != -1, "Last line of %s isn't stopping!" % key

        numLimit = 0
        numTick = 0

        for line in log:
            if line.find("Tick") != -1:
                numTick += 1
            if line.find("Limit") != -1 and numTick != 0: # Check if a tick has occurred to ignore startup process
                if numLimit == 0: # Reset numTick on first hit of limit
                    numTick = 5
                numLimit += 1

        assert numLimit != 0, "Failed to ever hit limit!"
        
        # The ratio should be approximately 5.0 because the limit is decreased by 5000
        #   each time the Limit is hit and the limit is increased by 1000 each tick
        ratio = numTick*1.0/numLimit
        assert ratio > 3.5, "Hit limit too frequently: Ratio=%.2f" % ratio
        assert ratio < 6.5, "Hit limit too infrequently: Ratio=%.2f" % ratio