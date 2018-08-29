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
            ./fetch_linux_amd64 --repo="https://github.com/RIAPS/riaps-externals/" --tag="$externalsversion" --release-asset="riaps-externals-armhf.deb" .
            ./fetch_linux_amd64 --repo="https://github.com/RIAPS/riaps-externals/" --tag=$externalsversion --release-asset="riaps-externals-amd64.deb" .
            ./fetch_linux_amd64 --repo="https://github.com/RIAPS/riaps-core" --tag=$coreversion --release-asset="riaps-core-amd64.deb" .
            ./fetch_linux_amd64 --repo="https://github.com/RIAPS/riaps-core" --tag=$coreversion --release-asset="riaps-core-armhf.deb" .
            ./fetch_linux_amd64 --repo="https://github.com/RIAPS/riaps-pycom" --tag=$pycomversion --release-asset="riaps-pycom-amd64.deb" .
            ./fetch_linux_amd64 --repo="https://github.com/RIAPS/riaps-pycom" --tag=$pycomversion --release-asset="riaps-pycom-armhf.deb" .
            ./fetch_linux_amd64 --repo="https://github.com/RIAPS/riaps-pycom" --tag=$pycomversion --release-asset="riaps-systemd-armhf.deb" .
            ./fetch_linux_amd64 --repo="https://github.com/RIAPS/riaps-pycom" --tag=$pycomversion --release-asset="riaps-systemd-amd64.deb" .
            ./fetch_linux_amd64 --repo="https://github.com/RIAPS/riaps-timesync" --tag=$timesyncversion --release-asset="riaps-timesync-amd64.deb" .
            ./fetch_linux_amd64 --repo="https://github.com/RIAPS/riaps-timesync" --tag=$timesyncversion --release-asset="riaps-timesync-armhf.deb" .
          '''
        }
        // Install deb packages to localhost and BBBs
        sh '''#!/bin/bash
          fab -f riaps-pycom/bin/fabfile -H 127.0.0.1 riaps.install
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
