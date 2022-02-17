#!/usr/bin/env python3

# https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/
# https://docs.python-guide.org/writing/structure/
# https://stackoverflow.com/questions/193161/what-is-the-best-project-structure-for-a-python-application
# https://pypi.org/project/click-config-file/
# https://www.tutorialspoint.com/python/os_symlink.htm

import os
import os.path
from pathlib import Path
from enum import Enum

from glob import glob
import xml.etree.cElementTree as ET

import click
import yaml

class Status(Enum):
    OK = 1
    MISSING = 2
    DIFFERENT = 3
    INSTALLED = 4

class PackageIndex:

    def __init__(self, *args, **kwargs):

        self.packages = {}

    def find(self, search):

        if isinstance(search, str):
            return self.packages.get(search, None)

        elif isinstance(search, PackageInfo):
            return self.packages.get(search.name, None)

        else: return None

    def insert(self, package_info):

        self.packages[package_info.name] = package_info

    def delete(self, package_info):

        del(self.packages[package_info.name])

    def update(self, package_info):

        package = self.find(package_info)

        if package:
            self.packages[package_info.name] = package.merge(package_info)
        else:
            self.insert(package_info)

    def get_expected(self):

        return { name: str(package_info.expected)
            for name, package_info
            in self.packages.items()
            if package_info.expected
            }

class PackageInfo:

    def __init__(self, *args, **kwargs):

        self.name = kwargs.get("name")
        self.actual = kwargs.get("actual", None)
        self.expected = kwargs.get("expected", None)
        
        b = self.actual and self.expected

        self.__is_same =  self.actual.samefile(self.expected) if b else False

    @property
    def status(self):
        return (
            Status.OK if self.__is_same else
            Status.MISSING if self.actual == None else
            Status.INSTALLED if self.expected == None else
            Status.DIFFERENT
        )

    def merge(self, other):
        return PackageInfo(
            name=self.name,
            actual=other.actual or self.actual,
            expected=other.expected or self.expected,
            )

    def __str__(self, verbose=False):

        text = "[{}] {} -> {}" if verbose else "[{}] {}"

        if self.status == Status.OK:
            return text.format("OK", self.name, str(self.actual.resolve()))
        elif self.status == Status.INSTALLED:
            return text.format("OK", self.name, str(self.actual.resolve()))
        elif self.status == Status.MISSING:
            return text.format("Missing", self.name, str(self.expected.resolve()))
        elif self.status == Status.DIFFERENT:
            return text.format("Different", self.name, str(self.expected.resolve()))

class CatkinManager:

    DEFAULT_PACKAGES_FILE = "ros_packages.yaml"

    def __init__(self, *args, **kwargs):
        
        self.catkin_ws = kwargs.get('catkin_ws', os.getcwd()) # current working directory
        self.packages_file = kwargs.get('packages_file', self.DEFAULT_PACKAGES_FILE)
        self.index = PackageIndex()

        self.__read_packages()
        self.__read_workspace()

    def add_package(self, name, expected, link=False):

        package_info = PackageInfo(name=name, expected=Path(expected))

        self.index.update(package_info)
        self.__write_packages()

        if (link):
            self.__create_link(package_info)

    def remove_package(self, package_info, unlink=False):

        package = self.index.find(package_info)

        if unlink:
            self.__remove_link(package_info)

        if package:
            self.index.delete(package)
            self.__write_packages()

            return package

        else: return False


    def __create_link(self, package_info):

        link_name = Path('{}/src'.format(self.catkin_ws)).joinpath(package_info.name)
        link_target = package_info.expected

        click.echo("ln -s {} {}".format(link_target.resolve(), link_name.resolve()))
        #link_name.symlink_to(package.expected)

    def __remove_link(self, package_info):

        link_name = Path('{}/src'.format(self.catkin_ws)).joinpath(package_info.name)

        click.echo("rm {}".format(link_name))
        #link_name.symlink_to(package.expected)


    def create_links(self, delete=False):
        self.__write_workspace(delete)


    def dependency_graph(self):
        edges = []
   
        #for file in Path('src').rglob('package.xml'):
        for file in list(glob("./src/**/package.xml", recursive=True)):

            tree = ET.ElementTree(file=file)
            root = tree.getroot()

            package = ''

            for elem in root:
                if elem.tag == 'name':
                    package = elem.text
                if elem.tag == 'depend':
                    edges.append('{} -> {}'.format(package, elem.text))

        print("digraph G {{\n{}\n}}".format('\n'.join(edges)))


    def print_info(self, verbose=False):

        for name, package_info in self.index.packages.items():

            if package_info.status == Status.OK:
                click.echo(click.style(package_info.__str__(verbose=verbose), fg="green"))
            elif package_info.status == Status.INSTALLED:
                click.echo(click.style(package_info.__str__(verbose=verbose), fg="yellow"))
            elif package_info.status == Status.MISSING:
                click.echo(click.style(package_info.__str__(verbose=verbose), fg="red"))
            elif package_info.status == Status.DIFFERENT:
                click.echo(click.style(package_info.__str__(verbose=verbose), fg="red"))


    def __read_workspace(self):

        for path in Path("{}/src".format(self.catkin_ws)).iterdir():
            if path.is_symlink() and path.is_dir():
                self.index.update(PackageInfo(name=path.name, actual=path))

        return self.index.packages


    def __read_packages(self):

        with self.__open_packages_file('r') as packages_file:
            try:
                data = yaml.safe_load(packages_file)
                for key, value in data["packages"].items():
                    self.index.update(PackageInfo(name=key, expected=Path(value)))
            except yaml.YAMLError as exc:
                print(exc)

        return self.index.packages


    def __open_packages_file(self, mode='r'):
        return open("{}/{}".format(self.catkin_ws, self.packages_file), mode)


    def __write_packages(self):

        with self.__open_packages_file('w') as packages_file:
            yaml.dump({
                'packages': self.index.get_expected()
            }, packages_file)


    def __write_workspace(self, delete=False):

        for name, package_info in self.index.packages.items():
            if package_info.status == Status.MISSING:
                self.__create_link(package_info)
            #if package_info.status == Status.DIFFERENT:
            if package_info.status == Status.INSTALLED and delete:
                self.__remove_link(package_info)