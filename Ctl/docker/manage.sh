DEVICECTL_HOME=/srv/devicectl

. $DEVICECTL_HOME/venv/bin/activate
cd $DEVICECTL_HOME/main

./manage.py $@
