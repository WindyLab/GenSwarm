
import os

def rename_lrf_to_mp4(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.lrf'):
                original_path = os.path.join(dirpath, filename)
                new_filename = os.path.splitext(filename)[0] + '.mp4'
                new_path = os.path.join(dirpath, new_filename)

                # 避免覆盖已有文件
                if not os.path.exists(new_path):
                    os.rename(original_path, new_path)
                    print(f"Renamed: {original_path} -> {new_path}")
                else:
                    print(f"Skipped (target exists): {new_path}")

# 示例调用：
# replace this with your actual directory path
rename_lrf_to_mp4("pics")
