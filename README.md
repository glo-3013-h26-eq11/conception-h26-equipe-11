# conception-h26-equipe-11
Repo centrale pour le cours de conception H26

## Environnement dev
Vous avez deux choix : 

1. Installer [ros2-humble](https://docs.ros.org/en/humble/index.html) localement
2. Faire le développement sur un container _Docker_ : [Comme ici](https://docs.ros.org/en/humble/How-To-Guides/Setup-ROS-2-with-VSCode-and-Docker-Container.html)

## Commandes

### Build le projet
```bash
colcon build
```

### Fix les erreurs de formattage
```bash
black .
```

### Run les tests avec tous les logs
```bash
colcon test --event-handlers console_cohesion+
```

### Créer un package/module

Voir la [doc](https://docs.ros.org/en/humble/How-To-Guides/Developing-a-ROS-2-Package.html#python-packages) pour plus d'info.

Ou ce [tutoriel](https://docs.ros.org/en/eloquent/Tutorials/Creating-Your-First-ROS2-Package.html).

```bash
ros2 pkg create --build-type ament_python --node-name my_node my_package
```

### Run un module

**Linux**
```bash
source install/setup.bash
ros2 run my_package my_node
```

### Run le launch file du web_interface
```bash
colcon build
source install/setup.bash
ros2 launch web_interface web_interface_launch.py
```