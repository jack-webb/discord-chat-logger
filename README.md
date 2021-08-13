### Discord Chat Logger
_Log Discord messages, edits and deletions_

The primary branch on this project (`master`) is not stable, and is not recommended for use. It contains undocumented breaking changes. The setup instructions below do not work on the primary branch.

Use the latest version from [releases](https://github.com/jack-webb/discord-chat-logger/releases) instead.

#### Requirements and setup
**Out of date - use environment variables instead. See main.py.**

_Requires Python 3.5.3 (or above) and Pipenv_
1. Install dependencies with `pipenv install` 
2. Copy `config.example.py` to `config.py` and add your bot token and database details.
3. Run with `pipenv run python -m logger.main`

Note: If you want to a run a version different to 3.8, edit the Pipfile to support. Only versions above 3.5.3 are supported.
