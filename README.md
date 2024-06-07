# GitLab Access Token Management Script

This Python script is designed to manage GitLab access tokens. It provides functionalities to list, create, rotate, and delete access tokens for GitLab users, groups, and projects.

## Prerequisites

- Python 3.x
- `python-gitlab` package
- `python-dateutil` package
- GitLab account with necessary permissions
- `settings.py` file containing GitLab URL and personal access token

### `settings.py`

Ensure you have a `settings.py` file with the following content:

```python
gitlab_url = "https://gitlab.example.com"
gitlab_token = "your_private_token"
```

## Script Usage

### Command Line Arguments

The script accepts several command line arguments to specify the operation and parameters:

- `-c`, `--create`: Create a new GitLab access token.
- `-d`, `--delete`: Delete an existing GitLab access token.
- `-r`, `--rotate`: Rotate an existing GitLab access token.
- `-e`, `--expires_at`: Specify the expiry date for the access token in `YYYY-MM-DD` format.
- `-g`, `--group`: Specify the GitLab group ID or name.
- `-l`, `--list`: List all active GitLab access tokens for the user/group/project.
- `-n`, `--name`: Specify the name of the access token.
- `-p`, `--project`: Specify the GitLab project ID or name.
- `-s`, `--scopes`: Specify the scopes for the access token. Comma-delimited list of scopes (e.g., `api,read_user`).
- `-t`, `--token`: Specify the GitLab access token ID or name.
- `-u`, `--user`: Specify the GitLab user ID or name. Only useful for administrators.

### Examples

#### Listing Access Tokens

```bash
gitlab_token_manager -l
```

#### Creating an Access Token

```bash
gitlab_token_manager -c -n "My Access Token" -s "api,read_user" -e "2024-12-31"
```

#### Rotating an Access Token

```bash
gitlab_token_manager -r -t "1" -e "2024-12-31"
```

#### Deleting an Access Token

```bash
gitlab_token_manager -d -t "1"
```

### GitLab Initialization

A GitLab object is initialized using the URL and token specified in the `settings.py` file.

### Functions

- `list_access_tokens(token_owner, token_type="personal")`: Lists active access tokens for the specified owner.
- `get_access_token(token, token_owner, token_type="personal")`: Retrieves a specific access token based on ID or name.
- `rotate_access_token(token, expires_at=None)`: Rotates an access token and optionally updates its expiry date.
- `create_access_token(token_name, token_scopes, token_owner, expires_at, token_type="personal")`: Creates a new access token with specified name, scopes, and expiry date.
- `delete_access_token(token)`: Deletes the specified access token.

### Main Execution

The script performs the following steps based on the provided arguments:

1. Determines the token owner (user, group, or project).
2. Validates the expiry date format if provided.
3. Lists access tokens if `--list` is specified.
4. Gets details of a specific access token if `--token` is specified.
5. Rotates an access token if `--rotate` is specified.
6. Creates a new access token if `--create` is specified.
7. Deletes an access token if `--delete` is specified.
