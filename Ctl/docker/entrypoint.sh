#!/bin/sh

function migrate_all() {
  echo applying all migrations
  manage migrate
}

function collect_static() {
  echo collecting static files
  manage collectstatic --no-input
}


cd $SERVICE_HOME
case "$@" in
  "uwsgi" )
    echo starting uwsgi
    if [[ -z "$NO_MIGRATE" ]]; then
      migrate_all
    fi
    if [[ -z "$NO_COLLECT_STATIC" ]]; then
      collect_static
    fi
    echo launching uwsgi ${UWSGI_HTTP}
    exec venv/bin/uwsgi --ini etc/django-uwsgi.ini
    ;;
	# good to keep it as a separate arg incase we end up with multi stage migrations tho
  "migrate_all" )
    migrate_all
    ;;
  "run_tests" )
    source venv/bin/activate
    export DJANGO_SETTINGS_MODULE=devicectl.settings
    export RELEASE_ENV=run_tests
    cd main
    pytest tests/ -vv --cov-report=term-missing --cov-report=xml --cov=django_devicectl --cov=devicectl
    ;;
  "test_mode" )
    source venv/bin/activate
    cd main
    echo dropping to shell
    exec "/bin/sh"
    ;;
  "/bin/sh" )
    echo dropping to shell "$1" - "$@"
    exec $@
    ;;
  * )
    if [[ -z "$NO_MIGRATE" ]]; then
      migrate_all
    fi
    exec manage $@
    ;;
esac
