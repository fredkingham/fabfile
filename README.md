fabfile
=======
curl -O https://raw.github.com/fredkingham/fabfile/master/fabfile.py

creates everything in the directory so run this from your script root

run with fab:create{{ name }}
cd {{ name }}
workon {{ name }}

remove with fab:remove{{ name }}
