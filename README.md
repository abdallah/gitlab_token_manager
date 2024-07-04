# GitLab Access Token Manager

This script manages GitLab access tokens, allowing you to create, delete, list, and rotate tokens for users, groups, or projects.

## Features

- **Create**: Create a new GitLab access token.
- **Delete**: Delete an existing GitLab access token.
- **List**: List all active access tokens.
- **Rotate**: Rotate an existing GitLab access token.

## Prerequisites

- Python 3.x
- `python-gitlab` library
- `python-dateutil` library

Install the required libraries using pip:

```bash
pip install python-gitlab python-dateutil
```

## Setup

1. **Clone the repository**:

   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Create a `settings.py` file**:
   Create a file named `settings.py` in the same directory as the script and add the following content:

   ```python
   gitlab_url = "https://gitlab.example.com"
   gitlab_token = "your_private_token"
   ```

## Usage

Run the script using the command:

```bash
python3 token_manager.py [OPTIONS]
```

### Options

#### Actions (mutually exclusive):

- `-c`, `--create`: Create a new GitLab access token.
- `-d`, `--delete`: Delete an existing GitLab access token.
- `-r`, `--rotate`: Rotate an existing GitLab access token.
- `-l`, `--list`: List all active GitLab access tokens.

#### Owners (mutually exclusive):

- `-u`, `--user`: GitLab User ID or Name.
- `-g`, `--group`: GitLab Group ID or Name.
- `-p`, `--project`: GitLab Project ID or Name.

#### Additional Options:

- `-e`, `--expires_at`: Access token expiry date (format: `YYYY-MM-DD`).
- `-n`, `--name`: Access token name.
- `-o`, `--output`: Output file path for the access token. Use `-` or `stdout` to print to the console.
- `-s`, `--scopes`: Comma-separated list of access token scopes (e.g., `api,read_user`).
- `-t`, `--token`: GitLab access token ID or name.

### Examples

1. **Create a new access token**:

   ```bash
   python3 token_manager.py --create --user <user_id> --name <token_name> --scopes "api,read_user" --expires_at "2024-12-31"
   ```

2. **Delete an access token**:

   ```bash
   python3 token_manager.py --delete --user <user_id> --token <token_id>
   ```

3. **List all access tokens for a user**:

   ```bash
   python3 token_manager.py --list --user <user_id>
   ```

4. **Rotate an access token**:

   ```bash
   python3 token_manager.py --rotate --user <user_id> --token <token_id> --expires_at "2025-12-31"
   ```

## Logging

All actions and errors are logged to `token_manager.log` in the script directory. Check this file for detailed logs and error messages.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

This script uses the `python-gitlab` library to interact with the GitLab API. For more information, visit the [python-gitlab documentation](https://python-gitlab.readthedocs.io/).

---

Feel free to reach out if you encounter any issues or have suggestions for improvements. Happy token managing!
