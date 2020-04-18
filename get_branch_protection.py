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
        print(git)
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
            #for repo in git.get_user().get_repos():
            #    print(repo.name)
        except GithubException as e:
            print("GithubException: {0}".format(e))
    else: 
        print("Error getting git is None")

def import_branch_protection(branch):
    return_code, stdout, stderr  = terraform.import_cmd('github_branch_protection.feature-extraction-service','feature-extraction-service:master')
    state=terraform.read_state_file()
    return state.__dict__


def main():
    print("start")
    init_logger()
    print(git)
    print("zzz")
    repos = get_git_repos()
    for repo in repos:
        print(repo.name)


if __name__ == '__main__':
    main()