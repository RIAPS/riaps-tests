import riaps_testing

def test_LimitNetwork():
    """Test RIAPS Network limit handler
    """
    results = riaps_testing.runTest("test_LimitNetwork", "testLimitNetwork", "netlimit.riaps", "netlimit.depl")
    assert len(results) != 0, "Failed to retrieve any logs!"
    for key in results.keys():
        log = results[key]
        assert log[0].find("Starting") != -1, "First line of %s isn't starting!" % key
        assert log[-1].find("Stopping") != -1, "Last line of %s isn't stopping!" % key

        numLimit = 0
        numTick = 0

        for line in log:
            if line.find("Starting") == -1 and line.find("Stopping") == -1:
                if line.find("Tick") != -1:
                    numTick += 1
                if line.find("Limit") != -1 and numTick != 0: # Check if a tick has occurred to ignore startup process
                    if numLimit == 0: # Reset numTick on first hit of limit
                        numTick = 6
                    numLimit += 1

        assert numLimit != 0, "Failed to ever hit limit!"
        
        # The ratio should be approximately 6.0 because the limit is 1.2KB/s and
        # the message size is increased by 256MB every second
        ratio = numTick*1.0/numLimit
        print("numTick=%d numLimit=%d ratio=%.2f" % (numTick, numLimit, ratio))
        assert ratio > 4.5, "Hit limit too frequently: Ratio=%.2f" % ratio
        assert ratio < 7.5, "Hit limit too infrequently: Ratio=%.2f" % ratio
