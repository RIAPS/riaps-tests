pipeline {
  agent { label 'test-vm' }
  stages {
    stage('Setup') {
      steps {
        //withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_OAUTH_TOKEN')]) {
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
    }
  }
}
