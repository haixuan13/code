#!/usr/bin/env python3
height = float(input("输入您的身高（米）: "))
weight = float(input("输入您的体重（千克）: "))
bmi= weight / (height ** 2)

# 计算BMI指数
if bmi < 18.5:
    print("您的BMI指数为", bmi, "，属于偏瘦范围。")
elif 18.5 <= bmi < 24:
    print("您的BMI指数为", bmi, "，属于正常范围。")
elif 24 <= bmi < 28:
    print("您的BMI指数为", bmi, "，属于超重范围。")
else:
    print("您的BMI指数为", bmi, "，属于肥胖范围。")