#!/usr/bin/env python3
import re
import sys
import gitlab
import argparse
import settings
import logging
from dateutil.relativedelta import relativedelta
from datetime import datetime

# Constants
DEFAULT_EXPIRY_MONTHS = 1
LOG_FILE = "token_manager.log"

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Argument parser setup
def setup_argument_parser():
    parser = argparse.ArgumentParser(description="Rotate GitLab Access Token")
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("-c", "--create", help="Create GitLab Access Token", action="store_true")
    action_group.add_argument("-d", "--delete", help="Delete GitLab Access Token", action="store_true")
    action_group.add_argument("-r", "--rotate", help="Rotate GitLab Access Token", action="store_true")
    owner_group = parser.add_mutually_exclusive_group()
    owner_group.add_argument("-u", "--user", help="GitLab User ID or Name")
    owner_group.add_argument("-g", "--group", help="GitLab Group ID or Name")
    owner_group.add_argument("-p", "--project", help="GitLab Project ID or Name")
    parser.add_argument("-e", "--expires_at", help='Access Token Expiry Date. i.e. "2021-12-31"')
    parser.add_argument("-l", "--list", help="List GitLab Access Tokens", action="store_true")
    parser.add_argument("-n", "--name", help="Access Token Name")
    parser.add_argument("-o", "--output", help="Output file path. Can also be '-' or 'stdout'")
    parser.add_argument("-s", "--scopes", help='Access Token Scopes. Comma delimited list of scopes. i.e. "api,read_user"')
    parser.add_argument("-t", "--token", help="GitLab Access Token ID or Name")
    return parser

def validate_args(args):
    if args.expires_at:
        try:
            datetime.strptime(args.expires_at, "%Y-%m-%d")
        except ValueError:
            logging.error("Invalid Expiry Date format. Use YYYY-MM-DD!")
            sys.exit(1)
    if args.rotate and not args.token:
        logging.error("Access Token ID or Name is required to rotate!")
        sys.exit(1)
    if args.create and (not args.name or not args.scopes):
        logging.error("Access Token Name and Scopes are required to create!")
        sys.exit(1)
    if args.create and not args.expires_at:
        args.expires_at = (datetime.now() + relativedelta(months=DEFAULT_EXPIRY_MONTHS)).strftime("%Y-%m-%d")
    if args.delete and not args.token:
        logging.error("Access Token ID or Name is required to delete!")
        sys.exit(1)

def initialize_gitlab():
    try:
        gl = gitlab.Gitlab(settings.gitlab_url, private_token=settings.gitlab_token)
        gl.auth()
        return gl
    except gitlab.GitlabAuthenticationError:
        logging.error("Authentication failed! Check your GitLab URL and Token.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred during GitLab initialization: {e}")
        sys.exit(1)

def get_token_owner(gl, args):
    try:
        if args.user:
            return gl.users.get(args.user), "personal"
        elif args.group:
            return gl.groups.get(args.group), "group"
        elif args.project:
            return gl.projects.get(args.project), "project"
        else:
            return gl.users.get(gl.user.id), "personal"
    except Exception as e:
        logging.error(f"Error retrieving token owner: {e}")
        sys.exit(1)

def list_access_tokens(gl, token_owner, token_type="personal"):
    try:
        if token_type == "personal":
            return gl.personal_access_tokens.list(user_id=token_owner.id, state="active")
        else:
            return token_owner.access_tokens.list()
    except Exception as e:
        logging.error(f"Error listing access tokens: {e}")
        return []

def get_access_token(gl, token, token_owner, token_type="personal"):
    try:
        if not token.isdigit():
            tokens = [t.id for t in list_access_tokens(gl, token_owner, token_type) if t.name == token]
            if not tokens:
                logging.error("Access Token not found!")
                return None
            token = tokens[0]
        if token_type == "personal":
            return gl.personal_access_tokens.get(token)
        else:
            return token_owner.access_tokens.get(token)
    except Exception as e:
        logging.error(f"Error getting access token: {e}")
        return None

def rotate_access_token(token, expires_at=None):
    try:
        if expires_at:
            token.expires_at = expires_at
        token.rotate()
        return token
    except Exception as e:
        logging.error(f"Error rotating access token: {e}")
        return None

def create_access_token(gl, token_name, token_scopes, token_owner, expires_at, token_type="personal"):
    try:
        if any(t.name == token_name for t in list_access_tokens(gl, token_owner, token_type)):
            logging.error("Access Token with this name already exists!")
            sys.exit(1)
        scopes = re.split(r"[,\s]+", token_scopes)
        if token_type == "personal":
            return token_owner.personal_access_tokens.create({"name": token_name, "scopes": scopes})
        else:
            return token_owner.access_tokens.create({"name": token_name, "scopes": scopes, "expires_at": expires_at})
    except Exception as e:
        logging.error(f"Error creating access token: {e}")
        return None

def delete_access_token(token):
    try:
        token.delete()
        logging.info(f"Access Token {token.id} has been deleted!")
    except Exception as e:
        logging.error(f"Error deleting access token: {e}")

def print_token_info(token):
    print(token.id, token.name, token.created_at, token.expires_at, token.revoked, token.scopes)

def handle_output(token, output):
    if output == "-" or output == "stdout":
        print(token.token)
    else:
        try:
            with open(output, "w") as f:
                f.write(token.token)
                logging.info(f"Access Token has been written to {output}")
        except Exception as e:
            logging.error(f"Error writing access token to file: {e}")

def main():
    parser = setup_argument_parser()
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    validate_args(args)
    gl = initialize_gitlab()
    token_owner, token_type = get_token_owner(gl, args)

    if args.list:
        tokens = list_access_tokens(gl, token_owner, token_type)
        if tokens:
            for token in tokens:
                print_token_info(token)
        else:
            logging.info("No active access tokens found for this user/group/project!")

    if args.token:
        token = get_access_token(gl, args.token, token_owner, token_type)
        if token:
            print_token_info(token)

    if args.rotate:
        token = get_access_token(gl, args.token, token_owner, token_type)
        if token:
            token = rotate_access_token(token, args.expires_at)
            if token:
                print_token_info(token)
                logging.info(f"Access Token: {token.token}")

    if args.create:
        token = create_access_token(gl, args.name, args.scopes, token_owner, args.expires_at, token_type)
        if token:
            print_token_info(token)
            logging.info(f"Access Token: {token.token}")

    if args.delete:
        token = get_access_token(gl, args.token, token_owner, token_type)
        if token:
            delete_access_token(token)

    if token and args.output:
        handle_output(token, args.output)

if __name__ == "__main__":
    main()
