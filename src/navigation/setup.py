from setuptools import find_packages, setup

package_name = "navigation"

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
    maintainer="louis",
    maintainer_email="lemes3@ulaval.ca",
    description="TODO: Package description",
    license="TODO: License declaration",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "route_planner_node = navigation.route_planner_node:main",
            "map_processor_node = navigation.map_processor_node:main",
            "current_node_from_aruco_node = navigation.current_node_from_aruco_node:main",
        ],
    },
)
