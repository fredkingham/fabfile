from fabric.api import env, task, sudo, cd, run, local, prefix, lcd
from fabric.contrib.project import rsync_project
from fabric.contrib.files import sed

env.key_filename = "nother.pem"
env.hosts = ["46.137.84.215"]
env.user = "ec2-user"


@task
def push_to_prod():
    local("pip freeze > requirements.txt")
    local('git commit -a -m "updating files"')
    local("git push origin master")
    remote_directory = "/home/ec2-user/figg_project"
    local_directory = "figg"
    rsync_project(remote_dir = remote_directory, local_dir = local_directory)
    with cd("/home/ec2-user/figg_project/figg/figg"):
        sed("settings.py", "DEBUG = True", "DEBUG = False")
    with cd("/home/ec2-user/figg_project/figg"):
        run("~/.virtualenvs/figg/bin/python manage.py collectstatic --noinput")
        run("~/.virtualenvs/figg/bin/python manage.py syncdb")
        
    with prefix("source /usr/bin/virtualenvwrapper.sh && workon figg"):
        run("pip install -r requirements.txt")

    sudo("service httpd restart")
