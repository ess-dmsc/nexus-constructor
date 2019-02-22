project = "nexus-constructor"

centos = 'essdmscdm/centos7-build-node:3.1.0'

container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
sh_cmd = "/usr/bin/scl enable rh-python35 -- /bin/bash -e"

node("docker") {
    cleanWs()
    dir("${project}") {
        stage("Checkout") {
            scm_vars = checkout scm
        }
    }
    try {
        image = docker.image(centos)
        container = image.run("\
            --name ${container_name} \
            --tty \
            --network=host \
            --env http_proxy=${env.http_proxy} \
            --env https_proxy=${env.https_proxy} \
        ")
        sh "docker cp ${project} ${container_name}:/home/jenkins/${project}"
        sh """docker exec --user root ${container_name} ${sh_cmd} -c \"
            chown -R jenkins.jenkins /home/jenkins/${project}
        \""""

        stage("Create virtualenv") {
            sh """docker exec ${container_name} ${sh_cmd} -c \"
                cd ${project}
                python -m venv build_env
            \""""
        }

        stage("Install requirements") {
            sh """docker exec ${container_name} ${sh_cmd} -c \"
                cd ${project}
                build_env/bin/pip --proxy ${https_proxy} install --upgrade pip
                build_env/bin/pip --proxy ${https_proxy} install -r requirements.txt
                build_env/bin/pip --proxy ${https_proxy} install codecov==2.0.15
                \""""
        }

        stage("Run Linter") {
        sh """docker exec ${container_name} ${sh_cmd} -c \"
                cd ${project}
                build_env/bin/flake8
            \""""
        }

        stage("Run tests") {
            def testsError = null
            try {
                sh """docker exec ${container_name} ${sh_cmd} -c \"
                    cd ${project}
                    build_env/bin/pytest ./tests --ignore=build_env --junitxml=/home/jenkins/${project}/test_results.xml
                \""""
                }
                catch(err) {
                    testsError = err
                    currentBuild.result = 'FAILURE'
                }
            sh """docker exec ${container_name} ${sh_cmd} -c \"
                cd ${project}
                build_env/bin/pytest --cov=nexus_constructor --cov-report=xml
                \""""
            withCredentials([string(credentialsId: 'nexus-constructor-codecov-token', variable: 'TOKEN')]) {
                sh """docker exec ${container_name} ${sh_cmd} -c \"
                    cd ${project}
                    build_env/bin/codecov -t ${TOKEN} -c ${scm_vars.GIT_COMMIT} -f coverage.xml
                    \""""
            }
            sh "docker cp ${container_name}:/home/jenkins/${project}/test_results.xml test_results.xml"
            junit "test_results.xml"
        }
    } finally {
        container.stop()
    }
}
