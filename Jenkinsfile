project = "nexus-constructor"

centos = 'essdmscdm/centos7-build-node:4.0.0'

container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
sh_cmd = "/bin/bash -e"

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
                python3.6 -m venv build_env
            \""""
        }

        stage("Install requirements") {
            sh """docker exec ${container_name} ${sh_cmd} -c \"
                cd ${project}
                build_env/bin/pip --proxy ${https_proxy} install --upgrade pip
                build_env/bin/pip --proxy ${https_proxy} install -r requirements.txt
                build_env/bin/pip --proxy ${https_proxy} install codecov==2.0.15 black
                \""""
        }
                              
        stage("Check formatting") {
            sh """docker exec ${container_name} ${sh_cmd} -c \"
                cd ${project}
                build_env/bin/python -m black . --check --exclude ./build_env/
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
                    build_env/bin/python -m pytest -s ./tests --ignore=build_env --junit-xml=/home/jenkins/${project}/test_results.xml --assert=plain --cov=nexus_constructor --cov-report=xml
                \""""
                }
                catch(err) {
                    testsError = err
                    currentBuild.result = 'FAILURE'
                }
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
