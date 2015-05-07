
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import boto.route53
import boto.ec2
import time
import subprocess

argv = sys.argv

if( len(argv) != 2 ):
        sys.exit("Require 1 Commnad-Line-args")

DNS = argv[1]
REGION = "ap-northeast-1"
CHECKING_INTERVAL = 5

conn = boto.ec2.connect_to_region(REGION)
route53_conn = boto.route53.connect_to_region('ap-northeast-1', profile_name='route53')

# route53 get public dns
zone = route53_conn.get_zone('mlkcca.com')
public_dns_name = zone.get_cname(DNS).to_print()
print("get public_dns_name " + public_dns_name) 


# ec2 use
def get_instance(public_dns_name):
    reservations = conn.get_all_instances()
    for reservation in reservations:
        for instance in reservation.instances:
            print(instance.public_dns_name)
            if str(instance.public_dns_name) + "." == str(public_dns_name):
                return instance

instance = get_instance(public_dns_name)
print instance
instance.reboot()
time.sleep(CHECKING_INTERVAL)

while subprocess.call(["ssh","-i","/home/ubuntu/tokyo.pem","-o","StrictHostKeyChecking=no","ubuntu@"+instance.public_dns_name,"exit"]) != 0:
        print "wait 5"
        time.sleep(CHECKING_INTERVAL)
        
