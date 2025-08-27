import argparse
import boto3
from botocore.exceptions import ClientError


def get_cfn_client(account: str, region: str):
    """Return a CloudFormation client for the given account and region.

    If account is 'general', use the master organization account. Otherwise assume
    the OrganizationAccountAccessRole in the target account before creating the
    client.
    """
    base_session = boto3.Session(profile_name='general', region_name=region)

    if account == 'general':
        return base_session.client('cloudformation')

    role_arn = f"arn:aws:iam::{account}:role/OrganizationAccountAccessRole"
    sts = base_session.client('sts')
    creds = sts.assume_role(RoleArn=role_arn, RoleSessionName='cfn-deploy')

    assumed_session = boto3.Session(
        aws_access_key_id=creds['Credentials']['AccessKeyId'],
        aws_secret_access_key=creds['Credentials']['SecretAccessKey'],
        aws_session_token=creds['Credentials']['SessionToken'],
        region_name=region,
    )
    return assumed_session.client('cloudformation')


def deploy_stack(account: str, region: str, stack_name: str, template_path: str):
    cfn = get_cfn_client(account, region)

    with open(template_path, 'r', encoding='utf-8') as f:
        template_body = f.read()

    try:
        cfn.describe_stacks(StackName=stack_name)
        exists = True
    except ClientError as e:
        if 'does not exist' in str(e):
            exists = False
        else:
            raise

    if exists:
        print(f"Updating stack {stack_name} in account {account}...")
        try:
            cfn.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_NAMED_IAM'],
            )
        except ClientError as e:
            if 'No updates are to be performed' in str(e):
                print('No updates required.')
            else:
                raise
    else:
        print(f"Creating stack {stack_name} in account {account}...")
        cfn.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Capabilities=['CAPABILITY_NAMED_IAM'],
        )


def main():
    parser = argparse.ArgumentParser(description='Deploy CloudFormation templates to AWS accounts.')
    parser.add_argument('account', help="Target account ID or 'general' for the master account")
    parser.add_argument('region', help='AWS region for deployment')
    parser.add_argument('stack_name', help='Name of the CloudFormation stack')
    parser.add_argument('template', help='Path to the CloudFormation template file')
    args = parser.parse_args()

    deploy_stack(args.account, args.region, args.stack_name, args.template)


if __name__ == '__main__':
    main()
