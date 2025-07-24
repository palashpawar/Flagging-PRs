**Pull Request Target Release Validator**

**This repository contains an Azure DevOps pipeline that automatically validates whether pull requests targeting the trunk branch are linked to work items with the correct Target Release.**

**🎯 Purpose**

To ensure that all changes merged into trunk are properly associated with a work item that has:

Emerson.TargetRelease == v16.LTS

If no such work item is found (including through parent links), the pipeline will fail and block the PR merge.

**🛠️ How It Works**

Triggered by pull requests to trunk

**For each PR:**

Fetches all linked work items (recursively includes parent work items)

Checks if any of them have the required Target Release

Fails the pipeline if none do

**🔐 Permissions & Tokens**

The pipeline uses System.AccessToken to authenticate with Azure DevOps REST APIs

In pipeline settings, make sure to check:
"Allow scripts to access the OAuth token"

