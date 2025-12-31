#!/bin/bash
if [[ ! -d /root/A ]]; then
    echo "目录不存在，创建目录 /root/A"
    read -p '是否确认创建目录 /root/A？(y/n):' chans
    if [[ -n $chans ]];then
        if [[ $chans='y' || $chans='Y' ]];then
            mkdir /root/A
            echo "目录 /root/A 创建成功"
        else
            echo "取消创建目录 /root/A"
        fi
    fi
fi