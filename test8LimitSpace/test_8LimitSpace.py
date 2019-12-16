import riaps_testing

def test_LimitSpace():
    """Test RIAPS Space limit handler
    """
    results = riaps_testing.runTest("test_LimitSpace", "testLimitSpace", "spclimit.riaps", "spclimit.depl")
    assert len(results) != 0, "Failed to retrieve any logs!"
    for key in results.keys():
        log = results[key]
        assert log[0].find("Starting") != -1, "First line of %s isn't starting!" % key
        assert log[-1].find("Stopping") != -1, "Last line of %s isn't stopping!" % key

        numTick = 0
        numLimit = 0
        curTick = 0

        for line in log:
            if line.find("Starting") == -1 and line.find("Stopping") == -1:
                if line.find("Tick") != -1:
                    curTick += 1
                elif line.find("Limit") != -1:
                    if numLimit == 0:
                        curTick = 5 # Ignore startup time
                    numLimit += 1
                    numTick += curTick
                    curTick = 0
        
        assert numLimit != 0, "Failed to ever hit limit!"

        ratio = numTick*1.0/numLimit
        # The ratio should be approximately 5 because the limit is 5MB
        # and the file size is incremented every second by 1MB
        assert ratio > 4.5, "Hit limit too frequently: Ratio=%.2f" % ratio
        assert ratio < 5.5, "Hit limit too infrequently: Ratio=%.2f" % ratio