"""RIAPS Clt Srv messaging model tests
"""
import riaps_testing

def verifyResults(results, numClt):
    """Verify that test results match the expected behavior of the Clt Srv model

    Args:
        results (dictionary): A dictionary in the format provided by riaps_testing.runTest(...)
        numClt  (int): The number of expected clients

    """
    cltCount = 0
    for key in results:
        if key.find("Client") != -1:
            assert results[key][0].find("Starting") != -1, "First line of %s isn't starting!" % key
            assert results[key][-1].find("Stopping") != -1, "Last line of %s isn't stopping!" % key
            cltCount += 1
            cltID = 0
            request = -1
            repCount = 0
            for line in results[key]:
                assert line.find("Failed") == -1, "Client request failed"
                if line.find("Req") != -1:
                    assert request == -1, "Made another request before receiving a reply!"
                    parts = line.split(" ")
                    cltID = int(parts[1])
                    request = int(parts[2])
                elif line.find("Rep") != -1:
                    assert request != -1, "Received an unexpected response!"
                    parts = line.split(" ")
                    assert int(parts[2]) == cltID, "Received a response meant for another node!"
                    assert int(parts[3]) == request*2, "Received an invalid response: Expected %d, found %s" % (request*2, parts[3])
                    cltID = 0
                    request = -1
                    repCount += 1
            assert repCount != 0, "Didn't receive any responses!"

    assert cltCount == numClt, "Found incorrect number of clients: Expected %d, found %d" % (numClt, cltCount)

def runTest(name, depl, numClt):
    """Run a Clt Srv test

    Invokes riaps_testing.runTest(...) with the provided name and depl in addition to
        the testCltSrv folder and cltsrv.riaps model. Then automatically performs log
        validation with verifyResults(...)

    Args:
        name   (str): The name of the application
        depl   (str): The name of the deployment(.depl) file to be tested
        numClt (int): The number of clients expected to be created by the deployment

    """
    verifyResults(riaps_testing.runTest(name, "testCltSrv", "cltsrv.riaps", depl), numClt)

def test_CltSrvLocal_1_1():
    runTest("CltSrvLocal_1_1", "testLocal_1_1.depl", 1)

def test_CltSrvRemote_1_1():
    runTest("CltSrvRemote_1_1", "testRemote_1_1.depl", 1)

def test_CltSrvRemote_1_N():
    runTest("CltSrvRemote_1_N", "testRemote_1_N.depl", 2)