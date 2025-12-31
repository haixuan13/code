#!/bin/bash

echo "=== 9×9乘法表 ==="

for i in {1..9}; do
    for j in {1..9}; do
        result=$((i * j))
        
        # 使用if和elif来判断不同的输出格式
        if [ $result -lt 10 ]; then
            # 个位数，前面加空格对齐
            printf "%d×%d=%d  " $i $j $result
        elif [ $result -lt 100 ]; then
            # 两位数，正常输出
            printf "%d×%d=%d " $i $j $result
        else
            # 三位数（虽然乘法表不会出现，但保留逻辑）
            printf "%d×%d=%d" $i $j $result
        fi
        
        # 每行结束后换行
        if [ $j -eq 9 ]; then
            echo ""
        fi
    done
done