#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import boto.ec2
import boto.route53
import datetime
import time
import pickle

argv = sys.argv

if( len(argv) != 4 ):
    sys.exit("Require 3 Command-Line-arg")

DNS = argv[1]
NAME = argv[2] + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
DESCRIPTION = argv[3]

REGION = "ap-northeast-1"

# route53 use
route53_conn = boto.route53.connect_to_region('ap-northeast-1', profile_name='route53')
zone = route53_conn.get_zone('mlkcca.com')
public_dns_name = zone.get_cname(DNS).to_print()
print("get public_dns_name " + public_dns_name) 

# ec2 use
conn = boto.ec2.connect_to_region(REGION)
def create_image(public_dns_name):
    reservations = conn.get_all_instances()
    for reservation in reservations:
        for instance in reservation.instances:
            if str(instance.public_dns_name) + "." == str(public_dns_name):
                print("create_image instance-id : " + instance.id + " dns_name " + public_dns_name)
                return (instance, instance.create_image(NAME, description=DESCRIPTION))
            

(image_instance, image_id) = create_image(public_dns_name)
image = conn.get_image(image_id)

while image.update() == "pending":
    print(image.update())
    time.sleep(5)
    
    
saved_images = {}
with open("ami-images.pickle","rb") as f:
    saved_images = pickle.load(f)

if saved_images.has_key(argv[2]):
    old_image_id = saved_images[argv[2]]
    old_image = conn.get_image(old_image_id)
    if  old_image is not None:
        old_image.deregister()
    
saved_images[argv[2]] = image_id

with open("ami-images.pickle","wb") as f:
    pickle.dump(saved_images, f)



# terminate old instances
image_instance.terminate()
