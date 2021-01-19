import configparser

from jira import JIRA

config = configparser.ConfigParser()
config.read('jira.cfg')
JIRA_CONFIG = config['JIRA']


def get_jira_client():
    return JIRA(
        basic_auth=(JIRA_CONFIG['USERNAME'], JIRA_CONFIG['PASSWORD']),
        options={'server': JIRA_CONFIG['URL']},
    )
