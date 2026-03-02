#!/usr/bin/env python3
"""
台灣 AQI 即時地圖分析系統 - 主程式
"""
import sys
import os

# 添加 scripts 資料夾到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.aqi_map import AQIMapGenerator
from scripts.setup import main as setup_main
from scripts.test_api import test_apis

def show_menu():
    """顯示主選單"""
    print("\n" + "="*50)
    print("台灣 AQI 即時地圖分析系統")
    print("="*50)
    print("1. 環境設定安裝")
    print("2. 生成 AQI 地圖")
    print("3. 測試 API 連線")
    print("4. 顯示系統資訊")
    print("5. 離開程式")
    print("="*50)

def show_system_info():
    """顯示系統資訊"""
    print("\n系統資訊")
    print("-" * 30)
    print("專案名稱: 台灣 AQI 即時地圖分析系統")
    print("版本: 1.0.0")
    print("技術棧: Python + Folium + geo_coor")
    print("數據源: 環境部開放 API")
    print("功能特色:")
    print("   - 即時 AQI 數據獲取")
    print("   - TWD97 高精度距離計算")
    print("   - 互動式地圖視覺化")
    print("   - CSV 數據匯出")
    print("輸出檔案:")
    print("   - outputs/aqi_map.html")
    print("   - outputs/aqi_station_distances_twd97.csv")

def run_aqi_analysis():
    """執行 AQI 分析"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        API_KEY = os.getenv('MOENV_API_KEY')
        if not API_KEY:
            print("錯誤: 請先設定 .env 檔案中的 MOENV_API_KEY")
            print("提示: 請選擇選項 1 進行環境設定")
            return
        
        print("\n開始執行 AQI 分析...")
        
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
            
            # 建立地圖
            print("\n建立 AQI 地圖...")
            aqi_map = generator.create_map(aqi_data)
            
            # 儲存地圖
            output_file = generator.save_map(aqi_map)
            
            if output_file:
                print("\n任務完成！")
                print(f"AQI 地圖生成完成：{output_file}")
                print(f"TWD97 距離計算完成：outputs/aqi_station_distances_twd97.csv")
                print(f"共處理 {len(distance_data)} 個測站 (使用 geo_coor 套件 TWD97 轉換)")
                print("\n提示: 請開啟 outputs/aqi_map.html 查看互動式地圖")
            else:
                print("地圖儲存失敗")
        else:
            print("無法獲取 AQI 數據")
            
    except Exception as e:
        print(f"執行 AQI 分析時發生錯誤: {e}")

def main():
    """主程式"""
    while True:
        show_menu()
        
        try:
            choice = input("\n請選擇功能 (1-5): ").strip()
            
            if choice == '1':
                print("\n執行環境設定...")
                setup_main()
                
            elif choice == '2':
                run_aqi_analysis()
                
            elif choice == '3':
                print("\n測試 API 連線...")
                from dotenv import load_dotenv
                load_dotenv()
                test_apis()
                
            elif choice == '4':
                show_system_info()
                
            elif choice == '5':
                print("\n感謝使用台灣 AQI 即時地圖分析系統！")
                break
                
            else:
                print("無效選擇，請輸入 1-5 的數字")
                
        except KeyboardInterrupt:
            print("\n\n程式中斷，感謝使用！")
            break
        except Exception as e:
            print(f"發生錯誤: {e}")

if __name__ == "__main__":
    main()
