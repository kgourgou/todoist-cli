import requests
import urllib
import argparse
import ConfigParser
import json
import os
import pprint

config = ConfigParser.ConfigParser()
config.read([os.path.expanduser('~/.todoist.cfg')])

TOKEN = config.get('DEFAULT', 'TOKEN')
DEFAULT_PROJECT_NAME = config.get('DEFAULT', 'DEFAULT_PROJECT_NAME')
URL = 'https://api.todoist.com/API'


def get_projects():
    """Returns a dictionary of projects with key: value of
    project_name: project_id"""

    params = [('token', TOKEN)]
    res_url = "{}/getProjects?{}".format(URL, urllib.urlencode(params))

    response = requests.get(res_url)

    if response.status_code != 200:
        print response.reason
        exit()

    json_response = json.loads(response.text)

    projects = {}

    for project in json_response:
        projects[project['name']] = project['id']
        projects[project['id']] = project['name']

    return projects


def list_projects():
    """Prints a list of the projects"""
    projects = get_projects()
    pprint.pprint([name for name in projects.keys() if type(name) != int])


def add_task(content, projects, project=None, due=None, url=None):
    """Adds a task. Returns resulting item json or error"""

    if project in projects:
        project_id = projects[project]

    else:
        project_id = projects[DEFAULT_PROJECT_NAME]

    if url is not None:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://{}".format(url)
        params = [('content', "{} ({})".format(url, content)), ('project_id', project_id), ('token', TOKEN), ('priority', 1)]

    else:
        params = [('content', content), ('project_id', project_id), ('token', TOKEN), ('priority', 1)]

    if due is not None:
        params.append(('date_string', due))

    res_url = "{}/addItem?{}".format(URL, urllib.urlencode(params))

    response = requests.get(res_url)

    if response.status_code != 200 or response.text.startswith('"ERROR'):
        print response.reason, response.text
        exit()

    json_response = json.loads(response.text)

    print "{} \n".format(json_response['content']) + \
        "due {} \n".format(json_response['due_date']) + \
        "added to project {}".format(projects[json_response['project_id']])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('function', help='Function to call: add, list_projects')
    parser.add_argument('-p', '--project', help="project to add task to")
    parser.add_argument('-c', '--content', help="desired task")
    parser.add_argument('-d', '--due', help="Due when?")
    parser.add_argument('-u', '--url', help="URL?")

    args = parser.parse_args()

    projects = get_projects()

    if args.function.lower() == "add":
        add_task(args.content, projects, project=args.project, due=args.due, url=args.url)
    else:
        list_projects()


if __name__ == "__main__":
    main()