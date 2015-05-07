import sys, os
import boto.ec2
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/aws-auto')
import utility
import fabfile
from datetime import datetime
from fabric.api import settings

AWS_JSON_FILE = "aws.json"
CREATE_IMAGE_NAME = "mongodb-deploy"
CREATE_IMAGE_DESCRIPTION = "mongodb deploy from script"
CREATE_IMAGE_TAG_NAME = "mongodb deploy"

def main():
    argv = sys.argv
    if( len(argv) != 3 ):
        sys.exit("Require DB size parameter")
    start_aws_job(argv[1], int(argv[2]))

def start_aws_job(key_filename, size):
    aws = utility.AwsUtility(key_filename)
    aws.block_device_map = get_ebs_map(size)
    with aws.create_instance_from_file(AWS_JSON_FILE) as instance:
        build(instance, key_filename)
        instance.reboot()
        image = instance.create_image(CREATE_IMAGE_NAME, CREATE_IMAGE_DESCRIPTION)
        aws.set_ami(CREATE_IMAGE_TAG_NAME, image)


def build(instance, key_filename):
    with settings(host_string=instance.instance.public_dns_name,
                  user = "ubuntu",
                  key_filename=key_filename):
        fabfile.all()


def get_ebs_map(size):
    dev_sda1 = boto.ec2.blockdevicemapping.EBSBlockDeviceType(volume_type="standard", delete_on_termination=True)
    dev_sda1.size = 8
    dev_sdb = boto.ec2.blockdevicemapping.EBSBlockDeviceType(volume_type="gp2", delete_on_termination=True)
    dev_sdb.size = size
    bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
    bdm['/dev/sda1'] = dev_sda1
    bdm['/dev/sdb'] = dev_sdb
    return bdm

if __name__ == '__main__':
    main()
