import os
import sys
from github import Github
from python_terraform import *
import logging

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

def set_fields(require_signed_commits_contexts, require_signed_commits_strict, require_signed_commits ,enforce_admins, repository, branch="master"):
    print(  'resource "github_branch_protection" "%s" { \n'
                '\t repository = "%s" \n'
                '\t branch = "%s" \n'
                '\t enforce_admins = %s \n'
                '\t require_signed_commits = true \n'
                '\n\n'
                '\t require_signed_commits { \n'
                    '\t\t strict   = false \n'
                    '\t\t contexts = [""] \n'
                '\t } \n'
                '\n\n'
                '\t required_pull_request_reviews { \n'
                    '\t\t dismiss_stale_reviews = true \n'
                    '\t\t dismissal_users = [""] \n'
                    '\t\t dismissal_teams = ["", ""] \n'
                    '\t\t require_code_owner_reviews = false \n'
                    '\t\t required_approving_review_count = 1 \n'
                '\t } \n'
                '\n\n'
                '\t restrictions { \n'
                    '\t\t users = [""] \n'
                    '\t\t teams = [""] \n'
                    '\t\t apps = [""] \n'
                '\t } \n'
            '}' % (branch, repository, branch ) )

def read_tfstate_file(repo):
    tfstate = import_branch_protection(repo)
    print ("enforce_admins: " + str(tfstate['resources'][0]['instances'][0]['attributes']['enforce_admins']).lower())
    print ("branch: " + str(tfstate['resources'][0]['instances'][0]['attributes']['branch']))
    print ("repository: " + str(tfstate['resources'][0]['instances'][0]['attributes']['repository']) )
    print ("require_signed_commits: " + str(tfstate['resources'][0]['instances'][0]['attributes']['require_signed_commits']).lower())
    print ("required_pull_request_reviews.dismiss_stale_reviews: " + str(tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews'][0]['dismiss_stale_reviews']).lower())
    print ("required_pull_request_reviews.include_admins: " + str(tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews'][0]['include_admins']).lower())
    print ("required_pull_request_reviews.require_code_owner_reviews: " + str(tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews'][0]['require_code_owner_reviews']).lower())
    print ("required_pull_request_reviews.required_approving_review_count: " + str(tfstate['resources'][0]['instances'][0]['attributes']['required_pull_request_reviews'][0]['required_approving_review_count']))

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
            '}\n' % (str(repo), str(repo)))
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
            resource = 'github_branch_protection.{}'.format(str(repo))
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


def main():
    print("start")
    #init_logger()
    terraform.init()
    '''
    repos = get_git_repos()
    repo_names = [repo.name for repo in repos]
    for repo_name in repo_names:
        print(repo_name)
    '''

    create_resource_file_for_importing("feature-extraction-service")
    #print (import_branch_protection(repo="feature-extraction-service", do_import=True) )
    read_tfstate_file("feature-extraction-service")

    delete_resource_file_for_importing()

if __name__ == '__main__':
    main()