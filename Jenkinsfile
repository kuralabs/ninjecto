pipeline {
    agent none

    stages {
        stage('Build') {
            agent {
                docker {
                    image 'kuralabs/python3-dev:latest'
                }
            }

            steps {
                sh '''
                    tox -r
                '''
                stash name: 'docs', includes: '.tox/doc/tmp/html/**/*'
            }
        }

        stage('Publish') {
            agent { label 'docs' }
            when { branch 'master' }
            steps {
                unstash 'docs'
                sh '''
                    umask 022
                    mkdir -p /deploy/docs/ninjecto
                    rm -rf /deploy/docs/ninjecto/*
                    cp -R .tox/env/tmp/html/* /deploy/docs/ninjecto/
                '''
            }
        }
    }
    post {
        success {
            slackSend (
                color: '#00FF00',
                message: "SUCCESSFUL: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})"
            )
        }

        failure {
            slackSend (
                color: '#FF0000',
                message: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})"
            )
        }
    }
}
