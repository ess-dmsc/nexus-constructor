project = "nexus-geometry-constructor"

centos = 'essdmscdm/centos7-build-node:3.1.0'

container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
sh_cmd = "/usr/bin/scl enable rh-python35 -- /bin/bash -e"

def get_pipeline()
{
    return {
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
                        build_env/bin/pip --proxy ${http_proxy} install --upgrade pip
                        build_env/bin/pip --proxy ${http_proxy} install -r requirements.txt
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
                }
            } finally {
                container.stop()
            }
        }  // node
    }  // return
}

def get_system_test_pipeline()
{
    return {
        // Use Windows so that tests with the GUI can be run
        node('windows10') {
            // Use custom location to avoid Win32 path length issues
            ws('c:\\jenkins\\') {
                try {
                    cleanWs()
                } catch(Exception ex) {
                    println("Warning, failed to clean workspace on Windows node");
                }
                dir("${project}") {
                    stage("Checkout") {
                        scm_vars = checkout scm
                    }  // stage

                    stage("Create virtualenv") {
                      bat """python -m venv build_env
                      """
                    }

                    stage("Install requirements") {
                        bat """build_env\\Scripts\\pip.exe --proxy ${env.http_proxy} install -r requirements.txt"""
                        bat """build_env\\Scripts\\pip.exe --proxy ${env.http_proxy} install codecov"""
                    }

                    stage("Run unit and system tests") {
                        bat """build_env\\Scripts\\pytest.exe .\\ --ignore=build_env --junitxml=test_results.xml"""
                        bat """build_env\\Scripts\\pytest.exe --cov=geometry_constructor --cov-report=xml"""
                        withCredentials([string(credentialsId: 'nexus-constructor-codecov-token', variable: 'TOKEN')]) {
                            bat """build_env\\Scripts\\codecov.exe -t ${TOKEN} -c ${scm_vars.GIT_COMMIT} -f coverage.xml"""
                        }
                        junit "test_results.xml"
                    }
                }  // dir
            }  // ws
        }  // node
    }  // return
}

node() {
    cleanWs()

    def builders = [:]
    builders['unit_tests'] = get_pipeline()
    builders['system_tests'] = get_system_test_pipeline()

    parallel builders

    cleanWs()
}
