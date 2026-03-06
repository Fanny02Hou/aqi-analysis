#!/usr/bin/env python3
"""
台灣 AQI 即時地圖分析系統 - 主程式
"""
import sys
import os
import pandas as pd

# 添加 scripts 資料夾到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.shelter_aqi_analysis import coordinate_check_main, aqi_map_main
from scripts.setup import main as setup_main
from scripts.test_api import test_apis

def show_menu():
    """顯示主選單"""
    print("\n" + "="*60)
    print("台灣 AQI 即時地圖分析系統")
    print("="*60)
    print("0. 系統說明")
    print("1. 環境設定安裝")
    print("2. 測試 API 連線")
    print("3. 抓取環境部API資料、計算各測站到台北車站的距離、改寫斗六測站的AQI值修改為150，並儲存檔案")
    print("4. 檢查避難收容處所檔案座標、離群值與判斷避難所為室內還室外，並儲存檔案")
    print("5. 建立 台灣環境與社會資料交集地圖 與 生成避難所距離最近監測站空氣品質報告")
    print("6. 離開程式")
    print("="*60)

def show_system_info():
    """顯示系統資訊"""
    print("\n系統資訊")
    print("-" * 50)
    print("專案名稱: 台灣 AQI 即時地圖分析系統")
    print("版本: 1.0.0")
    print("技術棧: Python + Folium + geo_coor + Pandas + NumPy")
    print("數據源: 環境部開放 API + 內政部避難收容處所資料")
    print("架構設計: 模組化程式設計，功能分離執行")
    print("=" * 50)
    print("執行步驟說明:")
    print("Step0. 系統說明")
    print("  - 顯示完整的系統架構說明")
    print("  - 詳細的執行步驟介紹")
    print("  - 輸出檔案總覽")
    print("  - 技術棧和數據源說明")
    print("")
    print("Step1. 環境設定安裝")
    print("  - 設定 MOENV_API_KEY 環境變數")
    print("  - 安裝所需 Python 套件")
    print("")
    print("Step2. 測試 API 連線")
    print("  - 測試環境部 API 連線狀況")
    print("  - 驗證 API 金鑰有效性")
    print("")
    print("Step3. 抓取環境部API資料、計算各測站到台北車站的距離、改寫斗六測站的AQI值修改為150，並儲存檔案")
    print("  - 獲取全台 AQI 測站即時資料")
    print("  - 使用 geo_coor 套件計算 TWD97 距離")
    print("  - 自動修改斗六測站 AQI 值為 150")
    print("  - 輸出: outputs/aqi_station_distances_twd97.csv")
    print("")
    print("Step4. 檢查避難收容處所檔案座標、離群值與判斷避難所為室內還室外，並儲存檔案")
    print("  - 載入避難收容處所點位檔案")
    print("  - 偵測座標系統 (EPSG:4326/EPSG:3826)")
    print("  - 移除異常點位 (座標異常、台灣邊界外)")
    print("  - 使用 shapefile 進行空間查詢")
    print("  - 關鍵字分類室內外避難所")
    print("  - 輸出: data/shelters_cleaned.csv")
    print("  - 輸出: outputs/deleted_shelter.csv")
    print("")
    print("Step5. 建立 台灣環境與社會資料交集地圖 與 生成避難所距離最近監測站空氣品質報告")
    print("  - 直接讀取現有 CSV 檔案 (避免重複計算)")
    print("  - 建立 Folium 雙圖層互動式地圖")
    print("    * 圖層 A: AQI 測站 (依 AQI 值顏色分級)")
    print("    * 圖層 B: 避難收容處所 (室內紫色/室外深藍色)")
    print("  - 使用 Haversine 公式計算避難所到最近測站距離")
    print("  - 風險標籤分類:")
    print("    * High Risk: AQI > 100")
    print("    * Warning: AQI > 50 AND 室外避難所")
    print("  - 輸出: outputs/aqi_map.html")
    print("  - 輸出: outputs/shelter_aqi_analysis.csv")
    print("")
    print("Step6. 離開程式")
    print("=" * 50)
    print("輸出檔案總覽:")
    print("  📄 outputs/aqi_map.html - 互動式地圖")
    print("  📊 outputs/aqi_station_distances_twd97.csv - AQI測站資料")
    print("  🏢 data/shelters_cleaned.csv - 清理後避難所資料")
    print("  🗑️ outputs/deleted_shelter.csv - 異常避難所資料")
    print("  📋 outputs/shelter_aqi_analysis.csv - 避難所風險分析報告")

def run_aqi_data_processing():
    """執行AQI資料處理"""
    print("\n開始執行AQI資料處理...")
    # 從shelter_aqi_analysis導入AQIMapGenerator
    from scripts.shelter_aqi_analysis import AQIMapGenerator
    from dotenv import load_dotenv
    load_dotenv()
    
    API_KEY = os.getenv('MOENV_API_KEY')
    if not API_KEY:
        print("錯誤: 請先設定 .env 檔案中的 MOENV_API_KEY")
        print("提示: 請選擇選項 1 進行環境設定")
        return
    
    # 建立 AQI 地圖生成器
    generator = AQIMapGenerator(API_KEY)
    
    # 獲取數據
    aqi_data = generator.fetch_aqi_data()
    
    if aqi_data:
        print(f"成功獲取 {len(aqi_data)} 個測站數據")
        
        # 計算距離到台北車站 (使用 geo_coor 套件)
        print("\n計算各測站到台北車站的距離 (使用 geo_coor 套件 TWD97 轉換)...")
        distance_data = generator.calculate_distances_to_taipei_station(aqi_data)
        
        # 匯出 CSV (TWD97 距離)
        print("\n匯出 TWD97 距離數據...")
        generator.export_to_csv(distance_data)
        
        print(f"\nAQI資料處理完成！")
        print(f"已修改斗六測站AQI值為150")
        print(f"檔案已儲存至: outputs/aqi_station_distances_twd97.csv")
        print(f"共處理 {len(distance_data)} 個測站")
    else:
        print("無法獲取 AQI 數據")

def run_shelter_coordinate_check():
    """執行避難收容處所座標檢查"""
    print("\n開始執行避難收容處所座標檢查...")
    coordinate_check_main()

def run_map_and_analysis():
    """執行地圖建立與分析"""
    print("\n開始執行地圖建立與分析...")
    aqi_map_main()

def main():
    """主程式"""
    while True:
        show_menu()
        
        try:
            choice = input("\n請選擇功能 (0-6): ").strip()
            
            if choice == '0':
                show_system_info()
                
            elif choice == '1':
                print("\n執行環境設定...")
                setup_main()
                
            elif choice == '2':
                print("\n測試 API 連線...")
                from dotenv import load_dotenv
                load_dotenv()
                test_apis()
                
            elif choice == '3':
                run_aqi_data_processing()
                
            elif choice == '4':
                run_shelter_coordinate_check()
                
            elif choice == '5':
                run_map_and_analysis()
                
            elif choice == '6':
                print("\n感謝使用台灣 AQI 即時地圖分析系統！")
                break
                
            else:
                print("無效選擇，請輸入 0-6 的數字")
                
        except KeyboardInterrupt:
            print("\n\n程式中斷，感謝使用！")
            break
        except Exception as e:
            print(f"發生錯誤: {e}")

if __name__ == "__main__":
    main()
