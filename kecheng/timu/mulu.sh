#!/bin/bash
if [[ !-d/home/smile/桌面/A ]]; then
	echo "不存在"
	read -p "需要创建？请输入Y|N:" chAns
	if [[ -n $chAns ]]; then
		if [[ $chAns == "Y" || $chAns == "y" ]]; then
			mkdir -p /home/smile/桌面/A
			echo "创建成功"
		fi
	fi
fi