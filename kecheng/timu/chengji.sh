#!/bin/bash
#成绩判断系统
echo "成绩判断系统"
read -p "请输入成绩：" i
if [[ $i -ge 60 ]]; then
	echo "成绩及格"
else
	echo "成绩不及格"
fi
