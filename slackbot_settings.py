from os import environ

API_TOKEN = environ.get('SLACK_API_TOKEN')

PLUGINS = [
    'slavojbot.plugins',
]

