import os
import sys
import csv

# 输入文件
#kernel_author_file
op_file_1 = sys.argv[1]
# part_ops_file
op_file_2 = sys.argv[2]

# 输出文件
ouptut_comm = op_file_2[:-4] + "kernel_author.csv"
output_diff = op_file_2[:-4] + "no_kernel.csv"
# 获取模型算子列表
op_list_1 = {}
with open(op_file_1) as f:
    for row in csv.reader(f):
        op_list_1[row[0]] = row
print(f"op number of {op_file_1} is {len(op_list_1)}")

# 获取模型算子列表
op_list_2 = []
with open(op_file_2) as f:
    for row in csv.reader(f):
        op_list_2.append(row[0])
print(f"op number of {op_file_2} is {len(op_list_2)}")


# 获取 part 算子
op_comm_list = []
op_diff_list = []
for op_name in op_list_2:
    if op_name in op_list_1:
        op_comm_list.append(op_list_1[op_name])
    else:
        op_diff_list.append(op_name)
print(f"comm op number is {len(op_comm_list)}")
print(f"diff of {op_file_2} is {len(op_diff_list)}")

# 先排序
op_comm_list.sort()
op_diff_list.sort()

# 写入CSV文件
with open(ouptut_comm, 'w') as f:
    for item in op_comm_list:
        f.write("%s\n" % item)
with open(output_diff, 'w') as f:
    for item in op_diff_list:
        f.write("%s\n" % item)
