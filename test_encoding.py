# -*- coding: utf-8 -*-
"""
测试中文编码问题
对比 requests.post 使用 json= 参数和手动序列化的区别
"""
import json
import requests

# 测试数据
data = {
    "touser": "test_user",
    "msgtype": "text",
    "text": {
        "content": "您好！我是您的"在办小助手"，很高兴为您服务。😊"
    }
}

print("=" * 60)
print("测试中文编码问题")
print("=" * 60)

# 方式1：使用 json= 参数（会产生乱码）
print("\n【方式1】使用 requests.post(json=data) - 会产生 Unicode 转义")
json_str_1 = json.dumps(data)  # 默认 ensure_ascii=True
print("JSON 字符串:")
print(json_str_1)
print("\n问题：中文被转义成 \\uXXXX 格式")

# 方式2：手动序列化，ensure_ascii=False（正确方式）
print("\n" + "=" * 60)
print("【方式2】手动序列化 ensure_ascii=False - 中文正常显示")
json_str_2 = json.dumps(data, ensure_ascii=False)
print("JSON 字符串:")
print(json_str_2)
print("\n✅ 中文保持原样，不会被转义")

print("\n" + "=" * 60)
print("结论：必须使用 ensure_ascii=False 来保留中文字符")
print("=" * 60)

