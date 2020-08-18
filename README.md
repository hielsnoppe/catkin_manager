# catkin_manager

**Work in progress!**

Expects the following:

    catkin_ws/src/
        packages.yaml
        
Where `packages.yaml` looks like this:

    packages:
        xivt_robotics_demo: ../ros-packages/xivt_robotics_demo

Use like this:

    catkin_manager.py info
    catkin_manager.py link
