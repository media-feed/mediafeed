import sys
from json import dumps
from urllib.request import urlopen


def download(filename, url):
    with open(filename, 'wb') as f, urlopen(url) as u:
        f.write(u.read())


def print_json(content):
    print(dumps(content), file=sys.stdout)


def print_jsons(contents):
    for content in contents:
        print_json(content)


def run(module_process):
    try:
        sys.exit(module_process())
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
