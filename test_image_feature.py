# -*- coding: utf-8 -*-
"""
图片处理功能测试脚本
测试图片会话管理和Gemini图片理解功能
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.image_session_service import ImageSessionService
from config import Config


def test_image_session_service():
    """测试图片会话服务"""
    print("=" * 60)
    print("测试1: 图片会话管理服务")
    print("=" * 60)
    
    # 创建测试目录
    test_upload_dir = os.path.join(Config.BASE_DIR, 'test_uploads')
    
    # 初始化服务
    service = ImageSessionService(upload_dir=test_upload_dir)
    
    # 模拟添加图片
    test_user_id = "test_user_123"
    
    # 创建测试图片文件
    test_image_path = os.path.join(test_upload_dir, 'test_image.jpg')
    if not os.path.exists(test_upload_dir):
        os.makedirs(test_upload_dir, exist_ok=True)
    
    # 创建一个空的测试文件
    with open(test_image_path, 'wb') as f:
        f.write(b'test image content')
    
    print(f"\n✅ 创建测试图片: {test_image_path}")
    
    # 测试添加图片到会话
    count = service.add_image(test_user_id, test_image_path)
    print(f"✅ 添加图片到会话，当前图片数: {count}")
    
    # 测试检查活跃会话
    has_session = service.has_active_session(test_user_id)
    print(f"✅ 检查活跃会话: {has_session}")
    
    # 测试获取图片
    images = service.get_session_images(test_user_id)
    print(f"✅ 获取会话图片: {images}")
    
    # 测试清空会话
    cleared = service.clear_session(test_user_id)
    print(f"✅ 清空会话，删除了 {cleared} 张图片")
    
    # 测试统计信息
    stats = service.get_stats()
    print(f"\n📊 统计信息: {stats}")
    
    # 清理测试文件
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
    if os.path.exists(test_upload_dir) and not os.listdir(test_upload_dir):
        os.rmdir(test_upload_dir)
    
    print("\n✅ 图片会话服务测试通过！")


def test_gemini_image_api():
    """测试Gemini图片理解API（需要真实图片）"""
    print("\n" + "=" * 60)
    print("测试2: Gemini图片理解API")
    print("=" * 60)
    
    # 检查是否有测试图片
    test_image = os.path.join(Config.BASE_DIR, 'test.png')
    
    if not os.path.exists(test_image):
        print(f"\n⚠️ 未找到测试图片: {test_image}")
        print("跳过Gemini API测试")
        return
    
    print(f"\n✅ 找到测试图片: {test_image}")
    
    # 检查当前配置是否支持图片理解
    current_llm = Config.CURRENT_LLM
    llm_config = Config.LLM_MODELS[current_llm]
    use_genai_sdk = llm_config.get('use_genai_sdk', False)
    
    if not use_genai_sdk:
        print(f"\n⚠️ 当前配置的模型 ({current_llm}) 不支持图片理解功能")
        print("请在 config.py 中将 CURRENT_LLM 设置为 'geminiofficial-flash' 或 'geminiofficial-pro'")
        return
    
    print(f"\n✅ 当前模型支持图片理解: {Config.LLM_MODEL}")
    print("\n提示: 完整的API测试需要启动Flask应用并发送真实的微信图片消息")
    print("你可以通过微信向公众号发送图片来测试完整流程")


def main():
    """主测试函数"""
    print("\n" + "🧪" * 30)
    print("图片处理功能测试")
    print("🧪" * 30 + "\n")
    
    try:
        # 测试图片会话服务
        test_image_session_service()
        
        # 测试Gemini API（如果有测试图片）
        test_gemini_image_api()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
        print("\n📝 使用说明:")
        print("1. 用户发送图片 → 系统下载并存储，回复'已接收到图片（共X张），是否继续发送图片还是根据图片提问？'")
        print("2. 用户继续发送图片 → 重复步骤1")
        print("3. 用户发送文本 → 将所有图片和文本一起发送给Gemini，返回AI回复")
        print("4. 每次文本提问后，图片会话自动清空")
        print("\n⚠️ 注意: 图片理解功能需要使用 Gemini 模型（geminiofficial-flash 或 geminiofficial-pro）")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

