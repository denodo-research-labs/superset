import java.text.SimpleDateFormat

String getCurrentDate(){
    def date = new Date()
    def sdf = new SimpleDateFormat("yyyyMMdd")
    return sdf.format(date)
}

String date = getCurrentDate()
String packageJSONVersion = ""

pipeline {
    agent any

    triggers{
        cron('0 3 * * 7 ') //Every sunday at 3am
    }

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
        string(name: 'UBI_IMAGE_VERSION', description: 'Version of the base UBI image to be used')
        string(name: 'NPM_BUILD_CMD', description: 'npm build command', defaultValue: 'build')
        string(name: 'EMAIL_TO', description: 'Who to send the notification email to', defaultValue: 'htorres@denodo.com, dfernandez@denodo.com, mrodriguezr@denodo.com, mpicos@denodo.com')
    }

    stages {
        stage('Build') {
            steps {
                script {
                    def packageJSON = readJSON file: 'superset-frontend/package.json'
                    packageJSONVersion = packageJSON.version.replaceAll('\\+','_')
                    def dockerbuild = "docker build "
                    dockerbuild = dockerbuild + "--build-arg UBI_IMAGE_VERSION=${params.UBI_IMAGE_VERSION} "
                    dockerbuild = dockerbuild + "--build-arg NPM_BUILD_CMD=${params.NPM_BUILD_CMD} "
                    dockerbuild = dockerbuild + "-t superset-denodo:${packageJSONVersion} "
                    dockerbuild = dockerbuild + "--target ci ."
                    sh dockerbuild
                }
            }
        }

        stage('Naming'){
            steps {
                script {
                   sh "docker image tag superset-denodo:${packageJSONVersion} ${params.REGISTRY}/superset-denodo:${packageJSONVersion}"
                }
            }
        }

        stage('Analyze'){
            steps {
                script {
                    sh "docker run --rm -t -v ${WORKSPACE}:/tmp/reports -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --format json -o /tmp/reports/report.json ${params.REGISTRY}/superset-denodo:${packageJSONVersion}"
                }
            }
        }

        stage('Push'){
            when {
                expression { params.DRY_RUN == false }
            }
            steps {
                script {
                    sh "docker push ${params.REGISTRY}/superset-denodo:${packageJSONVersion}"
                }
            }
        }

        stage('Report'){
            steps{
                script {
                    echo "Sending email to ${params.EMAIL_TO}"
                    emailext (
                        subject: "DenodoConnects images build&scan: Success! '${env.JOB_NAME}'",
                        body: """<p>Check console output at <a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a>.</p>
                                <br>
                                <p>Check vulnerability reports attached in this email.</p>""",
                        to: "${params.EMAIL_TO}",
                        recipientProviders: [[$class: 'CulpritsRecipientProvider']],
                        attachmentsPattern: "report.json"
                    )
                }
            }
        }
    }

    post {
        success {
            echo 'Cleaning images'
            sh "docker rmi -f superset-denodo:${packageJSONVersion}"
            sh "docker rmi -f ${params.REGISTRY}/superset-denodo:${packageJSONVersion}"
            sh "docker builder prune -f"
            script {
                build job: 'rotate-gcloud-docker-registry', parameters: [
                    string(name: 'REGISTRY', value: "${params.REGISTRY}/superset-denodo"),
                    string(name: 'FILTER', value: "tags:*"),
                    string(name: 'IMAGES_TO_LEAVE', value: "4")                
                ]
            }
        }

        failure {
            echo "Sending email to ${params.EMAIL_TO}"
            emailext (
                subject: "DenodoConnects images build&scan: Failure! '${env.JOB_NAME}'",
                body: """<p>Check console output at <a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>""",
                to: "${params.EMAIL_TO}",
                recipientProviders: [[$class: 'CulpritsRecipientProvider']]
            )
        }

        always {
            echo 'Cleaning environment'
            echo 'Removing containers'
            sh "if ! [ \"\$(docker ps -a -f status=exited -q 2> /dev/null)\" = \"\" ]; then docker container rm -f \$(docker ps -a -f status=exited -q); else echo \"No dangling images\"; fi"
            echo 'Removing images'
            sh "if ! [ \"\$(docker images -q node:16-slim 2> /dev/null)\" = \"\" ] ; then docker rmi -f node:16-slim; else echo \"Image node:16-slim does not exist\"; fi"
            sh "if ! [ \"\$(docker images -q aquasec/trivy 2> /dev/null)\" = \"\" ] ; then docker rmi -f aquasec/trivy; else echo \"Image aquasec/trivy does not exist\"; fi"
            sh "if ! [ \"\$(docker images -q registry.access.redhat.com/ubi9/python-39:${params.UBI_IMAGE_VERSION} 2> /dev/null)\" = \"\" ] ; then docker rmi -f python:${params.PYTHON_VERSION_IMAGE}; else echo \"Image registry.access.redhat.com/ubi9/python-39:${params.UBI_IMAGE_VERSION} does not exist\"; fi"
            sh "if ! [ \"\$(docker images -f dangling=true -q 2> /dev/null)\" = \"\" ]; then docker rmi -f \$(docker images -f dangling=true -q); else echo \"No dangling images\"; fi"
            echo 'Removing cache'
            sh "docker builder prune -af"
            cleanWs()
        }
    }
}
