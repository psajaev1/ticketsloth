from fabric.api import run, sudo, env, cd, put, local
from fabric.contrib.files import exists

# globals
env.project = 'ticketsloth'
env.psql_user = 'ticketsloth'
env.psql_password = 'oc+c.3jqKfIeeZG'
env.psql_db = 'ticketsloth'
env.git_url = 'git@github.com:buildthis/Tixchange.git'
env.forward_agent = True


def vagrant():
    # change from the default user to 'vagrant'
    env.user = 'vagrant'
    # connect to the port-forwarded ssh
    env.hosts = ['127.0.0.1:2222']

    # use vagrant ssh key
    result = local('vagrant ssh_config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1]
    env.branch = 'master'
    env.server = 'production'


def dev():
    env.server = 'dev'
    env.branch = 'develop'
    env.hosts = ['45.55.72.58']
    env.user = 'root'


def production():
    env.server = 'production'
    env.branch = 'develop'
    env.hosts = ['128.199.190.151']
    env.user = 'root'

# Webserver configuration
def setup_server():
    install_required_software()
    create_directories()
    configure_webserver()
    configure_application_server()
    configure_database()
    clone_project()


def install_required_software():
    sudo('apt-get -y update')
    sudo('apt-get -y upgrade')
    sudo('apt-get -y install python-setuptools nginx postgresql-client libpq-dev libjpeg-dev git git-core zlib1g-dev python-dev postgresql-server-dev-9.3 postgresql-contrib mosh gunicorn')
    sudo('easy_install pip')
    sudo('pip install virtualenv')


def create_directories():
    sudo('mkdir /webapps/')
    sudo('mkdir /webapps/%s' % env.project)
    sudo('mkdir -p /var/www/static')
    sudo('mkdir -p /var/www/media')
    sudo('chmod 777 /var/www/static')
    sudo('chmod 777 /var/www/media')


def configure_webserver():
    sudo('rm /etc/nginx/sites-enabled/default')


def configure_application_server():
    sudo('virtualenv /webapps/venv')


def configure_database():
    sudo('psql -c "CREATE ROLE {0} WITH PASSWORD \'{1}\' NOSUPERUSER CREATEDB NOCREATEROLE LOGIN;"'.format(env.psql_user, env.psql_password), user='postgres')
    sudo('psql -c "CREATE DATABASE {0} WITH OWNER={1} TEMPLATE=template0 ENCODING=\'utf-8\';"'.format(env.psql_db, env.psql_user), user='postgres')


def clone_project():
    # Make sure you run ssh-add -K and enable ssh agent forwarding

    with cd("/webapps/%s" % env.project):
        run('git clone %s .' % env.git_url)
        run('git checkout %s' % env.branch)


def update_server():
    sudo('apt-get -y update')
    sudo('apt-get -y upgrade')


def deploy():
    with cd("/webapps/%s" % env.project):
        run('git pull')
    upload_settings()
    if env.server == "dev":
        virtualenv('pip install -r requirements/dev.txt')
    if env.server == "production":
        virtualenv('pip install -r requirements/production.txt')
    copy_placeholder_images()
    virtualenv('python manage.py migrate --noinput')
    virtualenv('python manage.py collectstatic --noinput')
    update_webserver_config()
    update_webapp_config()
    make_whoosh_index_writable()


def upload_settings():
    file_name = ''
    if env.server == "dev":
        file_name = "dev_settings.py"
    if env.server == "production":
        file_name = "production_settings.py"
    put('config/%s' % file_name, '/webapps/%s/config/dev_settings.py' % env.project)


def update_webserver_config():
    if exists('/etc/nginx/sites-enabled/nginx.conf'):
        sudo('rm /etc/nginx/sites-enabled/nginx.conf')
    sudo('cp /webapps/%s/config/nginx.conf /etc/nginx/sites-enabled/' % env.project)
    sudo('service nginx restart')


def update_webapp_config():
    if exists('/etc/init/%s.conf' % env.project):
        sudo('rm /etc/init/%s.conf' % env.project)
    sudo('cp /webapps/%s/config/%s.conf /etc/init/' % (env.project, env.project))
    sudo('service %s restart' % env.project)


def createsuperuser():
    virtualenv('python manage.py createsuperuser')


def make_whoosh_index_writable():
    sudo('chmod 777 /webapps/%s/config/whoosh_index' % env.project)
    sudo('chmod 777 /webapps/%s/config/whoosh_index/*' % env.project)


def update_search_index():
    virtualenv('python manage.py update_index')
    sudo('chmod 777 /webapps/%s/config/whoosh_index' % env.project)
    sudo('chmod 777 /webapps/%s/config/whoosh_index/*' % env.project)


def rebuild_search_index():
    virtualenv('python manage.py rebuild_index')
    sudo('chmod 777 /webapps/%s/config/whoosh_index' % env.project)
    sudo('chmod 777 /webapps/%s/config/whoosh_index/*' % env.project)


def copy_placeholder_images():
    sudo('mkdir -p /var/www/media/images')
    sudo('mkdir -p /var/www/media/images/placeholders')
    sudo('yes | cp -rf /webapps/%s/static/images/placeholders/* /var/www/media/images/placeholders/' % env.project)

def virtualenv(command):
    with cd('/webapps/%s' % env.project):
        run('source /webapps/venv/bin/activate' + '&&' + command)
