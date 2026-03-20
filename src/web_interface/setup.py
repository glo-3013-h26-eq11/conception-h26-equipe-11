from setuptools import find_packages, setup
import os
from glob import glob

package_name = "web_interface"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (
            os.path.join("share", package_name, "launch"),
            glob(os.path.join("launch", "*launch.py*")),
        ),
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
            "static_web_server = web_interface.static_web_server:main",
            "console_node = web_interface.console_node:main",
            "system_health_node = web_interface.system_health_node:main",
        ],
    },
)
