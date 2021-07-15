pipeline {
  agent { label 'test-vm' }
  stages {
    stage('Setup') {
      steps {
        withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
          sh 'more update_hosts.sh'
          //sh 'chmod +x update_hosts.sh && ./update_hosts.sh'
        }
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
        sh '''#!/bin/bash
          RIAPSHOME=/usr/local/riaps riaps_fab -i /home/riaps/.ssh/id_rsa.key sys.reboot
        '''
    }
  }
}
