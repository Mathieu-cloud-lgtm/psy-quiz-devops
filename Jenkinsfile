pipeline {
    agent any

    environment {
        APP_NAME = 'psy-quiz'
        IMAGE_TAG = 'psy-quiz:latest'
        CONTAINER_NAME = 'psy-quiz-app'
    }

    stages {
        stage('Checkout') {
            steps {
              git branch: 'master', url: 'https://github.com/Mathieu-cloud-lgtm/psy-quiz-devops.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${IMAGE_TAG} .'
            }
        }

        stage('Test Container') {
            steps {
                sh 'docker run -d --name test-${APP_NAME} -p 8081:8000 ${IMAGE_TAG}'
                sh 'sleep 5'
                sh 'curl -f http://localhost:8081 || exit 1'
                sh 'docker stop test-${APP_NAME} && docker rm test-${APP_NAME}'
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker stop ${CONTAINER_NAME} || true'
                sh 'docker rm ${CONTAINER_NAME} || true'
                sh 'docker run -d --name ${CONTAINER_NAME} -p 8080:8000 ${IMAGE_TAG}'
            }
        }
    }

    post {
        success {
            echo '✅ Déploiement réussi !'
        }
        failure {
            echo '❌ Échec du pipeline'
        }
    }
}
