from fabric.api import env, task, sudo, settings, cd, run
from fabric.contrib.project import rsync_project
from fabric.contrib.files import sed

env.key_filename = "nother.pem"
env.hosts = ["46.137.84.215"]
env.user = "ec2-user"
deploy_user = "djangotest"
deploy_password = "ojzwdasdf"


@task
def push_to_prod():
    remote_directory = "/home/ec2-user/figg_project"
    local_directory = "figg"
    rsync_project(remote_dir = remote_directory, local_dir = local_directory)
    with cd("/home/ec2-user/figg_project/figg/figg"):
        sed("settings.py", "DEBUG = True", "DEBUG = False")
    with cd("/home/ec2-user/figg_project/figg"):
        run("python manage.py collectstatic --noinput")

    sudo("service httpd restart")

