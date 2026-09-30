from setuptools import find_packages, setup

package_name = 'speed_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='t-hermanns',
    maintainer_email='37556412+t-hermanns@users.noreply.github.com',
    description='Fake distance source, speed controller and mock actuator for ros2-unity-sim.',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'fake_distance_node = speed_control.fake_distance_node:main'
        ],
    },
)
