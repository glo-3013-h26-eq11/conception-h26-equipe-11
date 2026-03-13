from setuptools import find_packages, setup

package_name = "central_manager"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="devuser",
    maintainer_email="olcao1@ulaval.ca",
    description="Central orchestration of system modules",
    license="Apache-2.0",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "enforcer_manager_node = central_manager.enforcer_manager_node:main",
            "left_turn_enforcer_node = central_manager.left_turn_enforcer:main",
        ],
    },
)
