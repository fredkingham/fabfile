import os
import sys
from fabric.api import local, env, prefix, task
from fabric.context_managers import settings, lcd
env.host_string = "localhost"
VIRTUAL_ENV_WRAPPER = "/usr/local/bin/virtualenvwrapper.sh"

"""requires virtualenvwrapper/virtualenv/pip/git sets up a virtual env with ipython and django and creates the project"""


class Project(name):
    def __init__(name):
        self.project_dir = "%s_project" % name
        self.application_dir = os.path.join(self.project_dir, name)
        self.front_end_dir = os.path.join(self.application_dir, "front_end")
        self.app_name = names


def require_variable(var_name):
    """ check if a variable exists in the environment """
    if var_name not in os.environ:
        sys.stderr.write("var_name %s not found.\n\n" % var_name)
        sys.exit(-1)

#we need to move to our script directory

def require_function(func_name):
    if not function_exists(func_name):
        sys.stderr.write("func_name %s not found.\n\n" % func_name)
        sys.exit(-1)


def function_exists(func_name):
    return bool(local("which %s" % func_name, capture=True))

def get_project_name(name):
    return "%s_project" % name

def setup_front_end(project):
    with lcd(project.front_end):
        local("npm install brunch")
        local("node_modules/brunch/bin/brunch new static --skeleton https://github.com/fredkingham/brunch-with-cantaloupe.git")

def project_setup(name, init_git, empty, requirements_in):
    if not empty: 
        if requirements_in:
            local("pip install -r %s" % requirements_in)
        else:
            local("pip install ipython")
            local("pip install django")
            local("pip install ipdb")
            local("pip install mock")

    project = Project(name)

    local("django-admin.py startproject --template=https://github.com/fredkingham/django-project-skeleton/archive/master.zip %s" % name)
    local("mv %s %s" % (name, project.project_name)

    setup_front_end(project)

    with lcd(project.project_name):
        local("pip freeze > requirements.txt")
        if init_git:
            local("git init")



@task
def create(name, init_git = True, empty=False, requirements_in=False):
    require_variable("VIRTUALENVWRAPPER_HOOK_DIR")
    require_function("pip")
    require_function("python")
    require_function("git")
    require_function("npm")

    with prefix("source %s" % VIRTUAL_ENV_WRAPPER):
        with settings(warn_only=True):
            virtual_envs = local("workon", capture=True).splitlines()
            if name in virtual_envs:
                raise Exception("virtual env %s already exists" % name)

    with prefix("source %s" % VIRTUAL_ENV_WRAPPER):
        local("mkvirtualenv --no-site-packages %s" % name)

    with prefix("source %s" % VIRTUAL_ENV_WRAPPER):
        with prefix("workon %s" % name):
            project_setup(name, init_git, empty, requirements_in)

@task
def remove(name):
    with prefix("source %s" % VIRTUAL_ENV_WRAPPER):
        with settings(warn_only=True):
            local("rmvirtualenv %s" % name)
            local("rm -rf %s" % get_project_name(name))


