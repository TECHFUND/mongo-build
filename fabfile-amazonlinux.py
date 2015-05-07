#
# fabfile.py (milkcocoa/db)
#
from fabric.api import sudo, env, run, roles, task, cd, put
from fabric.contrib import project, console
import os


@task
def all():
    install_mongodb()
    conf_mongodb()
    mount_fs()
    restart_mongod()
    add_user()

def install_mongodb():
    put("conf/mongodb.repo", "/etc/yum.repos.d/mongodb.repo", use_sudo=True)
    sudo("yum install mongodb-org -y")


@task
def conf_mongodb():
    put("conf/mongodb.conf", "/etc/mongodb.conf", use_sudo=True)

@task
def add_user():
    sudo("mongo test --eval 'db.createUser({user : \"sgtn\", \
		pwd : \"techfund88\", \
		roles : [{role:\"dbAdmin\", db: \"staging\"}]})'")

@task
def mount_fs():
  sudo("umount /dev/xvdb")
  sudo("mkfs -t ext4 /dev/xvdb", warn_only=True)
  sudo("mkdir /mnt/data", warn_only=True)
  sudo("chown mongodb /mnt/data", warn_only=True)
  sudo("mount /dev/xvdb /mnt/data")
  sudo("sh -c \"echo /dev/xvdb /mnt/data ext4 noatime 0 0 > /etc/fstab\"")
  sudo("chown mongodb /mnt/data")

@task
def restart_mongod():
    sudo("service mongod restart")
