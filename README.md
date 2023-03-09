# THE PROJECT IS NOT USABLE AFTER TLSCONTACT INTRODUCED A ROBOT-PROTECTING LANDING PAGE.

# What is it?

If you ever tried to get a French Schengen visa using using TLSContact in London, you know that it's a pain
and it's nearly impossible to get an appointment earlier than in 1.5 months. This script constantly monitors
available appointments and notifies you as soon as it'll find an appropriate one.

# What's supported?

At the moment the script was tested only with London's office of TLSContact and only with French Overseas
Territory visa, but it should work at least with regular French visa as well.

# How it's working?

Under the hood the script uses [Selenium Webdriver](https://www.seleniumhq.org/projects/webdriver/) and
Python3. You have to provide your TLSContact credentials, and the script will monitor available dates for you.
All the notifications are being sent to [telegram](https://telegram.org), in order to work properly you have
to [register a Telegram Bot](https://core.telegram.org/bots#6-botfather) and provide the token to the script.

# Setting up

## Available arguments

* `--tls-application-reference`, e.g. `M7806666`, it's displayed in your TLSContact account as `Your TLScontact
  reference number`
* `--login`, your TLSContact login
* `--password`, your TLSContact password
* `--telegram-bot-token`, telegram bot's token, you have to get one from [BotFather](https://core.telegram.org/bots#6-botfather)
* `--telegram-chat-id`, chat id in Telegram, could be your UserId (you can detect your by dropping a message to
  [@userinfobot](https://t.me/userinfobot))
* `--search-before`, the date before which you're interested in the appointment. Bot will be sending a message
  to you at each run anyway, but with this date provided the message will be a bit different, clearly stating
  that it's a good date for you
* `--delay`, delay in seconds between runs. I recommend stick to the default value, 5400 seconds (1.5 hours),
  because TLSContact has a limit of allowed authentications per day   
* `--selenium-executor`, URL to Selenium command executor, use it when you know what you're doing
* `--once`, run the search just once, useful for debugging

## Easiest way to run, using docker-compose

Clone this repo locally:

```
git clone https://github.com/andrey-yantsen/tlscontact-appointment-finder.git
```

And run it using following command, replacing arguments with proper values:

```
docker-compose run -d selenium && sleep 10
docker-compose run tlscontact \
  --tls-application-reference <APPLICATION_REFERENCE> \
  --login <EMAIL> \
  --password <PASSWORD> \
  --search-before <DATE> \
  --telegram-bot-token <TELEGRAM_TOKEN> \
  --telegram-chat-id <TELEGRAM_CHAT_ID>
```

All those arguments are required.

## Other ways...

Just google it :)
