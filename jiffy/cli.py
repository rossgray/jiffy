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
    click.echo('Listing current issues assigned to you...\n')
    jira = get_jira_client()
    project = JIRA_CONFIG['DEFAULT_PROJECT']
    for issue in jira.search_issues(
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
                resolution = Resolved
                AND resolution changed to Resolved after startofday(-5)
            )
        )
        ORDER BY status
        ''',
        maxResults=20,
    ):
        print(
            '{}: {}: {}'.format(
                issue.fields.status,
                issue.key,
                issue.fields.summary,
            )
        )


if __name__ == '__main__':
    cli()
