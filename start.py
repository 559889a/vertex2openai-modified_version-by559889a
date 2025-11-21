"""
Windows 启动脚本
在项目根目录运行此脚本以启动服务
"""
from dotenv import load_dotenv
import os
import sys
import uvicorn

# 添加 app 目录到 Python 路径，以便正确导入模块
app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

def check_python_version():
    """检查 Python 版本"""
    if sys.version_info < (3, 8):
        print("错误：需要 Python 3.8 或更高版本")
        print(f"当前版本：{sys.version}")
        sys.exit(1)
    print(f"✓ Python 版本检查通过：{sys.version}")

def load_env_file():
    """加载 .env 文件"""
    if not os.path.exists('.env'):
        print("警告：未找到 .env 文件")
        print("请参考 WINDOWS_SETUP.md 创建 .env 配置文件")
        return False
    
    load_dotenv()
    print("✓ 已加载 .env 配置文件")
    return True

def check_required_env():
    """检查必需的环境变量"""
    api_key = os.getenv('API_KEY')
    vertex_key = os.getenv('VERTEX_EXPRESS_API_KEY')
    google_creds = os.getenv('GOOGLE_CREDENTIALS_JSON')
    creds_dir = os.getenv('CREDENTIALS_DIR', './credentials')
    
    # 检查 API_KEY
    if not api_key:
        print("错误：未设置 API_KEY 环境变量")
        print("请在 .env 文件中设置 API_KEY")
        return False
    print(f"✓ API_KEY 已设置")
    
    # 检查至少有一种凭证方式
    has_credentials = False
    
    if vertex_key:
        print(f"✓ 使用 Vertex Express API Key")
        has_credentials = True
    
    if google_creds:
        print(f"✓ 使用 GOOGLE_CREDENTIALS_JSON")
        has_credentials = True
    
    if os.path.exists(creds_dir) and os.path.isdir(creds_dir):
        json_files = [f for f in os.listdir(creds_dir) if f.endswith('.json')]
        if json_files:
            print(f"✓ 在 {creds_dir} 中找到 {len(json_files)} 个服务账号文件")
            has_credentials = True
    
    if not has_credentials:
        print("错误：未找到任何有效的 Google Cloud 凭证")
        print("请配置以下之一：")
        print("  1. VERTEX_EXPRESS_API_KEY")
        print("  2. GOOGLE_CREDENTIALS_JSON")
        print("  3. CREDENTIALS_DIR 中的 .json 文件")
        print("详情请参考 WINDOWS_SETUP.md")
        return False
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("OpenAI to Gemini Adapter - Windows 启动脚本")
    print("=" * 60)
    print()
    
    # 检查 Python 版本
    check_python_version()
    
    # 加载环境变量
    if not load_env_file():
        print("\n提示：你也可以手动设置环境变量后运行此脚本")
    
    # 检查必需的环境变量
    if not check_required_env():
        print("\n启动失败！请检查配置。")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("所有检查通过！正在启动服务...")
    print("=" * 60)
    print()
    print("服务将运行在: http://localhost:8050")
    print("按 Ctrl+C 停止服务")
    print()
    
    # 启动服务
    try:
        # 切换到 app 目录作为工作目录
        os.chdir(app_dir)
        
        port = int(os.getenv("APP_PORT", 8050))
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n服务已停止")
    except Exception as e:
        print(f"\n错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()