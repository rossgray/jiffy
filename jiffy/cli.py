import click
from client import get_jira_client, JIRA_CONFIG


@click.group()
def cli():
    pass


@cli.group()
def issues():
    pass


@issues.command()
def list():
    click.echo('Listing issues assigned to you...\n')
    jira = get_jira_client()
    project = JIRA_CONFIG['DEFAULT_PROJECT']
    for issue in jira.search_issues(
        f'assignee = currentUser() and project={project} order by created desc',
        maxResults=10,
    ):
        print('{}: {}'.format(issue.key, issue.fields.summary))


if __name__ == '__main__':
    cli()
