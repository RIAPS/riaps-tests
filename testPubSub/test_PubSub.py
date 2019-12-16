"""RIAPS Pub Sub messaging model tests
"""
from riaps_testing import runTest

def verifyResults(results, numPub, numSub):
    """Verify that test results match the expected behavior of the Pub Sub model

    Parses the returned log files to find all messages send by each publisher. Then asserts that
    each message sent by each publisher was received by each subscriber.

    Args:
        results (dictionary): A dictionary in the format provided by riaps_testing.runTest(...)
        numPub  (int): The number of expected publishers
        numSub  (int): The number of expected subscribers

    """
    pubs = {}
    subs = {}
    # Parse log files
    for key in results.keys():
        keyword = ""
        if key.find("Pub") != -1:
            keyword = "Publish"
        elif key.find("Sub") != -1:
            keyword = "Subscribe"
        if keyword != "":
            assert results[key][0].find("Starting") != -1, "First line of %s isn't starting!" % key
            assert results[key][-1].find("Stopping") != -1, "Last line of %s isn't stopping!" % key
            for line in results[key]:
                if line.find(keyword) != -1:
                    parts = line.split(" ")
                    if keyword == "Publish":
                        id = parts[1]
                        msg = parts[2]
                        if not id in pubs:
                            pubs[id] = []
                        pubs[id].append(msg)
                    elif keyword == "Subscribe":
                        id = parts[1]
                        pub_id = parts[2]
                        msg = parts[3]
                        if not id in subs:
                            subs[id] = {}
                        if not pub_id in subs[id]:
                            subs[id][pub_id] = []
                        subs[id][pub_id].append(msg)
    # Verify expected number of publishers and subscribers
    assert len(pubs) == numPub, "Incorrect number of pubs: Expected %d but found %d" % (numPub, len(pubs))
    assert len(subs) == numSub, "Incorrect number of subs: Expected %d but found %d" % (numSub, len(subs))
    # Iterate over subscribers to verify delievery of publisher messages
    for sub in subs.keys():
        for pub in pubs.keys():
            assert pub in subs[sub], "Sub #%s didn't receive any messages from Pub #%s" % (sub, pub)
            num_pub = len(pubs[pub])
            recv = 0
            for msg in pubs[pub]:
                if msg in subs[sub][pub]:
                    recv += 1
            perc = recv * 100.0 / recv
            print("Sub #%s received %.1f%%(%d) of Pub #%s's messages" % (sub, perc, recv, pub))
            assert perc > 80.0

def test_PubSubLocal_1_1():
    verifyResults(runTest("PubSubLocal_1_1", "testPubSub", "local.riaps", "testLocal_1_1.depl"), 1, 1)

def test_PubSubLocal_1_N():
    verifyResults(runTest("PubSubLocal_1_N", "testPubSub", "local.riaps", "testLocal_1_N.depl"), 1, 2)

def test_PubSubLocal_N_1():
    verifyResults(runTest("PubSubLocal_N_1", "testPubSub", "local.riaps", "testLocal_N_1.depl"), 2, 1)

def test_PubSubLocal_N_N():
    verifyResults(runTest("PubSubLocal_N_N", "testPubSub", "local.riaps", "testLocal_N_N.depl"), 2, 2)

def test_PubSubRemote_1_1():
    verifyResults(runTest("PubSubRemote_1_1", "testPubSub", "remote.riaps", "testRemote_1_1.depl"), 1, 1)

def test_PubSubRemote_1_N():
    verifyResults(runTest("PubSubRemote_1_N", "testPubSub", "remote.riaps", "testRemote_1_N.depl"), 1, 2)

def test_PubSubRemote_N_1():
    verifyResults(runTest("PubSubRemote_N_1", "testPubSub", "remote.riaps", "testRemote_N_1.depl"), 2, 1)

def test_PubSubRemote_N_N():
    verifyResults(runTest("PubSubRemote_N_N", "testPubSub", "remote.riaps", "testRemote_N_N.depl"), 3, 3)