#!/usr/bin/env python3

# https://docs.python-guide.org/writing/structure/
# https://stackoverflow.com/questions/193161/what-is-the-best-project-structure-for-a-python-application
# https://pypi.org/project/click-config-file/
# https://www.tutorialspoint.com/python/os_symlink.htm

import os
import os.path
from pathlib import Path
from enum import Enum

import click
import yaml

CATKIN_WS_SRC = "../catkin_ws/src"

def read_workspace():

    result = dict()

    for path in Path("../catkin_ws/src").iterdir():
        if path.is_symlink() and path.is_dir():
            result[path.name] = path

    return result

def read_packages():

    result = dict()

    with open("../catkin_ws/packages.yaml", 'r') as stream:
        try:
            data = yaml.safe_load(stream)
            for key, value in data["packages"].items():
                result[key] = Path(value)
        except yaml.YAMLError as exc:
            print(exc)

    return result

class Status(Enum):
    OK = 1
    MISSING = 2
    DIFFERENT = 3
    INSTALLED = 4

def compare(actual, expected, key):

    a = actual.get(key)
    e = expected.get(key)
    b = a and e

    return {
        "name": key,
        "actual": a,
        "expected": e,
        "is_same": a.samefile(e) if b else False,
        "status":
            Status.OK if b and a.samefile(e) else
            Status.MISSING if a == None else
            Status.INSTALLED if e == None else
            Status.DIFFERENT
    }

def create_link(package):

    link_name = Path(CATKIN_WS_SRC).joinpath(package["name"])
    target = package["expected"]

    click.echo("ln -s {} {}".format(target.resolve(), link_name.resolve()))
    #link_name.symlink_to(package["expected"])

def get_info():

    workspace = read_workspace()
    packages = read_packages()

    info_keys = sorted(set().union(workspace.keys(), packages.keys()))
    info = { k: compare(workspace, packages, k) for k in info_keys }

    return info

def print_info(package, verbose=False):

    text = "{}: {} -> {}" if verbose else "{}: {}"

    if package["status"] == Status.OK:
        text = click.style(text.format("OK", package["name"], str(package["actual"].resolve())), fg="green")
    elif package["status"] == Status.INSTALLED:
        text = click.style(text.format("OK", package["name"], str(package["actual"].resolve())), fg="yellow")
    elif package["status"] == Status.MISSING:
        text = click.style(text.format("Missing", package["name"], str(package["expected"].resolve())), fg="red")
    elif package["status"] == Status.DIFFERENT:
        text = click.style(text.format("Different", package["name"], str(package["expected"].resolve())), fg="red")

    click.echo(text)

@click.group()
def app():
    pass

@click.command()
@click.option("--verbose", "-v", is_flag=True)
def info(verbose):

    for key, value in get_info().items():
        print_info(value, verbose)

@click.command()
def link():
    for key, value in get_info().items():
        if value["status"] == Status.MISSING:
            create_link(value)

@click.command()
def build():
    print("catkin_make")

app.add_command(info)
app.add_command(link)
app.add_command(build)

if __name__ == '__main__':
    app()
