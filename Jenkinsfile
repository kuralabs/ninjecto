pipeline {
    agent { label 'docker' }

    stages {
        stage('Build') {
            agent { docker { image 'python:3.6' } }

            steps {
                sh '''
                    pip3 install tox
                    tox --recreate
                '''
                stash name: 'docs', includes: '.tox/doc/tmp/html/**/*'
            }
        }

        stage('Publish') {
            agent { label 'docs' }
            when {
                beforeAgent true
                branch 'master'
            }

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
                message: ":sunny: SUCCESSFUL: " +
                    "<${env.BUILD_URL}|[${env.BUILD_NUMBER}] ${env.JOB_NAME}>"
            )
        }

        failure {
            slackSend (
                color: '#FF0000',
                message: ":rain_cloud: FAILED: " +
                    "<${env.BUILD_URL}|[${env.BUILD_NUMBER}] ${env.JOB_NAME}>"
            )
        }
    }
}
