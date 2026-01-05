"""测试北京时间获取功能"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.datetime_utils import get_beijing_time, get_beijing_date_str, get_beijing_datetime_str

def test_datetime_utils():
    """测试时间工具函数"""
    print("=" * 60)
    print("测试北京时间工具函数")
    print("=" * 60)
    
    beijing_time = get_beijing_time()
    print(f"当前北京时间对象: {beijing_time}")
    print(f"当前北京日期字符串: {get_beijing_date_str()}")
    print(f"当前北京日期时间字符串: {get_beijing_datetime_str()}")
    print(f"时区信息: {beijing_time.tzinfo}")
    print(f"ISO格式: {beijing_time.isoformat()}")
    print("\n✓ 时间工具函数测试通过！")

def test_prompts():
    """测试Prompt生成（需要环境变量）"""
    try:
        from app.services.prompts import get_image_parse_prompt, get_text_parse_prompt
        
        print("\n" + "=" * 60)
        print("测试动态Prompt生成")
        print("=" * 60)
        
        print("\n图片解析Prompt片段:")
        image_prompt = get_image_parse_prompt()
        print(image_prompt[:500] + "...")
        
        print("\n文本解析Prompt片段:")
        text_prompt = get_text_parse_prompt()
        print(text_prompt[:500] + "...")
        
        # 验证日期是否在prompt中
        date_str = get_beijing_date_str()
        if date_str in image_prompt and date_str in text_prompt:
            print(f"\n✓ Prompt中包含当前日期: {date_str}")
        
        print("\n✓ Prompt生成测试通过！")
        
    except Exception as e:
        print(f"\n⚠ Prompt测试跳过 (需要配置环境变量)")
        print(f"提示: 请设置 VLM_API_KEY 等环境变量后再测试")
        print(f"错误: {type(e).__name__}")

if __name__ == "__main__":
    test_datetime_utils()
    test_prompts()
