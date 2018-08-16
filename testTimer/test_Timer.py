"""RIAPS Timer Port Tests
"""
import riaps_testing

def test_Timer():
    """
    Verify that test results match the expected behavior of the Timer ports
    """
    results = riaps_testing.runTest("Timer", "testTimer", "timer.riaps", "timer.depl")
    for key in results:
        if key.find("Client") != -1:
            assert results[key][0].find("Starting") != -1, "First line of %s isn't starting!" % key
            assert results[key][-1].find("Stopping") != -1, "Last line of %s isn't stopping!" % key
            # cltCount += 1
            # cltID = 0
            # request = -1
            # repCount = 0
            # for line in results[key]:
            #     assert line.find("Failed") == -1, "Client request failed"
            #     if line.find("Req") != -1:
            #         assert request == -1, "Made another request before receiving a reply!"
            #         parts = line.split(" ")
            #         cltID = int(parts[1])
            #         request = int(parts[2])
            #     elif line.find("Rep") != -1:
            #         assert request != -1, "Received an unexpected response!"
            #         parts = line.split(" ")
            #         assert int(parts[2]) == cltID, "Received a response meant for another node!"
            #         assert int(parts[3]) == request*2, "Received an invalid response: Expected %d, found %s" % (request*2, parts[3])
            #         cltID = 0
            #         request = -1
            #         repCount += 1
            # assert repCount != 0, "Didn't receive any responses!"

    # assert cltCount == numClt, "Found incorrect number of clients: Expected %d, found %d" % (numClt, cltCount)
