import java.text.SimpleDateFormat

String getCurrentDate(){
    def date = new Date()
    def sdf = new SimpleDateFormat("yyyyMMdd")
    return sdf.format(date)
}

String date = getCurrentDate()

pipeline {
    agent any

    parameters {
        booleanParam(
            name: 'MAKE_PRINCIPAL',
            defaultValue: true,
            description: '''If this is checked, this will be the image to use by default
            (That that you download by default without tag)'''
        )
        booleanParam(
            name: 'DRY_RUN',
            defaultValue: true,
            description: 'WARNING!!! If this is checked, the image WONT be pushed to docker registry'
        )
        string(
            name: 'REGISTRY',
            description: 'Docker registry where the image will be uploaded to',
            defaultValue: 'gcr.io/denodo-proddev-container/denodolabs')
        string(name: 'PYTHON_VERSION_IMAGE', description: 'Python docker image tag to use', defaultValue: '3.8.16-slim')
        string(name: 'GECKODRIVER_VERSION', description: 'Gecko driver version', defaultValue: 'v0.32.0')
        string(name: 'FIREFOX_VERSION', description: 'Firefox version', defaultValue: '106.0.3')
        string(name: 'NPM_BUILD_CMD', description: 'npm build command', defaultValue: 'build')
        string(name: 'DENODO_VERSION', description: 'Denodo version to use', defaultValue: '8.0')
    }

    stages {
        stage('Build') {
            steps {
                script {
                    def dockerbuild = "docker build "
                    dockerbuild = dockerbuild + "--build-arg PY_VER=${params.PYTHON_VERSION_IMAGE} "
                    dockerbuild = dockerbuild + "--build-arg GECKODRIVER_VERSION=${params.GECKODRIVER_VERSION} "
                    dockerbuild = dockerbuild + "--build-arg FIREFOX_VERSION=${params.FIREFOX_VERSION} "
                    dockerbuild = dockerbuild + "--build-arg NPM_BUILD_CMD=${params.NPM_BUILD_CMD} "
                    dockerbuild = dockerbuild + "-t superset-denodo:${params.DENODO_VERSION}.${date} ."
                    sh dockerbuild
                }
            }
        }

        stage('Naming'){
            steps {
                script {
                   sh "docker image tag superset-denodo:${params.DENODO_VERSION}.${date} ${params.REGISTRY}/superset-denodo:${params.DENODO_VERSION}.${date}"
                }
            }
        }

        stage('Push'){
            when {
                expression { params.DRY_RUN == false }
            }
            steps {
                script {
                    sh "docker push ${params.REGISTRY}/superset-denodo:${params.DENODO_VERSION}.${date}"
                }
            }
        }
    }

    post {
        success {
            echo 'Cleaning images'
            sh "docker rmi -f superset-denodo:${params.DENODO_VERSION}.${date}"
            sh "docker rmi -f ${params.REGISTRY}/superset-denodo:${params.DENODO_VERSION}.${date}"
            sh "docker builder prune -f"
        }

        always {
            echo 'Cleaning environment'
            echo 'Removing containers'
            sh "if ! [ \"\$(docker ps -a -f status=exited -q 2> /dev/null)\" = \"\" ]; then docker container rm -f \$(docker ps -a -f status=exited -q); else echo \"No dangling images\"; fi"
            echo 'Removing images'
            sh "if ! [ \"\$(docker images -q node:16-slim 2> /dev/null)\" = \"\" ] ; then docker rmi -f node:16-slim; else echo \"Image node:16-slim not exists\"; fi"
            sh "if ! [ \"\$(docker images -q python:${params.PYTHON_VERSION_IMAGE} 2> /dev/null)\" = \"\" ] ; then docker rmi -f python:${params.PYTHON_VERSION_IMAGE}; else echo \"Image python:${params.PYTHON_VERSION_IMAGE} not exists\"; fi"
            sh "if ! [ \"\$(docker images -f dangling=true -q 2> /dev/null)\" = \"\" ]; then docker rmi -f \$(docker images -f dangling=true -q); else echo \"No dangling images\"; fi"
            echo 'Removing cache'
            sh "docker builder prune -af"
            cleanWs()
        }
    }
}
