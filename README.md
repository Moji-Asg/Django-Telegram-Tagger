# Django Telegram Tagger

[![forthebadge](http://forthebadge.com/images/badges/made-with-python.svg)](http://forthebadge.com)

#### Video Demo: https://youtu.be/ZuyJulVJObY
#### Description: This bot notifies users of telegram group.

### Table of content
- [Installation](#installation)
  - [Docker](#docker)
  - [Without Docker](#without-docker)
- [Usage](#usage)
  - [Default Commands](#default-commands)
  - [Auto Tag](#auto-tag)
- [Custom Configurations](#custom-configurations)
- [Contributing](#contributing)
- [License](#license)

## Installation
[(back to top)](#table-of-content)

### Docker

1. First Install docker from [this link](https://docs.docker.com/engine/install).

2. Install Python:
   ```commandline
   apt install python python3-pip -y
   ```

3. Clone source code from git:
   ```commandline
   git clone https://github.com/moji-asg/django-telegram-tagger.git
   cd django-telegram-tagger
   ```

4. Create session file:
   1. `cd django-telegram-tagger`
   2. `python manage.py login`
   3. Enter phone number.
   4. Enter login code.
   5. Enter 2FA password if activated.
   6. `mv db/* ../db/`
   7. `cd ..`

5. Then open [docker-compose.yml](https://github.com/moji-asg/django-telegram-tagger/blob/master/docker-compose.yml):
   1. Replace values between "{}" at [line #12](https://github.com/moji-asg/django-telegram-tagger/blob/master/docker-compose.yml#L12)

6. Start Containers:
   ```commandline
   docker compose up -d
   ```
   - Make sure the version of you using supports compose, If not install it using this command:
   ```commandline
   pip install docker-compose
   docker-compose up -d
   ```

### Without Docker

1. Install Python:
   ```commandline
   apt install python python3-pip
   ```

2. Clone source code from git:
   ```commandline
   git clone https://github.com/moji-asg/django-telegram-tagger.git
   cd django-telegram-tagger
   ```

3. Install dependencies:
   ```commandline
   pip install -r requirements.txt
   ```

4. Create session file:
   1. `python manage.py login`
   2. Enter phone number.
   3. Enter login code.
   4. Enter 2FA password if activated.

5. Run Tagger:
   ```commandline
   python manage.py runserver 0.0.0.0:8000 --insecure --noreload --skip-checks
   ```

## Usage

[(back to top)](#table-of-content)

First enter your account's saved messages then send these commands below:
```text
/setusername myusername
/setpassword mypassword
/panel
```

Then enter panel by clicking the link.
Enter your username and password and sign in.
Then customize anything you want and remember to click save button at the end!

### Default Commands

- `/setusername`
  - Set username for signing in to settings panel.
  - Only in saved messages
- `/setpassword`
  - Set password for signing in to settings panel.
  - Only in saved messages
- `/settings`
  - Sends a link to settings panel.
- `/help`
  - Sends a help message about all commands.

### Auto Tag

First enter settings panel by `/panel` command.
Then scroll to the button to reach Auto Tag section.
You'll see 3 inputs there.

- Auto Tag Chats
  - You should enter chat's unique id (example: "-10015879654")
  - You can enter multi chats by going to next line.
- Auto Tag Type
  - Set what type of tag should but do.
- Auto Cleaning Tags
  - If activated bot will automatically clean tags.

#### What are these settings?
Auto Tag option is only for Telegram game [Werewolf](https://t.me/@werewolfbot).
When you start a game bot will automatically start tagging, and it will stop after game starts.

#### Warning!
This option currently works on "Persian Normal" mode in the game.
We will add other mods in the future.

## Custom Configurations
[(back to top)](#table-of-content)

You can change your default settings by changing these files:
- [settings.py](https://github.com/moji-asg/django-telegram-tagger/blob/master/django-telegram-tagger/django_telegram_tagger/settings.py)
- telegram/telegram.py [Line #16](https://github.com/moji-asg/django-telegram-tagger/blob/master/django-telegram-tagger/telegram/telegram.py#L16) - [Line #18](https://github.com/moji-asg/django-telegram-tagger/blob/master/django-telegram-tagger/telegram/telegram.py#L18)
- [tagger/settings.py](https://github.com/moji-asg/django-telegram-tagger/blob/master/django-telegram-tagger/tagger/settings.py)

## Contributing
[(back to top)](#table-of-content)

Your contributions are always welcome!

Feel free to make PR!

## License
[(back to top)](#table-of-content)

Please have a look at the [LICENSE.md](https://github.com/moji-asg/django-telegram-tagger/blob/master/LICENSE.md) for more details.
