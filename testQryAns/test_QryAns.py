"""RIAPS Qry Ans messaging model tests
"""
import riaps_testing

def verifyResults(results, numQry):
    """Verify that test results match the expected behavior of the Qry Ans model

    Args:
        results (dictionary): A dictionary in the format provided by riaps_testing.runTest(...)
        numQry  (int): The number of expected query actors

    """
    qryCount = 0
    for key in results:
        assert results[key][0].find("Starting") != -1, "First line of %s isn't starting!" % key
        assert results[key][-1].find("Stopping") != -1, "Last line of %s isn't stopping!" % key
        if key.find("Query") != -1:
            qryCount += 1
            qryID = 0
            query = -1
            ansCount = 0
            for line in results[key]:
                if line.find("Query") != -1:
                    parts = line.split(" ")
                    qryID = int(parts[1])
                    query = int(parts[2])
                elif line.find("Recv") != -1:
                    assert query != -1, "Received an unexpected response!"
                    parts = line.split(" ")
                    assert int(parts[2]) == qryID, "Received a response meant for another node!"
                    assert int(parts[3]) == query*2, "Received an invalid response: Expected %d, found %s" % (query*2, parts[3])
                    qryID = 0
                    query = -1
                    ansCount += 1
            assert ansCount != 0, "Didn't receive any answers!"

    assert qryCount == numQry, "Found incorrect number of query actors: Expected %d, found %d" % (numQry, qryCount)

def runTest(name, depl, numQry):
    """Run a Qry Ans test

    Invokes riaps_testing.runTest(...) with the provided name and depl in addition to
        the testQryAns folder and qryans.riaps model. Then automatically performs log
        validation with verifyResults(...)

    Args:
        name   (str): The name of the application
        depl   (str): The name of the deployment(.depl) file to be tested
        numQry (int): The number of clients expected to be created by the deployment

    """
    verifyResults(riaps_testing.runTest(name, "testQryAns", "qryans.riaps", depl), numQry)

def test_QryAnsLocal_1_1():
    runTest("QryAnsLocal_1_1", "testLocal_1_1.depl", 1)

def test_QryAnsRemote_1_1():
    runTest("QryAnsRemote_1_1", "testRemote_1_1.depl", 1)

def test_QryAnsRemote_1_N():
    runTest("QryAnsRemote_1_N", "testRemote_1_N.depl", 2)