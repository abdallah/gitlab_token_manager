#!/usr/bin/env python3
import re
import gitlab
import argparse
import settings
import logging
from dateutil.relativedelta import relativedelta
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Argument parser setup
parser = argparse.ArgumentParser(description='Rotate GitLab Access Token')
# Add mutually exclusive group
group = parser.add_mutually_exclusive_group()
group.add_argument('-c', '--create', help='Create GitLab Access Token', action='store_true')
group.add_argument('-d', '--delete', help='Delete GitLab Access Token', action='store_true')
group.add_argument('-r', '--rotate', help='Rotate GitLab Access Token', action='store_true')

parser.add_argument('-e', '--expires_at', help='Access Token Expiry Date. i.e. "2021-12-31"')
parser.add_argument('-g', '--group', help='GitLab Group ID or Name')
parser.add_argument('-l', '--list', help='List GitLab Access Tokens', action='store_true')
parser.add_argument('-n', '--name', help='Access Token Name')
parser.add_argument('-p', '--project', help='GitLab Project ID or Name')
parser.add_argument('-s', '--scopes', help='Access Token Scopes. Comma delimited list of scopes. i.e. "api,read_user"')
parser.add_argument('-t', '--token', help='GitLab Access Token ID or Name')
parser.add_argument('-u', '--user', help='GitLab User ID or Name. Only useful for administrators!')


args = parser.parse_args()

gl = gitlab.Gitlab(settings.gitlab_url, private_token=settings.gitlab_token)

def list_access_tokens(token_owner, token_type="personal"):
    access_tokens = []
    try:
        if token_type == "personal":
            access_tokens = gl.personal_access_tokens.list(user_id=token_owner.id, state="active")
        else:
            access_tokens = token_owner.access_tokens.list()
    except Exception as e:
        logging.error(f"Error listing access tokens: {e}")
    return access_tokens

def get_access_token(token, token_owner, token_type="personal"):
    try:
        if not token.isdigit():
            tokens = [t.id for t in list_access_tokens(token_owner, token_type) if t.name == token]
            if not tokens:
                logging.error("Access Token not found!")
                return None
            token = tokens[0]
        if token_type == "personal":
            token = gl.personal_access_tokens.get(token)
        else:
            token = token_owner.access_tokens.get(token)
    except Exception as e:
        logging.error(f"Error getting access token: {e}")
        return None
    return token

def rotate_access_token(token, expires_at=None):
    if expires_at:
        token.expires_at = expires_at
    try:
        token.rotate()
    except Exception as e:
        logging.error(f"Error rotating access token: {e}")
        return None
    return token

def create_access_token(token_name, token_scopes, token_owner, expires_at, token_type="personal"):
    tokens = [t for t in list_access_tokens(token_owner, token_type) if t.name == token_name]
    if tokens:
        logging.error("Access Token with this name already exists!")
        exit(1)
    scopes = re.split(r'[,\s]+', token_scopes)
    try:
        if token_type == "personal":
            token = token_owner.personal_access_tokens.create({"name": token_name, "scopes": scopes})
        else:
            token = token_owner.access_tokens.create({"name": token_name, "scopes": scopes, "expires_at": expires_at})
    except Exception as e:
        logging.error(f"Error creating access token: {e}")
        return None
    return token

def delete_access_token(token):
    try:
        token.delete()
        logging.info(f"Access Token {token.id} has been deleted!")
    except Exception as e:
        logging.error(f"Error deleting access token: {e}")

if __name__ == "__main__":
    token_type = "personal"
    token_owner = None
    try:
        if args.user:
            token_owner = gl.users.get(args.user)
        elif args.group:
            token_owner = gl.groups.get(args.group)
            token_type = "group"
        elif args.project:
            token_owner = gl.projects.get(args.project)
            token_type = "project"
        else:
            gl.auth()
            token_owner = gl.users.get(gl.user.id)

        if args.expires_at:
            try:
                datetime.strptime(args.expires_at, "%Y-%m-%d")
            except ValueError:
                logging.error("Invalid Expiry Date format. Use YYYY-MM-DD!")
                exit(1)

        if args.token:
            token = get_access_token(args.token, token_owner, token_type)
            if token:
                print(token.id, token.name, token.created_at, token.expires_at, token.revoked, token.scopes)

        if args.list:
            tokens = list_access_tokens(token_owner, token_type)
            if tokens:
                for token in tokens:
                    print(token.id, token.name, token.created_at, token.expires_at, token.revoked, token.scopes)
            else:
                logging.info("No active access tokens found for this user/group/project!")

        if args.rotate:
            if not args.token:
                logging.error("Access Token ID or Name is required to rotate!")
                exit(1)
            token = get_access_token(args.token, token_owner, token_type)
            if token:
                token = rotate_access_token(token, args.expires_at)
                if token:
                    print(token.id, token.name, token.created_at, token.expires_at, token.revoked, token.scopes)
                    logging.info(f'Access Token: {token.token}')

        if args.create:
            if not args.name or not args.scopes:
                logging.error("Access Token Name and Scopes are required to create!")
                exit(1)
            if not args.expires_at:
                args.expires_at = (datetime.now() + relativedelta(months=1)).strftime("%Y-%m-%d")

            token = create_access_token(args.name, args.scopes, token_owner, args.expires_at, token_type)
            if token:
                print(token.id, token.name, token.created_at, token.expires_at, token.revoked, token.scopes)
                logging.info(f'Access Token: {token.token}')

        if args.delete:
            if not args.token:
                logging.error("Access Token ID or Name is required to delete!")
                exit(1)
            token = get_access_token(args.token, token_owner, token_type)
            if token:
                delete_access_token(token)
    except gitlab.GitlabAuthenticationError:
        logging.error("Authentication failed! Check your GitLab URL and Token.")
        exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        exit(1)
