"""RIAPS Req Rep messaging model tests
"""
import riaps_testing

def verifyResults(results):
    """Verify that test results match the expected behavior of the Req Rep model

    Args:
        results (dictionary): A dictionary in the format provided by riaps_testing.runTest(...)
    """

    reqComponentRan = False
    repComponentRan = False
    for key in results:
        if key.find("Req") != -1:
            reqComponentRan = True
            reqResults = results[key]
            assert reqResults[-1].find("Stopping") != -1, "Last line of request component isn't \"Stopping\"!"
            assert reqResults[0].find("Starting") != -1, "First line of request component isn't \"Starting\"!"
        elif key.find("Rep") != -1:
            repComponentRan = True
            repResults = results[key]
            assert repResults[-1].find("Stopping") != -1, "Last line of reply component isn't \"Stopping\"!"
            assert repResults[0].find("Starting") != -1, "First line of reply component isn't \"Starting\"!"
        else:
            assert False, "Collected log for neither Request nor Reply"

    assert reqComponentRan, "No logs collected from request component"
    assert repComponentRan, "No logs collected from reply component"

    requestList = {}
    reportDict = {}
    receivedDict = {}


    if reqComponentRan:
        for msg in reqResults:
            if msg.find("Starting") != -1 or msg.find("on_clock") != -1 or msg.find("Stopping") != -1:
                continue
            if msg.find("Request") != -1:
                parts = msg.split(" ")
                requestDict[int(parts[-1])] = msg
            elif msg.find("Report") != -1:
                parts = msg.split(" ")
                reportDict[int(parts[-1])/2] = msg

    if repComponentRan:
        for msg in repResults:
            if msg.find("Starting") != -1 or msg.find("Stopping") != -1:
                continue
            if msg.find("Received") != -1:
                parts = msg.split(" ")
                receivedDict[int(parts[-1])] = msg

    msgCount, successCount = 0
    for request in requestDict:
        msgCount += 1
        if request in receivedDict:
            successCount += 1

    assert successCount/msgCount > 90.0, "Less than 90% ("+successCount/msgCount+") of requests recei by Replier"

    msgCount, successCount = 0
    for request in receivedDict:
        msgCount += 1
        if request in reportDict:
            successCount += 1

    assert successCount/msgCount > 90.0, "Less than 90% ("+successCount/msgCount+") of replies received by Requestor"


def runTest(name, riaps, depl):
    """Run a Clt Srv test

    Invokes riaps_testing.runTest(...) with the provided name and depl in addition to
        the testCltSrv folder and cltsrv.riaps model. Then automatically performs log
        validation with verifyResults(...)

    Args:
        name   (str): The name of the application
        depl   (str): The name of the deployment(.depl) file to be tested
        numClt (int): The number of clients expected to be created by the deployment

    """
    verifyResults(riaps_testing.runTest(name, "testReqRep", riaps, depl))

def test_ReqRep_local():
    runTest("ReqRep_local", "local.riaps", "testLocal.depl")

def test_ReqRep_local_single():
    runTest("ReqRep_local_single", "local_single.riaps", "testLocal_single.depl")

def test_ReqRep_remote():
    runTest("ReqRep_remote", "remote.riaps", "testRemote.depl")
