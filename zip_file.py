import os
from datetime import datetime

from shutil import make_archive




# path = os.path.join('LOG')  # 利用 os 模块的 getcwd() 函数 分别获取绝对路径
# target = os.path.join('LOG')
#
# make_archive('LOG', 'zip', os.path.join(os.getcwd()))


import os
import zipfile

def compress_zip(source_dir, target_file):


    zipf = zipfile.ZipFile(target_file, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            zipf.write(os.path.join(root, file))
    zipf.close()

source_dir = '源文件路径'
target_file = '目的文件.zip'


compress_zip(source_dir,target_file)

