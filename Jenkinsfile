pipeline {
  agent any

  parameters {
    string(name: 'PROJECT_NAME', defaultValue: '', description: 'Unique project name')
    string(name: 'SUBMITTED_BY', defaultValue: '', description: 'Submitter email')
  }

  stages {
    stage('Validate') {
      steps {
        script {
          if (!(params.PROJECT_NAME ==~ /^[a-z0-9][a-z0-9-]{2,30}$/)) {
            error "Invalid project name"
          }
        }
      }
    }

    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Build & Deploy') {
      steps {
        dir('template') {
          withEnv(["PROJECT_NAME=${params.PROJECT_NAME}"]) {
            sh '''
              export DB_PASS=$(openssl rand -hex 12)
              docker compose -p "$PROJECT_NAME" up -d --build
            '''
          }
        }
      }
    }

    stage('Verify') {
      steps {
        dir('template') {
          script {
            def port = sh(script: "docker compose -p ${params.PROJECT_NAME} port frontend 80 | head -1 | cut -d: -f2",
                          returnStdout: true).trim()
            sh "sleep 10 && curl -f http://localhost:${port}/api/health"
            currentBuild.description = "http://13.127.211.64:${port}"
            echo "Deployed at port ${port}"
          }
        }
      }
    }
  }

  post {
    failure {
      dir('template') {
        sh "docker compose -p ${params.PROJECT_NAME} down -v || true"
      }
    }
  }
}
