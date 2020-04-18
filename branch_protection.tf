resource "github_branch_protection" "feature-extraction-service" {
  repository     = "feature-extraction-service"
  branch         = "master"
  enforce_admins = true
 
}
