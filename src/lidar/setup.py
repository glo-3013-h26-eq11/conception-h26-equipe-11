from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'lidar'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='devuser',
    maintainer_email='devuser@todo.todo',
    description='LIDAR package with wall follower',
    license='MIT',
    entry_points={
        'console_scripts': [
            'wall_follower = lidar.wall_follower:main',
        ],
    },
)
