import os
from glob import glob

from setuptools import find_packages, setup
import os

package_name = "rover"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="devuser",
    maintainer_email="lemes3@ulaval.ca",
    description="TODO: Package description",
    license="Apache-2.0",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "rover_interface_node = rover.rover_interface_node:main",
            "rover_port_usb_node = rover.rover_port_usb_node:main",
        ],
    },
)
