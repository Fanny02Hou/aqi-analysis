#!/usr/bin/env python3
"""
環境安裝腳本
自動安裝所需的 Python 套件
"""
import subprocess
import sys
import os

def install_requirements():
    """安裝 requirements.txt 中的套件"""
    print("正在安裝所需的 Python 套件...")
    
    try:
        # 使用 pip 安裝套件
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("套件安裝完成！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"套件安裝失敗: {e}")
        return False
    except FileNotFoundError:
        print("找不到 pip，請確認 Python 已正確安裝")
        return False

def check_env_file():
    """檢查 .env 檔案是否存在"""
    if not os.path.exists('.env'):
        print(".env 檔案不存在，請先建立 .env 檔案並設定 API_KEY")
        return False
    
    # 檢查 API_KEY 是否設定
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'MOENV_API_KEY=25ca54e1-90d5-4466-84ce-20d8dc7286d1' not in content:
            print("請在 .env 檔案中設定您的環境部 API Key")
            return False
    
    return True

def main():
    """主程式"""
    print("AQI 地圖專案環境設定")
    print("=" * 40)
    
    # 檢查 .env 檔案
    if not check_env_file():
        print("\n請完成以下設定後重新執行：")
        print("1. 在 .env 檔案中設定您的環境部 API Key")
        print("2. 重新執行此腳本")
        return
    
    # 安裝套件
    if install_requirements():
        print("\n環境設定完成！")
        print("現在可以執行: python aqi_map.py")
    else:
        print("\n環境設定失敗，請檢查錯誤訊息")

if __name__ == "__main__":
    """直接執行 setup.py 時的獨立運行"""
    main()
