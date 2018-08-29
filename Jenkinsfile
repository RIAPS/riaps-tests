pipeline {
  agent { label 'test-vm' }
  stages {
    stage('Setup') {
      steps {
        withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_OAUTH_TOKEN')]) {
          sh '''#!/bin/bash
            # Fetch riaps-pycom for the fabfile
            git clone https://$GITHUB_OAUTH_TOKEN@github.com/RIAPS/riaps-pycom.git
            git -C riaps-pycom checkout e3384354b4d842cc9704cf40170214cdaba03222

            # Fetch deb packages being tested
            wget https://github.com/gruntwork-io/fetch/releases/download/v0.1.1/fetch_linux_amd64
            chmod +x fetch_linux_amd64
            source version.sh
            function fetch () {
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
            fetch riaps-externals $externalsversion riaps-externals-armhf.deb
            fetch riaps-externals $externalsversion riaps-externals-amd64.deb
            fetch riaps-core $coreversion riaps-core-armhf.deb
            fetch riaps-core $coreversion riaps-core-amd64.deb
            fetch riaps-pycom $pycomversion riaps-pycom-armhf.deb
            fetch riaps-pycom $pycomversion riaps-pycom-amd64.deb
            fetch riaps-pycom $pycomversion riaps-systemd-armhf.deb
            fetch riaps-pycom $pycomversion riaps-systemd-amd64.deb
            fetch riaps-timesync $timesyncversion riaps-timesync-armhf.deb
            fetch riaps-timesync $timesyncversion riaps-timesync-amd64.deb
          '''
        }
        // Install deb packages to localhost and BBBs
        sh '''#!/bin/bash
          fab -f riaps-pycom/bin/fabfile -H 127.0.0.1 riaps.install sys.sudo:"sed -i 's/eth0/enp0s8/g' /usr/local/riaps/etc/riaps.conf"
          fab -f riaps-pycom/bin/fabfile -H $(python3 read_hosts.py) riaps.kill riaps.install deplo.start
        '''
      }
    }
    stage('Test') {
      steps {
        sh '''#!/bin/bash
          RIAPSHOME=/usr/local/riaps pytest -x --junitxml=results.xml
        '''
      }
    }
  }
  post {
    always {
        junit allowEmptyResults: false, keepLongStdio: true, testResults: 'results.xml'
    }
  }
}
