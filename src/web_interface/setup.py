from setuptools import find_packages, setup
import os
from glob import glob

package_name = "web_interface"

dist_files = [
    (
        os.path.join("share", package_name, "dist", os.path.relpath(os.path.dirname(f), "web_interface/web_interface/dist")),
        [f],
    )
    for f in glob("web_interface/web_interface/dist/**/*", recursive=True)
    if os.path.isfile(f)
]

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
    ] + dist_files,
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
        "console_scripts": ["static_web_server = web_interface.static_web_server:main"],
    },
)
