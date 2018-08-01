pipeline {
  agent { label 'test-vm' }
  stages {
    stage('Test') {
      steps {
        sh '''#!/bin/bash
          RIAPSHOME=/usr/local/riaps pytest -x --junitxml=results.xml
        '''
      }
    }
    post {
        always {
            junit 'results.xml'
        }
    }
  }
}
