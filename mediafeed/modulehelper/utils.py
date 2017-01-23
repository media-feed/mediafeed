import sys
from json import dumps
from urllib.request import urlopen


def download(filename, url):
    with open(filename, 'wb') as f, urlopen(url) as u:
        content = True
        while content:
            content = u.read(4096)
            f.write(content)


def print_json(content):
    print(dumps(content), flush=True)


def print_jsons(contents):
    for content in contents:
        print_json(content)


def run(moduleprocess):
    try:
        status = moduleprocess()
        sys.exit(status)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
