import os
import zipfile
from datetime import datetime


def compress_zip(source_dir, target_file):
    """
    压缩指定目录到zip文件

    Args:
        source_dir (str): 源目录路径
        target_file (str): 目标zip文件路径

    Returns:
        bool: 压缩是否成功
    """
    try:
        if not os.path.exists(source_dir):
            print(f"源目录不存在: {source_dir}")
            return False

        with zipfile.ZipFile(target_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 计算相对路径，避免压缩包中包含完整路径
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)

        print(f"压缩完成: {target_file}")
        return True

    except Exception as e:
        print(f"压缩失败: {e}")
        return False


def compress_files(file_list, target_file):
    """
    压缩指定文件列表到zip文件

    Args:
        file_list (list): 文件路径列表
        target_file (str): 目标zip文件路径

    Returns:
        bool: 压缩是否成功
    """
    try:
        with zipfile.ZipFile(target_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_list:
                if os.path.exists(file_path):
                    # 只保留文件名，不包含路径
                    arcname = os.path.basename(file_path)
                    zipf.write(file_path, arcname)
                else:
                    print(f"文件不存在，跳过: {file_path}")

        print(f"文件压缩完成: {target_file}")
        return True

    except Exception as e:
        print(f"文件压缩失败: {e}")
        return False


if __name__ == '__main__':
    # 示例用法
    source_dir = 'LOG'  # 源文件路径
    target_file = f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'  # 目的文件.zip

    if os.path.exists(source_dir):
        compress_zip(source_dir, target_file)
    else:
        print(f"目录不存在: {source_dir}")

