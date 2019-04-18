project = "nexus-constructor"

// Set number of old artefacts to keep.
properties([
    buildDiscarder(
        logRotator(
            artifactDaysToKeepStr: '',
            artifactNumToKeepStr: '5',
            daysToKeepStr: '',
            numToKeepStr: ''
        )
    )
])

centos = 'essdmscdm/centos7-build-node:4.0.0'

container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
sh_cmd = "/bin/bash -e"

def get_win10_pipeline() {
return {
    node('windows10') {
      // Use custom location to avoid Win32 path length issues
      ws('c:\\jenkins\\') {
      cleanWs()
      dir("${project}") {
        stage("win10: Checkout") {
          scm_vars = checkout scm
        }  // stage

	stage("win10: Setup") {
          bat """python -m pip install --user -r requirements.txt
	    """
	} // stage
        stage("win10: Build Executable") {
          bat """
	    python setup.py build_exe"""
        }  // stage
    stage('win10: Archive Executable'){
        def git_commit_short = scm_vars.GIT_COMMIT.take(7)
        powershell label: 'Archiving build folder', script: "Compress-Archive -Path .\\build -DestinationPath nexus-constructor_windows_${git_commit_short}.zip"
        archiveArtifacts 'nexus-constructor*.zip'
    } // stage

      }  // dir
      } //ws
} // node
} // return
} // def

def get_macos_pipeline() {
return {
node('macos') {

cleanWs()
dir("${project}") {

 stage('Checkout') {
 try {
    checkout scm
 } catch (e) {
    failure_function(e, 'MacOSX / Checkout failed')
 }
 }

 stage('Setup'){
    sh "python3 -m pip install --user -r requirements.txt"
 }

 stage('Build Executable') {
    sh "python3 setup.py build_exe"
 }
 // archive as well
} // dir
} // node
} // return
} // def

def get_linux_pipeline() {
return {
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
                build_env/bin/python -m black . --check --exclude=build_env/
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
if (env.CHANGE_ID) {
    stage('Build Executable'){
        sh "docker exec ${container_name} ${sh_cmd} -c \" cd ${project} && build_env/bin/python setup.py build_exe  \" "
    }
    stage('Archive Executable') {
        def git_commit_short = scm_vars.GIT_COMMIT.take(7)
        sh "docker cp ${container_name}:/home/jenkins/${project}/build/ ./build && tar czvf nexus-constructor_linux_${git_commit_short}.tar.gz ./build "
        archiveArtifacts artifacts: 'nexus-constructor*.tar.gz', fingerprint: true
    } // stage
} // if
} // return
} // def

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

        def builders = [:]
        builders['centos7'] = get_linux_pipeline()
        // disabled for now as the build isn't setup for Mac OS just yet.
        // builders['macOS'] = get_macos_pipeline()

        // Only build executables on windows if it is a PR build
        if (env.CHANGE_ID) {
            builders['windows10'] = get_win10_pipeline()
        }
        parallel builders

    } finally {
        container.stop()
    }
}
