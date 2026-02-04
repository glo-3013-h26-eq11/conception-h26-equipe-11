# camera

Package ROS 2 pour publier le flux RGB de la caméra OAK-D via DepthAI.

## Exécuter

Build:

- `colcon build`
- `source install/setup.bash`

Launch (wrapper sur `depthai_ros_driver`):

- `ros2 launch camera oakd_rgb.launch.py`

## Paramètres

- `name` (str): nom du node DepthAI (défaut: `oak`)
- `namespace` (str)
- `params_file` (path): fichier YAML de paramètres du driver
- `rgb_profile` (str): format `WIDTH,HEIGHT,FPS` (défaut: `1280,720,10`)
- `rectify_rgb` (bool): rectification via `image_proc` (défaut: `false`)

## Dépendances runtime (Jetson)

- `ros-humble-depthai-ros`

Voir aussi `docs/camera/jetson_setup.md`.
