pipeline {
    agent { label 'docker' }

    environment {
        ADJUST_USER_UID = sh(
            returnStdout: true,
            script: 'id -u'
        ).trim()
        ADJUST_USER_GID = sh(
            returnStdout: true,
            script: 'id -g'
        ).trim()
        ADJUST_DOCKER_GID = sh(
            returnStdout: true,
            script: 'getent group docker | cut -d: -f3'
        ).trim()
    }

    stages {
        stage('Build') {
            agent {
                docker {
                    alwaysPull true
                    image 'kuralabs/python3-dev:latest'
                    args '-u root:root'
                }
            }

            steps {
                sh '''
                    sudo --user=python3 --preserve-env --set-home tox --recreate
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
                    cp -R .tox/doc/tmp/html/* /deploy/docs/ninjecto/
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
