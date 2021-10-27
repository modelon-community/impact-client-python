node('docker'){

  stage ('scm') {
    checkout(scm)
  }

  stage ('test') {
    sh 'make lint'
    sh 'make test'
  }

  stage ('publish') {
    withCredentials([usernamePassword(credentialsId: 'GitHub-Jenkins', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
      withCredentials([usernamePassword(credentialsId: 'pypi-modelon-api-key', usernameVariable: 'PYPI_USERNAME', passwordVariable: 'PYPI_PASSWORD')]) {
        env.GIT_CREDENTIALS = "${GIT_USERNAME}:${GIT_PASSWORD}"
        env.PYPI_USERNAME = "${PYPI_USERNAME}"
        env.PYPI_PASSWORD = "${PYPI_PASSWORD}"
        sh 'make publish'
      }
    }
  }
}
