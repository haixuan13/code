#!/bin/bash
read -p "请输入数字: " inNum
for ((sum=0,i=1; i<=$inNum; i+=2))
do
sum=$[sum+i]
done
echo 总和为 "$sum"