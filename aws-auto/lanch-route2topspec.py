#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto.ec2
import boto.route53
import time
import datetime
import socket
import sys

argv = sys.argv
arg_len = len(argv)
if( arg_len != 6 ):
    sys.exit("Require 5 Command-Line-arg")

UPDATE_CNAME_NAME = argv[1]
AMI = argv[2]
INSTANCE_TYPE = argv[3]
SECURITY_GROUPS = [argv[4]]
TAGS = eval(argv[5])
TAGS["Name"] = TAGS["Name"] + " at time : " + datetime.datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
    
REGION = "ap-northeast-1"
CHECKING_INTERVAL = 5
KEY_PAIR="privatekey"

Availability_ZONE = "ap-northeast-1a"

conn = boto.ec2.connect_to_region(REGION)

# terminate old instances
try:
    ip = socket.gethostbyname(UPDATE_CNAME_NAME)
    reservations = conn.get_all_instances()
    for reservation in reservations:
        instance = reservation.instances[0]
        if str(instance.private_ip_address) == str(ip) and instance.state == "running":
            print("terminalt : " + instance.id)
            conn.terminate_instances(instance_ids=[instance.id])
except socket.gaierror, msg:
    print msg


# create new instances
reserved = conn.run_instances(AMI,
                              key_name=KEY_PAIR,
                              security_groups=SECURITY_GROUPS,
                              instance_type=INSTANCE_TYPE,
                              placement=Availability_ZONE)
instance = reserved.instances[0]
conn.create_tags([instance.id], TAGS)

def check_status(instance):
    print "check! status : %s" % instance.state
    return instance.state
    
while check_status(instance) != "running":
    time.sleep(CHECKING_INTERVAL)
    instance.update()

public_dns_name = instance.public_dns_name


# route53 use
conn = boto.route53.connect_to_region('ap-northeast-1', profile_name='route53')
zone = conn.get_zone('mlkcca.com')
zone.update_cname(UPDATE_CNAME_NAME, public_dns_name)


# status check
def get_instance_status():
    conn = boto.ec2.connect_to_region(REGION)
    existing_instances_status = conn.get_all_instance_status()
    for instance_status in existing_instances_status:
        if instance_status.id == instance.id:
            return instance_status



while True:
    instance_status = get_instance_status()
    time.sleep(CHECKING_INTERVAL)
    print instance_status.system_status.status + "/" + instance_status.instance_status.status
    if instance_status.system_status.status == "ok" and instance_status.instance_status.status:
        break
    
