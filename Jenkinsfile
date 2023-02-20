@Library('ecdc-pipeline')
import ecdcpipeline.ContainerBuildNode
import ecdcpipeline.PipelineBuilder

project = "nexus-constructor"

// Set number of old artefacts to keep.
properties([
    buildDiscarder(
        logRotator(
            artifactDaysToKeepStr: '',
            artifactNumToKeepStr: '1',
            daysToKeepStr: '',
            numToKeepStr: ''
        )
    )
])

container_build_nodes = [
  'centos7': ContainerBuildNode.getDefaultContainerBuildNode('centos7-gcc11')
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

    pipeline_builder.stage("${container.key}: Dependencies") {
        container.sh """
        which python
        python --version
        python -m pip install --user -r ${pipeline_builder.project}/requirements-dev.txt
        python -m pip install --user -r ${pipeline_builder.project}/requirements-jenkins.txt
        """
    } // stage

    if (env.CHANGE_ID) {
        pipeline_builder.stage("${container.key}: Formatting (black)") {
            try {
                container.sh """
                cd ${pipeline_builder.project}
                export LC_ALL=en_US.utf-8
                export LANG=en_US.utf-8
                python -m black .
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

    pipeline_builder.stage("${container.key}: Static Analysis (flake8)") {
        container.sh """
        cd ${pipeline_builder.project}
        python -m flake8 --exclude definitions,nx-class-documentation
        """
    } // stage

//   pipeline_builder.stage("Static type check") {
//       container.sh """
//       cd ${pipeline_builder.project}
//       python -m mypy --ignore-missing-imports ./nexus_constructor
//       """
//   } // stage

    pipeline_builder.stage("${container.key}: Run non-ui tests") {
        def testsError = null
        try {
            container.sh """
            cd ${pipeline_builder.project}
            python -m pytest tests -s
            """
        }
        catch(err) {
            testsError = err
            currentBuild.result = 'FAILURE'
        }

    } // stage
    
    // Only run in pull request builds
    if (env.CHANGE_ID) {
        def diffError = false
        pipeline_builder.stage("Verify NeXus HTML") {
            container.sh """
            python -m venv nexus_doc_venv
            source nexus_doc_venv/bin/activate
            pip --proxy ${https_proxy} install --upgrade pip
            pip --proxy ${https_proxy} install -r ${project}/definitions/requirements.txt
    
            mkdir nexus_doc
            cd nexus_doc
            export SOURCE_DIR=../${project}/definitions
            python ../${project}/definitions/utils/build_preparation.py ../${project}/definitions
            make
            """
    
            try {
                container.sh """
                diff \
                    --recursive \
                    ${project}/nx-class-documentation/html \
                    nexus_doc/manual/build/html
                """
            } catch (e) {
                echo 'Caught exception after diff error, setting variable'
                diffError = true
            }
        } // stage
    
        if (diffError) {
            pipeline_builder.stage("Update NeXus HTML") {
                container.sh """
                export LC_ALL=en_US.utf-8
                export LANG=en_US.utf-8
                cd ${pipeline_builder.project}
                rm -rf nx-class-documentation/html
                cp -r ../nexus_doc/manual/build/html nx-class-documentation/
                git config user.email 'dm-jenkins-integration@esss.se'
                git config user.name 'cow-bot'
                git status --ignored
                git add --force nx-class-documentation
                git commit -m 'Update NeXus HTML documentation'
                """
            
                // Push any changes resulting from formatting
                withCredentials([
                    usernamePassword(
                        credentialsId: 'cow-bot-username-with-token',
                        usernameVariable: 'USERNAME',
                        passwordVariable: 'PASSWORD'
                    )
                ]) {
                    withEnv(["PROJECT=${pipeline_builder.project}"]) {
                        container.sh """
                        cd $PROJECT
                        git push https://$USERNAME:$PASSWORD@github.com/ess-dmsc/$PROJECT.git HEAD:$CHANGE_BRANCH
                        """
                     }  // withEnv
                }  // withCredentials
                error 'Updating NeXus HTML documentation'
            }  // stage
        }  // if
    } // if
}

def get_macos_pipeline() {
    return {
        node('macos') {
            cleanWs()
            dir("${project}") {
                stage('MacOS: Checkout') {
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
                stage('MacOS: Run non-ui tests') {
                    sh """
                    source ~/virtualenvs/${pipeline_builder.project}-${pipeline_builder.branch}/bin/activate
                    python -m pytest tests -s
                    """
                } // stage
                stage('MacOS: Run ui tests') {
                    sh """
                    source ~/virtualenvs/${pipeline_builder.project}-${pipeline_builder.branch}/bin/activate
                    python -m pytest ui_tests -s
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
