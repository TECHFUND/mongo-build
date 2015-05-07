#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import boto.route53

argv = sys.argv

if( len(argv) != 3 ):
    sys.exit("Require 2 Commnad-Line-args")


OLD_DNS = argv[1]
NEW_DNS = argv[2]

# route53 use
conn = boto.route53.connect_to_region('ap-northeast-1', profile_name='route53')
zone = conn.get_zone('mlkcca.com')
public_dns_name = zone.get_cname(OLD_DNS).to_print()
zone.update_cname(NEW_DNS, public_dns_name)
zone.update_cname(OLD_DNS, "none")
