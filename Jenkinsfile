@Library('ecdc-pipeline')
import ecdcpipeline.ContainerBuildNode
import ecdcpipeline.PipelineBuilder

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

container_build_nodes = [
  'centos7': ContainerBuildNode.getDefaultContainerBuildNode('centos7-gcc8')
]


pipeline_builder = new PipelineBuilder(this, container_build_nodes)

builders = pipeline_builder.createBuilders { container ->

    pipeline_builder.stage("Checkout") {
        dir(pipeline_builder.project) {
            scm_vars = checkout scm
        }
        // Copy source code to container
        container.copyTo(pipeline_builder.project, pipeline_builder.project)
    }  // stage

    pipeline_builder.stage("Create virtualenv") {
        container.sh """
            cd ${project}
            python3.6 -m venv build_env
        """
    } // stage

    pipeline_builder.stage("Install requirements") {
        container.sh """
            cd ${project}
            build_env/bin/pip --proxy ${https_proxy} install --upgrade pip
            build_env/bin/pip --proxy ${https_proxy} install -r requirements-jenkins.txt
            """
    } // stage

    if (env.CHANGE_ID) {
        pipeline_builder.stage("Check formatting") {
            try {
                container.sh """
                cd ${project}
                export LC_ALL=en_US.utf-8
                export LANG=en_US.utf-8
                build_env/bin/python -m black .
                git config user.email 'dm-jenkins-integration@esss.se'
                git config user.name 'cow-bot'
                git status -s
                git add -u
                git commit -m 'GO FORMAT YOURSELF (black)'
                """
            } catch (e) {
                // Okay to fail as there could be no badly formatted files to commit
            } finally {
                // Clean up
            }
        } // stage
    }

    pipeline_builder.stage("Run Linter") {
        container.sh """
                cd ${project}
                build_env/bin/flake8 --exclude build_env,definitions,nx-class-documentation
            """
    } // stage

   pipeline_builder.stage("Static type check") {
       container.sh """
               cd ${project}
               build_env/bin/python -m mypy ./nexus_constructor
           """
   } // stage

    pipeline_builder.stage("Run tests") {
        def testsError = null
        try {
                container.sh """
                    cd ${project}
                    build_env/bin/python -m pytest -s ./tests --ignore=build_env --ignore=tests/ui_tests
                """
            }
            catch(err) {
                testsError = err
                currentBuild.result = 'FAILURE'
            }

    } // stage

    pipeline_builder.stage("Verify NeXus HTML") {
        container.sh """
            python3.6 -m venv nexus_doc_venv
            source nexus_doc_venv/bin/activate
            pip --proxy ${https_proxy} install --upgrade pip
            pip --proxy ${https_proxy} install -r ${project}/definitions/requirements.txt

            mkdir nexus_doc
            cd nexus_doc
            export SOURCE_DIR=../${project}/definitions
            python ../${project}/definitions/utils/build_preparation.py ../${project}/definitions
            make
        """

        container.sh "diff --recursive ${project}/nx-class-documentation nexus_doc/manual/build/html"
    } // stage

    if (env.CHANGE_ID) {
        pipeline_builder.stage('Build Executable'){
            container.sh "cd ${project} && build_env/bin/pyinstaller --noconfirm nexus-constructor.spec"
        }

        pipeline_builder.stage('Archive Executable') {
            def git_commit_short = scm_vars.GIT_COMMIT.take(7)
            container.copyFrom("${project}/dist/", './build')
            sh "tar czvf nexus-constructor_linux_${git_commit_short}.tar.gz ./build "
            archiveArtifacts artifacts: 'nexus-constructor*.tar.gz', fingerprint: true
        } // stage
    } // if

}

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
                    } // catch
                } // stage
                stage('Setup') {
                    sh """
                        mkdir -p ~/virtualenvs
                        /opt/local/bin/python3.6 -m venv ~/virtualenvs/${pipeline_builder.project}-${pipeline_builder.branch}
                        source ~/virtualenvs/${pipeline_builder.project}-${pipeline_builder.branch}/bin/activate
                        pip --proxy=${https_proxy} install --upgrade pip
                        pip --proxy=${https_proxy} install -r requirements-dev.txt
                    """
                } // stage
                stage('Run tests') {
                    sh """
                        source ~/virtualenvs/${pipeline_builder.project}-${pipeline_builder.branch}/bin/activate
                        python -m pytest . -s --ignore=definitions/ --ignore=tests/ui_tests/
                    """
                } // stage
            } // dir
        } // node
    } // return
} // def

node("docker") {
    cleanWs()

    stage('Checkout') {
        dir("${project}") {
            try {
                scm_vars = checkout scm
            } catch (e) {
                failure_function(e, 'Checkout failed')
            }
        }
    }

    builders['macOS'] = get_macos_pipeline()
    parallel builders
}
