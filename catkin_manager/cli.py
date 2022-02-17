#!/usr/bin/env python3

# https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/
# https://docs.python-guide.org/writing/structure/
# https://stackoverflow.com/questions/193161/what-is-the-best-project-structure-for-a-python-application
# https://pypi.org/project/click-config-file/
# https://www.tutorialspoint.com/python/os_symlink.htm

import click
import os
import os.path
from pathlib import Path

from .core import CatkinManager, Status, PackageInfo

@click.group()
@click.pass_context
def app(ctx):
    ctx.ensure_object(dict)

@click.command()
@click.option("--verbose", "-v", is_flag=True)
def info(verbose):

    cm = CatkinManager()
    cm.print_info(verbose)

@click.command()
@click.argument("package")
@click.argument("location", type=click.Path(exists=True))
@click.option('--link/--no-link', "-L", default=True)
def add(package, location, link):
    
    cm = CatkinManager()
    cm.add_package(package, location, link=link)

    print("Added: {}: {}".format(package, location))
    if link:
        print("Linked: {} -> {}".format(package, location))

@click.command()
@click.argument("package")
@click.option("--force", "-f", is_flag=True)
def rm(package, force):

    cm = CatkinManager()
    removed = cm.remove_package(package, unlink=force)

    if removed:
        print("Removed: {}: {}".format(package, removed.expected))
        if force:
            print("Unlinked: {} -> {}".format(package, removed.actual))
            print("catkin_make && source devel/setup.bash")
    else:
        print("Not found: {}".format(package))

@click.command()
@click.option('--delete', '-d', is_flag=True)
def link(delete):

    cm = CatkinManager()
    cm.create_links(delete)

@click.command()
def build():
    print("catkin_make && source devel/setup.bash")

@click.command()
def dependencies():

    cm = CatkinManager()
    cm.dependency_graph()

app.add_command(info)
app.add_command(link)
app.add_command(build)
app.add_command(add)
app.add_command(rm)
app.add_command(dependencies)

if __name__ == '__main__':
    app(obj={})
