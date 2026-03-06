#!/usr/bin/env python3
"""
測試環境部 API 連線
"""
import requests
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()
API_KEY = os.getenv('MOENV_API_KEY')

def test_apis():
    """測試可用的 API 端點"""
    
    # 目前只加入已確認可用的 API
    test_urls = [
        {
            'name': '環境部主要 API (需要 API Key)',
            'url': 'https://data.moenv.gov.tw/api/v2/aqx_p_432',
            'params': {'api_key': API_KEY, 'format': 'JSON'}
        }
    ]
    
    for test in test_urls:
        print(f"\n{'='*50}")
        print(f"測試: {test['name']}")
        print(f"URL: {test['url']}")
        
        try:
            response = requests.get(test['url'], params=test['params'], timeout=20)
            print(f"狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"數據類型: {type(data)}")
                
                if isinstance(data, dict):
                    print(f"字典鍵值: {list(data.keys())}")
                    if 'records' in data:
                        print(f"記錄數量: {len(data['records'])}")
                        if data['records']:
                            print(f"第一筆記錄: {data['records'][0]}")
                    elif 'data' in data:
                        print(f"數據數量: {len(data['data'])}")
                elif isinstance(data, list):
                    print(f"列表長度: {len(data)}")
                    if data:
                        print(f"第一筆數據: {data[0]}")
                
                print("連線成功!")
            else:
                print(f"HTTP 錯誤: {response.status_code}")
                print(f"回應內容: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"連線失敗: {e}")
        except Exception as e:
            print(f"其他錯誤: {e}")

if __name__ == "__main__":
    """直接執行 test_api.py 時的獨立運行"""
    print("開始測試環境部 API 連線...")
    print(f"API Key: {API_KEY[:10]}..." if API_KEY else "API Key 未設定")
    test_apis()
