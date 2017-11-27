// vim: ft=groovy
properties([
    buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '3', daysToKeepStr: '', numToKeepStr: '3')),
    pipelineTriggers([[$class: 'PeriodicFolderTrigger', interval: '2d']])
])

node('cloud') {
    def cloud_image = 'https://jenkins.liquiddemo.org/job/liquidinvestigations/job/factory/job/master/lastSuccessfulBuild/artifact/cloud-x86_64-image.tar.xz'
    def liquid_prerequisites_cloud_image = 'https://jenkins.liquiddemo.org/job/setup-prerequisites/job/master/lastSuccessfulBuild/artifact/liquid-cloud-x86_64-prerequisites.img.xz'
    stage('CLOUD: Host Debug Information') {
        sh 'set -x && hostname && uname -a && free -h && df -h'
    }
    deleteDir()
    checkout scm
    try {
        stage('CLOUD: Build a Factory & Prepare Cloud Image') {
            sh 'git clone https://github.com/liquidinvestigations/factory'
            sh 'mkdir -pv factory/images/cloud-x86_64/'
            dir('factory/images/cloud-x86_64') {
                sh "wget -q $cloud_image -O tmp.tar.xz;"
                sh 'xzcat tmp.tar.xz | tar x'
                sh 'rm tmp.tar.xz'
            }
        }
        stage('CLOUD: Prepare the build') {
            sh 'cp jenkins-config.yml ansible/vars/config.yml'
            sh 'mkdir images'
            sh "wget -q $liquid_prerequisites_cloud_image -O images/pre.img.xz"
            sh 'xzcat images/pre.img.xz > images/ubuntu-x86_64-raw.img'
            sh 'rm images/pre.img.xz'
        }
        stage('CLOUD: Build Image') {
            sh 'factory/factory run --smp 2 --memory 2048 --share .:/mnt/setup --share images:/mnt/images /mnt/setup/bin/jenkins_build /mnt/setup/bin/build_image cloud --image /mnt/images/ubuntu-x86_64-raw.img'
        }
        stage('CLOUD: Test and Archive') {
            parallel(
                first_boot: {
                    stage("CLOUD: Run first boot") {
                        sh 'mkdir factory/images/liquid'
                        sh 'cp images/ubuntu-x86_64-raw.img factory/images/liquid/disk.img'
                        sh 'factory/factory run --share .:/mnt/setup --share factory/images/liquid:/mnt/liquid /mnt/setup/bin/with-image-chroot /mnt/liquid/disk.img bash < ci/prepare-image-for-testing'
                        sh 'echo \'{"login": {"username": "liquid", "password": "liquid"}}\' > factory/images/liquid/config.json'
                        sh 'factory/factory run --image liquid --smp 2 --memory 2048  --share .:/mnt/setup PYTHONUNBUFFERED=yeah /mnt/setup/bin/run_first_boot_tests.py'
                        junit 'tests/results/*.xml'
                    }
                },
                archive_raw_image: {
                    stage('CLOUD: Archive Raw Image') {
                        sh 'xz -1 < images/ubuntu-x86_64-raw.img > liquid-cloud-x86_64-raw.img.xz'
                        archiveArtifacts 'liquid-cloud-x86_64-raw.img.xz'
                    }
                }
            )
        }
    } finally {
        deleteDir()
    }
}
