import os
import sys
from fabric.api import local, env, prefix, task
from fabric.context_managers import settings, lcd
env.host_string = "localhost"
VIRTUAL_ENV_WRAPPER = "/usr/local/bin/virtualenvwrapper.sh"

"""requires virtualenvwrapper/virtualenv/pip/git sets up a virtual env with ipython and django and creates the project"""


def require_variable(var_name):
    """ check if a variable exists in the environment """
    if var_name not in os.environ:
        sys.stderr.write("var_name %s not found.\n\n" % var_name)
        sys.exit(-1)

#we need to move to our script directory
#if we need to create


def require_function(func_name):
    if not function_exists(func_name):
        sys.stderr.write("func_name %s not found.\n\n" % func_name)
        sys.exit(-1)


def function_exists(func_name):
    return bool(local("which %s" % func_name, capture=True))

def project_setup(name, init_git, empty, requirements_in):
    if not empty: 
        if requirements_in:
            local("pip install -r %s" % requirements_in)
        else:
            local("pip install ipython")
            local("pip install django")


    local("django-admin.py startproject --template=https://github.com/fredkingham/django-simple-project/archive/master.zip %s" % name)

    with lcd(name):
        local("pip freeze > requirements.txt")
        if init_git:
            local("git init")

@task
def create(name, init_git = True, empty=False, requirements_in=False):
    require_variable("VIRTUALENVWRAPPER_HOOK_DIR")
    require_function("pip")
    require_function("python")
    require_function("git")

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
            local("rm -r %s" % name)


