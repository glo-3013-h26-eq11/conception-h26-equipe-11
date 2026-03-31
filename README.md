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
colcon test --packages-skip ldlidar_ros2 integration_tests --event-handlers console_cohesion+
```

### Exemple de test unique
```bash
colcon test --packages-select integration_tests --pytest-args "-k test_proximity_sensor_updates_web" --event-handlers console_cohesion+
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

### Update un submodule du repo
```bash
git submodule update --init --recursive
```

### Run le launch file du web_interface
```bash
colcon build
source install/setup.bash
ros2 launch web_interface web_interface_launch.py
```

### Full clone sur le rover
```bash
git clone https://github.com/glo-3013-h26-eq11/conception-h26-equipe-11.git
cd conception-h26-equipe11
git submodule update --init --recursive
docker run -it --privileged --network host --device=/dev/bus/usb -v /dev:/dev -v .:/home/ws test_louis:latest
cd src/web_interface/web_intersace
npm install
npx vite build
cd ../../..
```

### Code coverage
```bash
mkdir .coverage_folder

colcon test \
            --event-handlers console_direct+ \
            --pytest-args \
              --cov \
              --cov-report=term-missing \
              --cov-report=xml:.coverage_folder/coverage.xml \
              --junitxml=.coverage_folder/pytest.xml \
            | tee .coverage_folder/pytest-coverage.txt

coverage combine $(find src -name '.coverage')

coverage report -m | tee .coverage_folder/pytest-coverage.txt 

coverage xml -o .coverage_folder/coverage.xml --include 'src/*'

coverage html -d .coverage_folder/coverage-html --include="src/*"
```
