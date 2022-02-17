# catkin_manager

Manage catkin workspaces with symlinks.

**Work in progress!**

## The problem

When working with ROS packages from different sources,
the catkin workspace quickly becomes a mess.
Some possible reasons for this are:

* Working with different forks of a package results in name clashes
* Heterogeneity of repository structures, e.g.
  - one package per repository
  - multiple packages per repository
  - repositories containing their own `catkin_ws`
  - etc.

Also, using the same packages in different catkin workspaces requires to have a copy of the code in each of them,
leading to code duplication.

## A solution

Instead of cloning repositories into the catkin workspace,
I create symbolic links from the catkin workspace to the location of the respective ROS packages I want to use.
This tool supports the management of such links.

The tool expects a file named `packages.yaml` inside the catkin workspace:

    catkin_ws/
        build/
        devel/
        src/
        packages.yaml

The file contains a mapping between package names to file system locations:

    packages:
        xivt_robotics_demo: ../ros-packages/xivt_robotics_demo
        present_other_location: ../../examples/present_other_location
        required_but_missing: ../../examples/required_but_missing

## Usage

The tool is used as follows:

To print information about the packages listed in `packages.yaml` and the respective links:

    $ catkin_manager.py info
    Installed: present_not_required
    Different: present_other_location
    Missing: required_but_missing
    OK: xivt_robotics_demo

    $ catkin_manager.py info --verbose
    Installed: present_not_required -> ../../examples/present_not_required
    Different: present_other_location -> ../../examples_other/present_other_location
    Missing: required_but_missing -> ../../examples/required_but_missing
    OK: xivt_robotics_demo -> ../ros-packages/xivt_robotics_demo

To create the links as specified in `packages.yaml`:

    $ catkin_manager.py link
    ln -s ../../examples/present_other_location present_other_location
    ln -s ../../examples/required_but_missing required_but_missing

To also remove links that are not specifed in `packages.yaml`:

    $ catkin_manager.py link -d
    ln -s ../../examples/present_other_location present_other_location
    ln -s ../../examples/required_but_missing required_but_missing
    rm present_not_required
