from setuptools import setup, find_packages

setup(
    name='catkin_manager',
    version='0.0.1',
    description='',
    author='Niels Hoppe',
    author_email='niels.hoppe@fokus.fraunhofer.de',
    packages=find_packages(include=['catkin_manager', 'catkin_manager.*']),
    install_requires=[
        'Click',
        'GitPython',
        'PyYAML',
    ],
    entry_points={
        'console_scripts': ['catkin_manager=catkin_manager.cli:app']
    }
)