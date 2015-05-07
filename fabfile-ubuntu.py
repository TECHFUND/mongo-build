#
# fabfile.py (milkcocoa/db)
#
from fabric.api import sudo, env, run, roles, task, cd, put
from fabric.contrib import project, console
import os


@task
def all():
    install_mongodb_common()
    install_mongodb()
    put("conf/mongodb.conf", "/etc/mongodb.conf", use_sudo=True)
    mount_fs()
    restart_mongod()

def install_mongodb_common():
    sudo("apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10")
    sudo("sh -c \"echo deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen > /etc/apt/sources.list.d/mongo.list\"")
    sudo("apt-get update -y")
    sudo("DEBIAN_FRONTEND=noninteractive apt-get -y upgrade ")

def install_mongod():
    sudo("apt-get install mongodb-org-server -y")

def install_mongos():
    sudo("apt-get install mongodb-org-mongos -y")

def install_mongodb():
    sudo("apt-get install mongodb-org -y")

def install_mongo_tools():
    sudo("apt-get install mongodb-org-tools -y")

def install_mongo_shell():
    sudo("apt-get install mongodb-org-shell -y")

@task
def mount_fs():
  #sudo("umount /dev/xvdb")
  sudo("mkfs -t ext4 /dev/xvdb")
  sudo("mkdir /mnt/data")
  sudo("chown mongodb /mnt/data")
  sudo("mount /dev/xvdb /mnt/data")
  sudo("sh -c \"echo /dev/xvdb /mnt/data ext4 noatime 0 0 > /etc/fstab\"")
  sudo("chown mongodb /mnt/data")

def restart_mongod():
    sudo("service mongod restart")
