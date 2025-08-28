# AWS CloudFormation Templates

This repository contains reusable AWS CloudFormation templates and a simple Python deployment script for managing stacks across multiple accounts.

## Usage

Deploy a template to an account using the provided script:

```bash
python deploy.py <account> <region> <stack_name> <template_path>
```

The `account` value may be `general` to use credentials from the master organization account, or a specific AWS account ID to assume the `OrganizationAccountAccessRole`.
