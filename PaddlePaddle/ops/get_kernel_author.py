import os
import csv
import git
import re
import time
import subprocess
import paddle
import paddle_custom_device
# from IPython import get_ipython

kernel_path = "/home/wangruting/PaddleCustomDevice/backends/mlu/kernels"
online_kernel_path = "https://github.com/PaddlePaddle/PaddleCustomDevice/backends/mlu/kernels/"
# get latest commit and date
repo = git.Repo("/home/wangruting/PaddleCustomDevice")
paddle_commit = paddle_custom_device.mlu.version()
# 3.0-rc0
commit_hash = "b84fac70d1b981285c8ed09a6dbf4c8a2d523233"
# commit = repo.head.commit
commit = repo.commit(commit_hash)
commit_date = time.strftime("%Y%m%d", time.gmtime(commit.committed_date))
# add date to output file name
file_out = "kernel_author_" + commit_date + ".csv"

# 获取所有的_npu.cc文件
def get_filelist(dir):
    file_list = []
    for home, dirs, files in os.walk(dir):
        for filename in files:  
            if filename.endswith(".cc"):
                file_list.append(os.path.join(home, filename))
    return file_list
kernel_file_list = get_filelist(kernel_path)
print("kernel file number is : {}".format(len(kernel_file_list)))

def get_command(command):
    # print(command)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    # print(out)
    return str(out.decode("utf-8"))

def is_valid_date_format(date_str):
    # 正则表达式：匹配 20xx-xx-xx 格式，其中 xx 是数字
    pattern = r'^20\d{2}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_str))

# 获取所有的NPU算子的名称和行数
kernel_support_dict = {}
for file_name in kernel_file_list:
    last_slash_index = file_name.rfind('/')
    if last_slash_index != -1:
        result = file_name[last_slash_index + 1:]
    else:
        result = file_name
    with open(file_name, 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines)):
            line = lines[i]           
            if line.find("PD_REGISTER_PLUGIN_KERNEL(") != -1:
                if line.endswith("(\n"):
                    op_line = lines[i + 1]
                    op_name = op_line.strip().split(",")[0].strip()
                else:
                    op_line = line
                    op_name = op_line.strip().split("(")[1].split(",")[0].strip()
                author_name = get_command(f'cd {kernel_path} && git blame -p -L {i},{i} -- {file_name} | grep "author "')
                author_name = author_name.strip().split("author ")[1]
                time_stamp =  get_command(f'cd {kernel_path} && git blame -L {i},{i} -- {file_name} | cut -d " " -f3')
                index = 3
                while not is_valid_date_format(time_stamp):
                    index += 1
                    time_stamp = get_command(f'cd {kernel_path} && git blame -L {i},{i} -- {file_name} | cut -d " " -f{index}')
                
                # print("author_name = ",author_name, " time = ", time_stamp) 
                kernel_support_dict[op_name] = (author_name, time_stamp, online_kernel_path + result)
print("kernel number is : {}".format(len(kernel_support_dict)))

# SORT first and save to CSV
with open(file_out, 'w') as f:
    for key in sorted (kernel_support_dict.keys()):
        author_name, time_stamp, path = kernel_support_dict[key]
        f.write("{},{},{},{}".format(key, path, author_name, time_stamp))
