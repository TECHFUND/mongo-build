#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto.ec2
import boto.route53
import time
import datetime
import socket
import sys
import json
import subprocess
import re

REGION = "ap-northeast-1"
Availability_ZONE = "ap-northeast-1c"
KEY_PAIR="privatekey"

class AwsUtility:
    def __init__(self, pemfile_name):
        self.conn = boto.ec2.connect_to_region(REGION)
        self.route53_conn = boto.route53.connect_to_region(REGION, profile_name='route53')
        self.pemfile_name = pemfile_name
        self.block_device_map = None

    def create_instance(self, ami_id, instance_type, security_groups, tags):
        reserved = self.conn.run_instances(
            ami_id,
            key_name=KEY_PAIR,
            instance_type=instance_type,
            security_groups=security_groups,
            placement=Availability_ZONE,
            block_device_map=self.block_device_map)
        instance = reserved.instances[0]
        self.conn.create_tags([instance.id], tags)
        return TmpInstance(instance, self.conn, self.pemfile_name)


    def create_instance_from_image_name(self, image_name, instance_type, security_groups, tags):
        image = self.get_ami(image_name)
        if tags.has_key("Name"):
            tags["Name"] = tags["Name"] + " : " + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        if image:
            return self.create_instance(image.id, instance_type, security_groups, tags)
        
    def create_instance_from_file(self, jsonfile):
        jsonData = {}
        with open(jsonfile,"r") as f:
            jsonData = json.load(f)
        if jsonData.has_key("ami-name"):
            return self.create_instance_from_image_name(jsonData["ami-name"], jsonData["instance-type"], jsonData["security-groups"], jsonData["tags"])
        else:
            return self.create_instance(jsonData["ami"], jsonData["instance-type"], jsonData["security-groups"], jsonData["tags"])

    def get_ami(self, name):
        images =  self.conn.get_all_images(owners='self')
        pattern = re.compile(name + ".*") 
        for image in images:
            if image.tags.has_key("Name") and pattern.match(image.tags["Name"]) and image.update() == "available":
                return image
        return None

    def set_ami(self, name, ami_image, old_delete=True):
        old_image = self.get_ami(name)
        ami_image.add_tag('Name',value=name + " " + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
        if old_image and old_delete:
            print "deregister old_image : %s " % old_image.id
            old_image.deregister()

    def route_change(self, dns, value, old_instance_delete=True,sleep_time=60,zone="mlkcca.com"):
        zone = self.route53_conn.get_zone(zone)
        old_value = zone.get_cname(dns).to_print()
        print dns + " : old value : " + old_value
        zone.update_cname(dns,value)
        if old_instance_delete:
            instance = self.get_instance_from_dns(old_value)
            if instance:
                time.sleep(sleep_time)
                instance.terminate()

    def get_instance_from_dns(self, dns):
        reservations = self.conn.get_all_instances()
        for reservation in reservations:
            for instance in reservation.instances:
                if instance.public_dns_name + "." == dns:
                    return instance

    def add_record(self, cname, value, ttl=60, zone="mlkcca.com"):
        zone = self.route53_conn.get_zone(zone)
        zone.add_cname(cname, value, ttl=ttl)

    def copy_image(self, deploy_name, name, old_delete=True):
        deploy_image = self.get_ami(deploy_name)
        if deploy_image:
            image_id = self.conn.copy_image(REGION, deploy_image.id, name + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')).image_id
            image = self.conn.get_image(image_id)
            while image.update() == "pending":
                print("image status : %s " % image.update())
                time.sleep(5)
            self.set_ami(name, image, old_delete=old_delete)
        
class TmpInstance(object):
    def __init__(self, instance, conn, pemfile_name):
        self.instance = instance
        self.conn = conn
        self.pemfile_name = pemfile_name
        while self.instance.state != "running":
            time.sleep(5)
            self.instance.update()
            print "check! status : %s" % self.instance.state
        self.instance_status_check()
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        print "terminate! : %s" % self.instance.public_dns_name
        self.instance.terminate()
        
    def reboot(self):
        print "reboot!"
        self.instance.reboot()
        self.ssh_connection_check()

    def create_image(self,name, description):
        print "create image!"
        name_and_date = name + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        image_id = self.instance.create_image(name_and_date, description=description)
        image = self.conn.get_image(image_id)
        while image.update() == "pending":
            print("image status : %s " % image.update())
            time.sleep(5)
        return image
            
        
    def ssh_connection_check(self):
        print "ssh connection check"
        time.sleep(60)
        while subprocess.call(["ssh","-i",self.pemfile_name,"-o","StrictHostKeyChecking=no","ubuntu@"+self.instance.public_dns_name,"exit"]) != 0:
            time.sleep(5)
            print "ssh connection check"

    def instance_status_check(self):
        instance_status = self.get_instance_status()
        while instance_status.system_status.status != "ok" or not instance_status.instance_status.status:
            time.sleep(5)
            instance_status = self.get_instance_status()
            print instance_status.system_status.status + "/" + instance_status.instance_status.status

        
    def get_instance_status(self):
        existing_instances_status = self.conn.get_all_instance_status()
        for instance_status in existing_instances_status:
            if instance_status.id == self.instance.id:
                return instance_status

    
