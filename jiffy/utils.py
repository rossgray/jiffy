import jira

from rich import print
from rich.table import Table

from client import JIRA_CONFIG


def get_issue_url(issue: jira.Issue) -> str:
    jira_url = JIRA_CONFIG['URL']
    return f'{jira_url}/browse/{issue.key}'


def get_issue_str(issue: jira.Issue) -> str:
    return '{}: {}: {}'.format(
        issue.fields.status,
        issue.key,
        issue.fields.summary,
    )


def format_time(secs: int) -> str:
    total_hours = secs / 60 / 60
    days = total_hours // 24
    hours = total_hours % 24
    if days > 0:
        return f"{days}d {hours}h"
    return f"{hours}h"


def print_issue(issue: jira.Issue) -> None:
    grid = Table.grid(expand=True)
    grid.add_column()
    grid.add_column()
    grid.add_row("", "")  # probably better way to add padding than this
    grid.add_row("[bold magenta]Key", issue.key)
    grid.add_row("[bold magenta]Summary", issue.fields.summary)
    grid.add_row("[bold magenta]URL", get_issue_url(issue))
    grid.add_row("[bold magenta]Issue type", issue.fields.issuetype.name)
    grid.add_row("[bold magenta]Status", issue.fields.status.name)
    if issue.fields.issuetype.subtask is False:
        time_estimate = format_time(issue.fields.aggregatetimeestimate or 0)
        grid.add_row(
            "[bold magenta]Total time estimate (including subtasks)",
            time_estimate,
        )
        time_spent = format_time(issue.fields.aggregatetimespent or 0)
        grid.add_row(
            "[bold magenta]Total time spent (including subtasks)",
            time_spent,
        )
    grid.add_row("", "")  # probably better way to add padding than this
    print(grid)
