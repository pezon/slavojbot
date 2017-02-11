import logging

from slackbot.bot import Bot

logger = logging.getLogger()
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def main():
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
