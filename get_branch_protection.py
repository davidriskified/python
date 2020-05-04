import os
import sys
from github import Github
from python_terraform import *
import logging
import json

current_path = os.path.dirname(os.path.realpath(__file__))

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

def set_fields(tfstate):

    #general
    repository = str(tfstate['resources'][0]['instances'][0]['attributes']['repository'])
    branch = str(tfstate['resources'][0]['instances'][0]['attributes']['branch'])
    enforce_admins = str(tfstate['resources'][0]['instances'][0]['attributes']['enforce_admins']).lower()
    require_signed_commits = str(tfstate['resources'][0]['instances'][0]['attributes']['require_signed_commits']).lower()
    general = (
    '\n'
    '\t repository = "%s" \n'
    '\t branch = "%s" \n'
    '\t enforce_admins = %s \n'
    '\t require_signed_commits = %s \n' % (repository, branch, enforce_admins, require_signed_commits)
    )

    # Required status check
    if not tfstate['resources'][0]['instances'][0]['attributes']['required_status_checks']:
        required_status_checks = ''
    else:
        required_status_checks__strict = str(tfstate['resources'][0]['instances'][0]['attributes']['required_status_checks'][0]['strict']).lower() 
        required_status_checks__contexts = json.dumps(tfstate['resources'][0]['instances'][0]['attributes']['required_status_checks'][0]['contexts'])
        #required_status_checks__include_admins = str(tfstate['resources'][0]['instances'][0]['attributes']['required_status_checks'][0]['include_admins']).lower()
        required_status_checks = (
        '\n'
        '\t required_status_checks { \n'
        '\t\t strict   = %s \n'
        '\t\t contexts = %s \n'
        #'\t\t include_admins = %s \n'
        '\t } \n' % (required_status_checks__strict,
        required_status_checks__contexts))
        #, required_status_checks__include_admins) )

    if not tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews']:
        required_pull_request_reviews = ''
    else:
        required_pull_request_reviews__dismiss_stale_reviews = str(tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews'][0]['dismiss_stale_reviews']).lower()
        required_pull_request_reviews__dismissal_users = json.dumps(tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews'][0]['dismissal_users'])
        required_pull_request_reviews__dismissal_teams = json.dumps(tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews'][0]['dismissal_teams'])
        required_pull_request_reviews__require_code_owner_reviews = str(tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews'][0]['require_code_owner_reviews']).lower()
        required_pull_request_reviews__required_approving_review_count = str(tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews'][0]['required_approving_review_count'])
        required_pull_request_reviews = (
        '\n'
        '\t required_pull_request_reviews { \n'
        '\t\t dismiss_stale_reviews = %s \n'
        '\t\t dismissal_users = %s \n'
        '\t\t dismissal_teams = %s \n'
        '\t\t require_code_owner_reviews = %s \n'
        '\t\t required_approving_review_count = %s \n'
        '\t } \n' % (required_pull_request_reviews__dismiss_stale_reviews,
        required_pull_request_reviews__dismissal_users,
        required_pull_request_reviews__dismissal_teams,
        required_pull_request_reviews__require_code_owner_reviews,
        required_pull_request_reviews__required_approving_review_count))

    if not tfstate['resources'][0]['instances'][0]['attributes']['restrictions']:
        restrictions = ''
    else:
        restrictions_checks__users = json.dumps(tfstate['resources'][0]['instances'][0]['attributes']['restrictions'][0]['users'])
        restrictions_checks__teams = json.dumps(tfstate['resources'][0]['instances'][0]['attributes']['restrictions'][0]['teams'])
        restrictions__apps = json.dumps(tfstate['resources'][0]['instances'][0]['attributes']['restrictions'][0]['apps']) 
        restrictions = (
        '\n'
        '\t restrictions { \n'
        '\t\t users = %s \n'
        '\t\t teams = %s \n'
        '\t\t apps = %s \n'
        '\t } \n' % (restrictions_checks__users,
        restrictions_checks__teams,
        restrictions__apps))

    if not os.path.exists(current_path + '/output'):
        os.makedirs(current_path + '/output')

    tf_content = ('resource "github_branch_protection" ' + '"' + str(repository.replace('-', '_')) + '"' + ' { \n'
                + str(general)
                + str(required_status_checks)
                + str(required_pull_request_reviews)
                + str(restrictions) +
            '\n}\n')

    f = open(current_path + '/output/' + str(repository.replace('-', '_')) + '.tf', "w")
    f.write(tf_content)
    f.close()

def read_tfstate_file(repo):
    tfstate = import_branch_protection(repo)

    print ("enforce_admins: " + str(tfstate['resources'][0]['instances'][0]['attributes']['enforce_admins']).lower())
    print ("branch: " + str(tfstate['resources'][0]['instances'][0]['attributes']['branch']))
    print ("repository: " + str(tfstate['resources'][0]['instances'][0]['attributes']['repository']) )
    print ("require_signed_commits: " + str(tfstate['resources'][0]['instances'][0]['attributes']['require_signed_commits']).lower())
    # required_pull_request_reviews
    if not tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews']:
        print ("required_pull_request_reviews: []")
    else:
        print ("required_pull_request_reviews.include_admins: " + str(tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews'][0]['include_admins']).lower())
        print ("required_pull_request_reviews.require_code_owner_reviews: " + str(tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews'][0]['require_code_owner_reviews']).lower())
        print ("required_pull_request_reviews.required_approving_review_count: " + str(tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews'][0]['required_approving_review_count']))
        print ("required_pull_request_reviews.dismiss_stale_reviews: " + str(tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews'][0]['dismiss_stale_reviews']).lower())
        print ("required_pull_request_reviews.dismissal_users: " +  json.dumps(tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews'][0]['dismissal_users']))
        print ("required_pull_request_reviews.dismissal_teams: " +  json.dumps(tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews'][0]['dismissal_teams']))

    # required_status_checks
    if not tfstate['resources'][0]['instances'][0]['attributes']['required_status_checks']:
        print("required_status_checks: []")
    else:
        print ( "required_status_checks.contexts: " + json.dumps(tfstate['resources'][0]['instances'][0]['attributes']['required_status_checks'][0]['contexts']) )
        print ( "required_status_checks.include_admins: " + str(tfstate['resources'][0]['instances'][0]['attributes']['required_status_checks'][0]['include_admins']).lower() )
        print ( "required_status_checks.strict: " + str(tfstate['resources'][0]['instances'][0]['attributes']['required_status_checks'][0]['strict']).lower() )

    # restrictions
    if not tfstate['resources'][0]['instances'][0]['attributes']['restrictions']:
        print("restrictions: []")
    else:
        print ("restrictions.apps :" + json.dumps(tfstate['resources'][0]['instances'][0]['attributes']['restrictions'][0]['apps']) )
        print ("restrictions.teams :" +  json.dumps(tfstate['resources'][0]['instances'][0]['attributes']['restrictions'][0]['teams']) )
        print ("restrictions.users :" +  json.dumps(tfstate['resources'][0]['instances'][0]['attributes']['restrictions'][0]['users']) )

    set_fields(tfstate)


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

def create_resource_file_for_importing(repo):
    f = open("git_branch_protection.tf", "w")
    f.write('resource "github_branch_protection" "%s" { \n'
                '\t repository     = "%s"\n'
            '}\n' % (str(repo.replace('-','_')), str(repo)))
    f.close()

def delete_resource_file_for_importing(cleanup = True):
    if cleanup:
        os.remove(current_path + "/git_branch_protection.tf")
        os.remove(current_path + "/terraform.tfstate")

def import_branch_protection(repo, do_import=True, branch="master"):
    if not terraform:
        print("Terraform object error, check if initiated")
        sys.exit(1)
    try:
        if do_import:
            resource = 'github_branch_protection.{}'.format(str(repo.replace('-','_')))
            repo_and_branch = '{}:{}'.format(str(repo),str(branch))
            return_code, stdout, stderr  = terraform.import_cmd(resource, repo_and_branch)
            if return_code != 0:
                print("Unable to import git resource:%s branch info: %s return code %d" % (resource, repo_and_branch, return_code))
                sys.exit(1)
        terraform.read_state_file()
    except:
        print("Unable to read state file")
        sys.exit(1)
    return terraform.tfstate.__dict__


def testing():
    #repo_name = "chef"
    #repo_name = "omer-test"
    repo_name = "feature-extraction-service"
    create_resource_file_for_importing(repo_name)
    read_tfstate_file(repo_name)
    delete_resource_file_for_importing()

# Preperation:
#   1. Install the follwing packages:
#       pip install python-terraform
#       pip install PyGithub
#   2. Create the github.ft with the proprer GITHUB_TOKEN
#       provider "github" {
#           token        = "${var.github_token}"
#           organization = "${var.github_organization}"
#       }
#   3. terraform init
# Run:
#   GITHUB_TOKEN="XXXXXXXXXXX" python2.7 get_branch_protection.py
# Outout:
#   terrafom branch protection files will be under the directory output
# Testing:
#   Import some branch protections using terraform import and test by perform terraform apply
#   For example:
#   If we take the repository name: feature-extraction-service
#   1. Create terraform file import.tf with the follwing:
#       resource "github_branch_protection" "feature_extraction_service" {
#           repository     = "master"
#       }
#   2. Import the branch permission to ftstate by:
#       terraform import github_branch_protection.feature_extraction_service feature-extraction-service:master
#   3. Test to see no drifts by:
#       terraform apply

def main():
    print("Start importing")
    #init_logger()
    terraform.init()
    f = open(current_path + "/branch_protection_status.log", "w")

    with open("excluded_repos.txt") as k:
        excluded_repos = k.readlines()
    excluded_repos = [x.strip() for x in excluded_repos]

    repos = get_git_repos()
    for repo in repos:
        if repo.name in excluded_repos:
            f.write("Repository %s is excluded from importing\n" % (repo.name))
            continue
        try:
            branch = repo.get_branch("master")
        except:
            f.write("Fail getting branch master for repository %s\n" % (repo.name))
            continue
        if branch.protected:
            f.write("Branch master of repository %s is protected\n" % (repo.name))
            create_resource_file_for_importing(repo.name)
            read_tfstate_file(repo.name)
            delete_resource_file_for_importing()
        else:
            f.write("Branch master of repository %s is NOT protected\n" % (repo.name))

    f.close()
    print("End importing")

if __name__ == '__main__':
    main()