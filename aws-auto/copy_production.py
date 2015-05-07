import utility
import sys, multiprocessing


def copy_image(key_filename, deploy_name, production_name, old_delete=True):
    aws = utility.AwsUtility(key_filename)
    aws.copy_image(deploy_name, production_name, old_delete=old_delete)
    
def main():
    argv = sys.argv
    if( len(argv) != 3 ):
        sys.exit("Require pemfile path")
    start_aws_job(argv[1], argv[2])
    
def start_aws_job(key_filename, select_instance):
    if select_instance == "top":
        copy_image(key_filename, "top deploy", "top production")
    elif select_instance == "manage":
        copy_image(key_filename, "manage deploy", "manage production")
    elif select_instance == "app":
        copy_image(key_filename, "app deploy", "app production", old_delete=False)
    elif select_instance == "logger":
        copy_image(key_filename, "logger build", "logger production")
    
if __name__ == '__main__':
    main()
