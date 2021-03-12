from pprint import pprint

import click
import jira
from PyInquirer import prompt

from client import JIRA_CONFIG, get_jira_client
from utils import print_issue, get_issue_str

jira_client = get_jira_client()
project = JIRA_CONFIG['DEFAULT_PROJECT']


@click.group()
def cli():
    pass


@cli.command()
def issues():
    click.echo('Listing current issues assigned to you...\n')
    issues = jira_client.search_issues(
        f'''assignee = currentUser()
        AND project={project}
        AND issueType != Sub-task
        AND (
            (
                resolution = Unresolved
                AND
                status != Backlog
            )
            OR (
                updated > startofday(-5)
            )
        )
        ORDER BY status ASC, updated DESC
        ''',
        maxResults=20,
    )

    questions = [
        {
            'type': 'list',
            'name': 'issue',
            'message': 'Please select an issue',
            'choices': [
                {
                    'name': get_issue_str(i),
                    'value': i,
                }
                for i in issues
            ],
        },
    ]

    answers = prompt(questions)
    issue = answers['issue']

    process_issue_actions(issue)


def process_issue_actions(issue: jira.Issue):

    actions = []
    if issue.fields.subtasks:
        actions.append({'name': 'Show subtasks', 'value': 'show_subtasks'})
    actions += [
        {'name': 'Update status', 'value': 'status'},
        {'name': 'Log time', 'value': 'logtime'},
        {'name': 'Show details', 'value': 'details'},
        # {'name': 'Open in JIRA', 'value': 'open'},
    ]
    questions = [
        {
            'type': 'list',
            'name': 'action',
            'message': 'What action would you like to perform?',
            'choices': actions,
        },
    ]
    answers = prompt(questions)
    action = answers['action']
    while action != 'exit':

        action = handle_action(action, issue)
        if action == 'exit':
            return
        print(f'Current issue: {get_issue_str(issue)}')

        # ask if want to perform another action
        questions = [
            {
                'type': 'list',
                'name': 'action',
                'message': 'Do you want to perform any further actions?',
                'choices': [
                    {'name': 'Nope', 'value': 'exit'},
                ]
                + actions,
            },
        ]
        answers = prompt(questions)
        action = answers['action']


def process_subtask_actions(subtask: jira.Issue):
    actions = [
        {'name': 'Update status', 'value': 'status'},
        {'name': 'Log time', 'value': 'logtime'},
        {'name': 'Show details', 'value': 'details'},
        {'name': 'Go back to parent issue', 'value': 'parent'},
    ]
    questions = [
        {
            'type': 'list',
            'name': 'action',
            'message': 'What action would you like to perform?',
            'choices': actions,
        },
    ]
    answers = prompt(questions)
    action = answers['action']
    while action not in ('exit', 'parent'):

        handle_action(action, subtask)

        # ask if want to perform another action
        questions = [
            {
                'type': 'list',
                'name': 'action',
                'message': 'Do you want to perform any further actions?',
                'choices': [
                    {'name': 'Nope', 'value': 'exit'},
                ]
                + actions,
            },
        ]
        answers = prompt(questions)
        action = answers['action']

    return action


def handle_action(action: str, issue: jira.Issue) -> str:

    # First make sure issue is up-to-date
    issue = jira_client.issue(issue.key)

    if action == 'show_subtasks':
        subtasks = issue.fields.subtasks
        questions = [
            {
                'type': 'list',
                'name': 'subtask',
                'message': 'Please select a subtask',
                'choices': [
                    {
                        'name': get_issue_str(s),
                        'value': s,
                    }
                    for s in subtasks
                ],
            },
        ]
        answers = prompt(questions)
        subtask = answers['subtask']
        action = process_subtask_actions(subtask)
        return action
    elif action == 'status':
        transitions = jira_client.transitions(issue)
        pprint([(t['id'], t['name']) for t in transitions])

        questions = [
            {
                'type': 'list',
                'name': 'transition',
                'message': 'Transition to',
                'choices': [
                    {
                        'name': t['name'],
                        'value': t['id'],
                    }
                    for t in transitions
                ],
            },
        ]
        answers = prompt(questions)
        transition_id = answers['transition']
        jira_client.transition_issue(issue, transition_id)
    elif action == 'logtime':
        questions = [
            {
                'type': 'input',
                'name': 'logtime_amount',
                'message': 'How much time do you want to log?',
            },
        ]
        answers = prompt(questions)
        time_spent = answers['logtime_amount']
        jira_client.add_worklog(issue=issue, timeSpent=time_spent)
    elif action == 'details':
        print_issue(issue)
    # elif action == 'open':
    #     pass


if __name__ == '__main__':
    cli()
