#!/bin/bash
# Script for updating BBBs to a certain RIAPS version
# Reads version numbers from version.sh

# GITHUB_OAUTH_TOKEN must be set to a valid token for fetching artifacts and fabfile
# The Jenkinsfile sets this variable before calling this script

# Name of RIAPS NIC on build machine (Needs to be changed for a different machine)
NIC_NAME=enp0s8

# Fetch the script used for downloading artifacts from GitHub
wget https://github.com/gruntwork-io/fetch/releases/download/v0.1.1/fetch_linux_amd64
chmod +x fetch_linux_amd64

# fetch
# Download a specific branch or tag of a build artifact
# args: <repo> <tag/branch> <artifact>
function fetch () {
    # Try to fetch the artifact from Jenkins
    wget -q $JENKINS_URL/job/RIAPS/job/$1/job/$2/lastSuccessfulBuild/artifact/$3
    if [ $? -ne 0 ]
    then
        # Failed to find artifact on Jenkins, so check GitHub
        ./fetch_linux_amd64 --repo="https://github.com/RIAPS/$1/" --tag="$2" --release-asset="$3" .
        if [ $? -ne 0 ]
        then
            echo "Failed to find $1/$2/$3 on Jenkins or GitHub"
            exit 1
        else
            echo "Downloaded $1/$2/$3 from GitHub"
        fi
    else
        echo "Downloaded $1/$2/$3 from Jenkins"
    fi
}

# Fetch riaps-pycom for the fabfile
git clone https://$GITHUB_OAUTH_TOKEN@github.com/RIAPS/riaps-pycom.git
git -C riaps-pycom checkout 6c21a2ee3e267ba3be8866acfeaed3d44cf1565a

# Fetch deb packages being tested
source version.sh
#fetch riaps-core $coreversion riaps-core-armhf.deb
#fetch riaps-core $coreversion riaps-core-amd64.deb
fetch riaps-pycom $pycomversion riaps-pycom-armhf.deb
fetch riaps-pycom $pycomversion riaps-pycom-amd64.deb
fetch riaps-timesync $timesyncversion riaps-timesync-armhf.deb
fetch riaps-timesync $timesyncversion riaps-timesync-amd64.deb

# Install deb packages to localhost and BBBs
fab -f riaps-pycom/bin/fabfile -H 127.0.0.1 riaps.install
fab -f riaps-pycom/bin/fabfile -H $(python3 read_hosts.py) riaps.kill riaps.install deplo.start

# Update riaps.conf to correct NIC name
sudo sed -i "s/eth0/$NIC_NAME/g" /etc/riaps/riaps.conf
