import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import  LaunchConfiguration, PathJoinSubstitution, TextSubstitution

def generate_launch_description():

    world_arg = DeclareLaunchArgument(
        'world', default_value='hospital_easy.sdf',
        description='Name of the Gazebo world file to load'
    )

    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Add your own gazebo library path here
    pkg_navi_stack_hw = get_package_share_directory('navi_stack_hw')
    # 1. For hospital models:
    gazebo_models_path = os.path.join(pkg_navi_stack_hw, 'models')
    # 2. For the robot 'package:':
    ros_share_path = os.path.dirname(pkg_navi_stack_hw)

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py'),
        ),
        launch_arguments={'gz_args': [PathJoinSubstitution([
            pkg_navi_stack_hw,
            'worlds',
            LaunchConfiguration('world')
        ]),
        #TextSubstitution(text=' -r -v -v1 --render-engine ogre')],
        TextSubstitution(text=' -r -v -v1')],
        'on_exit_shutdown': 'true'}.items()
    )

    launchDescriptionObject = LaunchDescription()

    # Setting environment variables in ROS 2 style
    launchDescriptionObject.add_action(
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', f"{gazebo_models_path}:{ros_share_path}")
    )
    launchDescriptionObject.add_action(
        AppendEnvironmentVariable('SDF_PATH', gazebo_models_path)
    )

    launchDescriptionObject.add_action(world_arg)
    launchDescriptionObject.add_action(gazebo_launch)

    return launchDescriptionObject