import riaps_testing

def test_LimitMemory():
    """Test RIAPS Memory limit handler
    """
    results = riaps_testing.runTest("test_LimitMemory", "testLimitMemory", "memlimit.riaps", "memlimit.depl")
    assert len(results) != 0, "Failed to retrieve any logs!"
    for key in results.keys():
        log = results[key]
        assert log[0].find("Starting") != -1, "First line of %s isn't starting!" % key
        assert log[-1].find("Stopping") != -1, "Last line of %s isn't stopping!" % key

        numTick = 0
        numLimit = 0
        curTick = 0

        for line in log:
            if line.find("Tick") != -1:
                curTick += 1
            elif line.find("Limit") != -1:
                if numLimit == 0:
                    curTick = 5 # Ignore startup time
                numLimit += 1
                numTick += curTick
                curTick = 0
        
        assert numLimit != 0, "Failed to ever hit limit!"

        # The ratio should be very close to 5.0 because the memory usage is increased by
        #   35MB each tick and the memory limit is 200MB
        ratio = numTick*1.0/numLimit
        assert ratio > 4.5, "Hit limit too frequently: Ratio=%.2f" % ratio
        assert ratio < 5.5, "Hit limit too infrequently: Ratio=%.2f" % ratio