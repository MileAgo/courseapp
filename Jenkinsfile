pipeline {
    agent any

    environment {
        IMAGE_NAME = 'mileag0/mydevopsproject'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%IMAGE_TAG% -t %IMAGE_NAME%:latest .'
            }
        }

        stage('Security Scan') {
            steps {
                // fail the build on HIGH/CRITICAL vulnerabilities that have a fix available
                bat 'docker run --rm -v //var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed --scanners vuln %IMAGE_NAME%:%IMAGE_TAG%'
            }
        }

        stage('Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_TOKEN'
                )]) {
                    bat 'echo %DOCKER_TOKEN% | docker login -u %DOCKER_USERNAME% --password-stdin'
                    bat 'docker push %IMAGE_NAME%:%IMAGE_TAG%'
                    bat 'docker push %IMAGE_NAME%:latest'
                    bat 'docker logout'
                }
            }
        }

        stage('Update GitOps') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-creds',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_TOKEN'
                )]) {
                    bat '''
                        if exist gitops rmdir /s /q gitops
                        git clone https://%GIT_USER%:%GIT_TOKEN%@github.com/MileAgo/courseapp-gitops.git gitops
                        powershell -Command "(Get-Content gitops/benny-app/dev/values.yaml) -replace 'tag: .*', 'tag: %IMAGE_TAG%' | Set-Content gitops/benny-app/dev/values.yaml"
                        cd gitops
                        git config user.name "jenkins"
                        git config user.email "jenkins@localhost"
                        git add benny-app/dev/values.yaml
                        git commit -m "Update image tag to %IMAGE_TAG%"
                        git push origin main
                    '''
                }
            }
        }
    }
}
