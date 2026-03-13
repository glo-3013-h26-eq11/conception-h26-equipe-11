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
            "route_planner = navigation.route_planner_node:main",
            "map_processor_node = navigation.map_processor_node:main",
            "goal_selector_node = navigation.goal_selector_node:main",
            "aruco_localizer_node = navigation.aruco_localizer_node:main",
            "route_executor_node = navigation.route_executor_node:main",
        ],
    },
)
