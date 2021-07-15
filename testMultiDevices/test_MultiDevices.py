"""RIAPS Multiple Devices messaging model tests
"""
import riaps_testing

def verifyResults(results, numDevices):
     """Verify that test results match the expected behavior of a device using
        the Qry Ans model with an inside port within the device component

     Args:
         results (dictionary): A dictionary in the format provided by riaps_testing.runTest(...)
         numDevices  (int): The number of expected device actors

    """
    qryCount = 0
    for key in results:
        assert results[key][0].find("Starting") != -1, "First line of %s isn't starting!" % key
        assert results[key][-1].find("Stopping") != -1, "Last line of %s isn't stopping!" % key
        if key.find("Query") != -1:
            qryCount += 1
            qryID = 0
            queryNum = -1
            ansCount = 0
            for line in results[key]:
                if line.find("Query") != -1:
                    parts = line.split(" ")
                    qryID = int(parts[1])
                    queryNum = int(parts[2])
                elif line.find("Recv") != -1:
                    assert queryNum != -1, "Received an unexpected response!"
                    parts = line.split(" ")
                    assert int(parts[2]) == qryID, "Received a response meant for another node!"
                    assert int(parts[3]) == queryNum, "Received an invalid response: Expected %d, found %s" % (queryNum, parts[3])
                    qryID = 0
                    queryNum = -1
                    ansCount += 1
            assert ansCount != 0, "Didn't receive any answers!"

    assert qryCount == numDevices, "Found incorrect number of devices responsed: Expected %d, found %d" % (numDevices, qryCount)

def runTest(name, depl, numDevices):
    """Run a Multiple Devices test

    Invokes riaps_testing.runTest(...) with the provided name and depl in addition to
        the testMultiDevices folder and multiDevices.riaps model. Then automatically performs log
        validation with verifyResults(...)

    Args:
        name       (str): The name of the application
        depl       (str): The name of the deployment(.depl) file to be tested
        numDevices (int): The number of devices expected to be created by the deployment

    """
    verifyResults(riaps_testing.runTest(name, "testMultiDevices", "multiDevices.riaps", depl), numDevices)

def test_multiDevices():
    runTest("multiDevices", "multiDevices.depl", 3)
