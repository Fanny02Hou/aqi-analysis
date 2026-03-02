import os
import requests
import folium
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import math
import csv
from geo_coor.core import GeoCoordinate

# 載入環境變數
load_dotenv()

# 從 .env 讀取 API Key
API_KEY = os.getenv('MOENV_API_KEY')

class AQIMapGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://data.moenv.gov.tw/api/v2/aqx_p_432"
        # 台北車站座標 (WGS84)
        self.taipei_station = {
            'name': '台北車站',
            'latitude': 25.0478,
            'longitude': 121.5170
        }
        # 初始化 geo_coor 轉換器
        self.geo_converter = GeoCoordinate()
        # 預先計算台北車站的 TWD97 座標
        self.taipei_twd97 = self.geo_converter.wgs84_2_twd97(
            self.taipei_station['longitude'],  # x = 經度
            self.taipei_station['latitude']   # y = 緯度
        )
    
    def fetch_aqi_data(self):
        """獲取全台即時 AQI 數據"""
        # 嘗試主要 API
        data = self._try_primary_api()
        if data:
            return data
            
        # 嘗試備用 API (實際上是同一個 API)
        data = self._try_backup_api()
        if data:
            return data
            
        # 使用測試數據
        print("無法連線到環境部 API，使用測試數據")
        return self._get_test_data()
    
    def _try_primary_api(self):
        """嘗試主要 API - 環境部新域名"""
        try:
            url = self.base_url
            params = {
                'api_key': self.api_key,
                'format': 'JSON'
            }
            
            print(f"嘗試環境部 API: {url}")
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            print(f"API 回應類型: {type(data)}")
            if isinstance(data, dict):
                print(f"API 回應鍵值: {list(data.keys())}")
            
            # 檢查不同的數據格式
            if 'records' in data:
                print(f"找到 {len(data['records'])} 筆記錄")
                return data['records']
            elif 'data' in data:
                print(f"找到數據區塊，包含 {len(data['data'])} 筆記錄")
                return data['data']
            elif isinstance(data, list):
                print(f"直接返回列表，包含 {len(data)} 筆記錄")
                return data
            else:
                print(f"未知的數據格式: {data}")
                # 如果是單一記錄，包裝成列表
                if isinstance(data, dict):
                    return [data]
                else:
                    return None
                
        except Exception as e:
            print(f"環境部 API 連線失敗: {e}")
        return None
    
    def _try_backup_api(self):
        """嘗試備用 API - 實際上是同一個 API"""
        try:
            # 使用相同的 URL，但作為備用機制
            url = "https://data.moenv.gov.tw/api/v2/aqx_p_432"
            params = {
                'api_key': self.api_key,
                'format': 'JSON'
            }
            
            print(f"嘗試備用連線: {url}")
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            print(f"備用 API 成功，數據類型: {type(data)}")
            
            # 處理數據格式
            if isinstance(data, list):
                print(f"直接返回列表，包含 {len(data)} 筆記錄")
                return data
            elif isinstance(data, dict):
                if 'records' in data:
                    print(f"找到 {len(data['records'])} 筆記錄")
                    return data['records']
                elif 'data' in data:
                    print(f"找到數據區塊，包含 {len(data['data'])} 筆記錄")
                    return data['data']
                else:
                    print(f"未知的數據格式: {data}")
                    return [data]
            else:
                print(f"未知的數據類型: {type(data)}")
                return None
                
        except Exception as e:
            print(f"備用 API 連線失敗: {e}")
            return None
    
    def _get_test_data(self):
        """獲取測試數據"""
        test_data = [
            {'sitename': '基隆', 'county': '基隆市', 'aqi': '36', 'pollutant': '', 'status': '良好', 'latitude': '25.129167', 'longitude': '121.760056'},
            {'sitename': '汐止', 'county': '新北市', 'aqi': '31', 'pollutant': '', 'status': '良好', 'latitude': '25.06624', 'longitude': '121.64081'},
            {'sitename': '新店', 'county': '新北市', 'aqi': '35', 'pollutant': '', 'status': '良好', 'latitude': '24.977222', 'longitude': '121.537778'},
            {'sitename': '土城', 'county': '新北市', 'aqi': '31', 'pollutant': '', 'status': '良好', 'latitude': '24.982528', 'longitude': '121.451861'},
            {'sitename': '板橋', 'county': '新北市', 'aqi': '33', 'pollutant': '', 'status': '良好', 'latitude': '25.012972', 'longitude': '121.458667'},
        ]
        print(f"使用測試數據，共 {len(test_data)} 筆記錄")
        return test_data
    
    def _get_aqi_status(self, aqi_value):
        """根據 AQI 值判斷空氣品質狀態"""
        try:
            aqi = int(aqi_value)
            if aqi <= 50:
                return '良好'
            elif aqi <= 100:
                return '普通'
            elif aqi <= 150:
                return '對敏感族群不健康'
            elif aqi <= 200:
                return '對所有族群不健康'
            elif aqi <= 300:
                return '非常不健康'
            else:
                return '危害'
        except (ValueError, TypeError):
            return '未知'
    
    def get_aqi_color(self, aqi):
        """根據 AQI 值返回對應的顏色"""
        try:
            aqi_value = int(aqi)
            
            # 優化分色：0-50 綠色、51-100 黃色、101+ 紅色
            if aqi_value <= 50:
                return 'green'
            elif aqi_value <= 100:
                return 'yellow'
            else:
                return 'red'
        except (ValueError, TypeError):
            return 'gray'
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """使用 geo_coor 套件轉換為 TWD97 後計算距離（公里）"""
        # 使用 geo_coor 套件將 WGS84 轉換為 TWD97
        # 注意：wgs84_2_twd97(x, y) 其中 x=經度, y=緯度
        x1, y1 = self.geo_converter.wgs84_2_twd97(lon1, lat1)
        x2, y2 = self.geo_converter.wgs84_2_twd97(lon2, lat2)
        
        # 使用 TWD97 平面座標計算歐幾里得距離
        dx = x2 - x1
        dy = y2 - y1
        distance_meters = math.sqrt(dx**2 + dy**2)
        
        # 轉換為公里
        distance_km = distance_meters / 1000
        
        return round(distance_km, 2)
    
    def calculate_distances_to_taipei_station(self, aqi_data):
        """計算每個測站到台北車站的距離 (使用 geo_coor 套件)"""
        results = []
        
        taipei_lat = self.taipei_station['latitude']
        taipei_lon = self.taipei_station['longitude']
        
        print(f"台北車站座標 (WGS84): {taipei_lat}, {taipei_lon}")
        print(f"台北車站座標 (TWD97): X={self.taipei_twd97[0]:.2f}, Y={self.taipei_twd97[1]:.2f}")
        
        for station in aqi_data:
            try:
                # 獲取測站資訊
                site_name = station.get('sitename', '未知測站')
                county = station.get('county', station.get('sitename', '未知'))
                lat = float(station.get('latitude', 0))
                lon = float(station.get('longitude', 0))
                aqi = station.get('aqi', 'N/A')
                pollutant = station.get('pollutant', 'N/A')
                status = station.get('status', 'N/A')
                
                if lat == 0 or lon == 0:
                    continue
                
                # 使用 geo_coor 套件計算距離
                distance = self.calculate_distance(lat, lon, taipei_lat, taipei_lon)
                
                result = {
                    '測站名稱': site_name,
                    '所在縣市': county,
                    '緯度(WGS84)': lat,
                    '經度(WGS84)': lon,
                    '距離台北車站_TWD97(公里)': distance,
                    'AQI': aqi,
                    '主要污染物': pollutant,
                    '空氣品質狀態': status
                }
                
                results.append(result)
                
            except (ValueError, KeyError) as e:
                print(f"處理測站 {station.get('sitename', '未知')} 距離計算時發生錯誤: {e}")
                continue
        
        return results
    
    def export_to_csv(self, distance_data):
        """匯出距離數據到 CSV"""
        if not distance_data:
            print("沒有數據可匯出")
            return
        
        # 確保 outputs 資料夾存在
        os.makedirs('outputs', exist_ok=True)
        
        # 匯出 TWD97 距離數據
        output_file = 'outputs/aqi_station_distances_twd97.csv'
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = distance_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(distance_data)
        
        print(f"TWD97 距離數據已匯出: {output_file}")
        print(f"共匯出 {len(distance_data)} 筆記錄")
    
    def get_location_name(self, station):
        """獲取測站位置名稱"""
        county = station.get('county', '')
        sitename = station.get('sitename', '')
        
        if county and county != sitename:
            return f"{county} - {sitename}"
        else:
            return sitename
    
    def create_map(self, aqi_data):
        """建立 AQI 地圖"""
        # 建立以台灣為中心的地圖
        taiwan_center = [23.8, 121.0]
        m = folium.Map(location=taiwan_center, zoom_start=7)
        
        # 添加標題和圖例
        title_html = '''
        <h3 align="center" style="font-size:30px"><b>台灣即時空氣品質指標 (AQI) 地圖</b></h3>
        <div align="center" style="font-size:28px">
        <span style="color:green; font-weight:bold">● 良好 (0-50)</span> | 
        <span style="color:orange; font-weight:bold">● 普通 (51-100)</span> | 
        <span style="color:red; font-weight:bold">● 不健康 (101+)</span>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # 添加測站標記
        for station in aqi_data:
            try:
                lat = float(station.get('latitude', 0))
                lon = float(station.get('longitude', 0))
                
                if lat == 0 or lon == 0:
                    continue
                
                # 獲取測站資訊
                site_name = station.get('sitename', '未知測站')
                county = station.get('county', '')
                aqi = station.get('aqi', 'N/A')
                pollutant = station.get('pollutant', 'N/A')
                status = station.get('status', 'N/A')
                
                # 獲取顏色
                color = self.get_aqi_color(aqi)
                
                # 建立彈出視窗內容
                popup_content = f"""
                <b>{site_name}</b><br>
                位置: {county}<br>
                AQI: <span style="color:black; font-weight:bold">{aqi}</span><br>
                主要污染物: {pollutant}<br>
                空氣品質: {status}<br>
                座標: ({lat:.4f}, {lon:.4f})
                """
                
                # 添加標記
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=8,
                    popup=popup_content,
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                    weight=2,
                    tooltip=f"{site_name} - AQI: {aqi}"
                ).add_to(m)
                
            except (ValueError, KeyError) as e:
                print(f"處理測站 {station.get('sitename', '未知')} 時發生錯誤: {e}")
                continue
        
        return m
    
    def save_map(self, aqi_map):
        """儲存地圖到檔案"""
        try:
            # 確保 outputs 資料夾存在
            os.makedirs('outputs', exist_ok=True)
            
            # 儲存地圖
            output_file = 'outputs/aqi_map.html'
            aqi_map.save(output_file)
            
            return output_file
        except Exception as e:
            print(f"儲存地圖時發生錯誤: {e}")
            return None

def main():
    """主程式"""
    if not API_KEY:
        print("錯誤: 請在 .env 檔案中設定 MOENV_API_KEY")
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
        else:
            print("地圖儲存失敗")
    else:
        print("無法獲取 AQI 數據")

if __name__ == "__main__":
    """直接執行 aqi_map_clean.py 時的獨立運行"""
    main()
