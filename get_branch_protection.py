import os
import sys
from github import Github
from python_terraform import *
import logging

git = None
terraform = None

#init Github instance 
if 'GITHUB_TOKEN' not in os.environ:
    print("Please set the environmen variable GITHUB_TOKEN")
    sys.exit(1)
else:
    #print("Github token is: " + str(os.environ['GITHUB_TOKEN']))
    try:
        git = Github(os.environ['GITHUB_TOKEN'])
        print("Git was successfully set")
    except GithubException as e:
        print("GithubException: {0}".format(e))
        print("Error connectin to Github ")
        sys.exit(1)

#init Terraform instance
try:
    terraform = Terraform()
except:
    print("Error initiation Terraform")
    sys.exit(1)


def init_logger():
    logging.basicConfig(filename='importer.log',level=logging.DEBUG)

def get_git_repos():
    if git is not None:
        try:
            return git.get_user().get_repos()
        except GithubException as e:
            print("GithubException: {0}".format(e))
    else: 
        print("Error getting git is None")

def import_branch_protection(repo):
    return_code, stdout, stderr  = terraform.import_cmd('github_branch_protection.{}'.format(str(repo)),'{}:master'.format(str(repo)))
    state=terraform.read_state_file()
    return state.__dict__

def main():
    print("start")
    init_logger()
    
    repos = get_git_repos()
    repo_names = [repo.name for repo in repos]
    for repo_name in repo_names:
        print(repo_name)


if __name__ == '__main__':
    main()