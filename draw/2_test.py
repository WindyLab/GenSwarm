import os
import json
import shutil


def should_delete(meta_json_path, error_substring):
    """
    判断是否有错误信息需要处理。
    """
    try:
        with open(meta_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 导航到 analysis -> run_result -> local -> result
        analysis = data.get('analysis', {})
        run_result = analysis.get('run_result', {})
        local = run_result.get('local', {})
        result = local.get('result', [])
        for value in result:
            if value in ['Timeout', 'None', 'NONE']:
                return False
        return True  # 如果有问题

    except json.JSONDecodeError:
        print(f"错误: 无法解析 JSON 文件 {meta_json_path}。")
        return False
    except Exception as e:
        print(f"错误: 处理文件 {meta_json_path} 时发生异常: {e}")
        return False


def copy_directories(root_dir, error_substring):
    """
    遍历 root_dir 下的所有子目录，根据检查结果将目录复制到不同的文件夹。
    保留原始目录不变。
    """
    # 创建新目录用于存放有问题和没有问题的目录
    no_error_dir = os.path.join(root_dir, 'no_error')
    error_dir = os.path.join(root_dir, 'error')

    if not os.path.exists(no_error_dir):
        os.makedirs(no_error_dir)
    if not os.path.exists(error_dir):
        os.makedirs(error_dir)

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        if 'cap.json' in filenames:
            meta_json_path = os.path.join(dirpath, 'cap.json')
            print(f"检查文件: {meta_json_path}")
            if should_delete(meta_json_path, error_substring):
                # 如果没有错误，复制到 no_error 目录
                target_dir = error_dir
            else:
                # 如果有错误，复制到 error 目录
                target_dir = no_error_dir


            try:
                # 获取目标目录的完整路径
                target_path = os.path.join(target_dir, os.path.basename(dirpath))
                # 使用 shutil.copytree 来复制整个目录
                shutil.copytree(dirpath, target_path)
                print(f"复制目录: {dirpath} 到 {target_path}")
            except Exception as e:
                print(f"错误: 无法复制目录 {dirpath} 到 {target_path}: {e}")


def main():
    # 设置要遍历的根目录
    root_directory = "/home/derrick/catkin_ws/src/code_llm/workspace/comparative/cap/shaping"  # 请将此路径替换为实际路径

    # 定义要检查的错误子字符串
    error_message = "cannot import name 'main' from 'main'"

    # 检查根目录是否存在
    if not os.path.isdir(root_directory):
        print(f"错误: 根目录 '{root_directory}' 不存在或不是一个目录。")
        return


    # 执行复制操作
    copy_directories(root_directory, error_message)


if __name__ == "__main__":
    main()
