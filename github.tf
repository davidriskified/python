variable "github_token" {}
variable "github_organization" {}

# Configure the GitHub Provider
provider "github" {
	token        = var.github_token
	organization = var.github_organization
}

