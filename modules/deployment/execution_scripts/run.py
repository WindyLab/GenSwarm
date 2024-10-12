import os
import pickle
import sys
import threading
from xmlrpc.client import escape

import rospy
from code_llm.srv import GetTargetPositions, GetCharPoints, GetCharPointsRequest


def get_target_positions():
    rospy.wait_for_service('/get_target_positions')
    try:
        get_target_positions = rospy.ServiceProxy('/get_target_positions', GetTargetPositions)
        response = get_target_positions()
        return {info.id: (info.position.x, info.position.y) for info in response.target_positions}
    except rospy.ServiceException as e:
        print(f"Service call failed: {e}")
        return {}


def get_contour_points(character):
    rospy.wait_for_service('/get_char_points')
    try:
        get_char_points = rospy.ServiceProxy('/get_char_points', GetCharPoints)
        request = GetCharPointsRequest(character=character)
        response = get_char_points(request)
        points = [(point.x, point.y) for point in response.points]
        return points
    except rospy.ServiceException as e:
        print(f"Service call failed: {e}")
        return []


def run_robot(robot_id, target_position, formation_points, task=None):
    from local_skill import initialize_ros_node, run_loop
    initialize_ros_node(robot_id=robot_id, target_position=target_position, formation_points=formation_points,
                        assigned_task=task)
    run_loop()


def run_multiple_robot(start_idx, end_idx):
    rospy.init_node(f'multi_robot_publisher_node{start_idx}_{end_idx}', anonymous=True)
    target_positions = get_target_positions()
    # char_points = get_contour_points('R')
    char_points = [(1, -1), (1, 1), (0, 0), (1, 0), (2, 0)]
    threads = []
    assigned = False
    try:
        with open(os.path.join('allocate_result.pkl'), 'rb') as f:
            task = pickle.load(f)
            assigned = True
    except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
        print(f"Error loading file: {e}. Initializing a default task.")

    for i in range(start_idx, end_idx + 1):
        assigned_task = task[i] if assigned else None
        thread = threading.Thread(target=run_robot, args=(i, target_positions[i], char_points,assigned_task))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    a = sys.argv
    # start_id = 1
    # end_id = 9
    start_id = int(sys.argv[1])
    end_id = int(sys.argv[2])

    run_multiple_robot(start_id, end_id)
