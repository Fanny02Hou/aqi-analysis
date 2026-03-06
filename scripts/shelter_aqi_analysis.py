import pandas as pd
import numpy as np
import math
import os
import requests
import folium
import csv
import warnings
import re
from dotenv import load_dotenv
from pyproj import CRS, Transformer
import geopandas as gpd
from shapely.geometry import Point
from geo_coor.core import GeoCoordinate

warnings.filterwarnings('ignore')

# 載入環境變數
load_dotenv()

# 從 .env 讀取 API Key
API_KEY = os.getenv('MOENV_API_KEY')

# ============================================================================
# 座標檢查與清理功能 (來自 coordinate_check_results.py)
# ============================================================================

def load_env_config():
    """
    載入環境變數配置
    """
    load_dotenv()
    target_crs = os.getenv('target_crs', 'EPSG3826')
    return target_crs

def detect_coordinate_system(longitudes, latitudes):
    """
    判斷座標系統是經緯度（EPSG:4326）還是二度分帶（EPSG:3826）
    
    Args:
        longitudes (pd.Series): 經度數列
        latitudes (pd.Series): 緯度數列
    
    Returns:
        str: 座標系統判斷結果
    """
    # 經緯度範圍檢查
    lon_min, lon_max = longitudes.min(), longitudes.max()
    lat_min, lat_max = latitudes.min(), latitudes.max()
    
    print(f"經度範圍: {lon_min:.6f} ~ {lon_max:.6f}")
    print(f"緯度範圍: {lat_min:.6f} ~ {lat_max:.6f}")
    
    # 判斷座標系統
    # 經緯度（EPSG:4326）：台灣地區經度約 119-123，緯度約 21-26
    # 二度分帶（EPSG:3826）：X座標約 170000-350000，Y座標約 2400000-2800000
    
    if (lon_min >= 100 and lon_max <= 125 and 
        lat_min >= 20 and lat_max <= 30):
        return "EPSG:4326"
    elif (lon_min >= 100000 and lon_max <= 400000 and 
          lat_min >= 2000000 and lat_max <= 3000000):
        return "EPSG:3826"
    else:
        # 進一步檢查
        taiwan_lon_count = ((longitudes >= 119) & (longitudes <= 123)).sum()
        taiwan_lat_count = ((latitudes >= 21) & (latitudes <= 26)).sum()
        
        twd97_x_count = ((longitudes >= 170000) & (longitudes <= 350000)).sum()
        twd97_y_count = ((latitudes >= 2400000) & (latitudes <= 2800000)).sum()
        
        if taiwan_lon_count > len(longitudes) * 0.8 and taiwan_lat_count > len(latitudes) * 0.8:
            return "EPSG:4326"
        elif twd97_x_count > len(longitudes) * 0.8 and twd97_y_count > len(latitudes) * 0.8:
            return "EPSG:3826"
        else:
            return "未知座標系統"

def convert_to_target_crs(df, source_crs, target_crs):
    """
    將座標轉換為目標座標系統
    
    Args:
        df (pd.DataFrame): 包含經緯度的資料框
        source_crs (str): 來源座標系統
        target_crs (str): 目標座標系統
    
    Returns:
        pd.DataFrame: 加入目標座標系統座標的資料框
    """
    print(f"開始轉換座標系統: {source_crs} -> {target_crs}")
    
    # 定義座標系統對應和格式化
    def format_epsg(crs_string):
        """確保EPSG格式正確（包含冒號）"""
        if isinstance(crs_string, str):
            # 移除可能的空白字符
            crs_clean = crs_string.strip()
            # 如果沒有冒號，添加冒號
            if crs_clean.upper().startswith('EPSG') and ':' not in crs_clean:
                # 提取數字部分
                if crs_clean.upper() == 'EPSG4326':
                    return 'EPSG:4326'
                elif crs_clean.upper() == 'EPSG3826':
                    return 'EPSG:3826'
                elif crs_clean.upper() == 'EPSG3824':
                    return 'EPSG:3824'
                else:
                    # 嘗試提取數字
                    match = re.search(r'(\d+)', crs_clean)
                    if match:
                        return f'EPSG:{match.group(1)}'
            return crs_clean
        return crs_string
    
    # 格式化座標系統
    source_epsg = format_epsg(source_crs)
    target_epsg = format_epsg(target_crs)
    
    crs_mapping = {
        "EPSG:4326": "EPSG:4326",
        "EPSG:3824": "EPSG:3824",  # TWD97度
        "EPSG:3826": "EPSG:3826",  # TWD97公尺
    }
    
    print(f"格式化後的來源座標系統: {source_epsg}")
    print(f"格式化後的目標座標系統: {target_epsg}")
    
    # 如果來源和目標相同，檢查是否需要為後續處理準備欄位
    if source_epsg == target_epsg:
        print("✅ 座標系統已符合目標，無需轉換")
        
        # 無論目標座標系統是什麼，都需要TWD97欄位供後續空間查詢使用
        if 'TWD97_lon' not in df.columns or 'TWD97_lat' not in df.columns:
            print("為後續空間查詢準備TWD97座標欄位")
            if target_epsg == "EPSG:3826":
                # 如果已經是TWD97，直接複製
                df['TWD97_lon'] = df['經度']
                df['TWD97_lat'] = df['緯度']
            elif target_epsg == "EPSG:4326":
                # 如果是WGS84，需要轉換為TWD97供空間查詢
                print("轉換WGS84座標為TWD97供空間查詢使用")
                transformer = Transformer.from_crs("EPSG:4326", "EPSG:3826", always_xy=True)
                
                def transform_coords(lon, lat):
                    try:
                        x, y = transformer.transform(lon, lat)
                        return x, y
                    except:
                        return np.nan, np.nan
                
                coords = df.apply(lambda row: transform_coords(row['經度'], row['緯度']), axis=1)
                df['TWD97_lon'] = [coord[0] for coord in coords]
                df['TWD97_lat'] = [coord[1] for coord in coords]
                
                # 移除轉換失敗的記錄
                valid_mask = ~df['TWD97_lon'].isna() & ~df['TWD97_lat'].isna()
                df = df[valid_mask].copy()
                print(f"TWD97轉換完成，剩餘 {len(df)} 筆有效資料")
        else:
            print("TWD97座標欄位已存在")
        
        # 同時準備目標座標系統的欄位以保持一致性
        if target_epsg == "EPSG:4326":
            if 'WGS84_lon' not in df.columns or 'WGS84_lat' not in df.columns:
                print("為一致性準備WGS84座標欄位")
                df['WGS84_lon'] = df['經度']
                df['WGS84_lat'] = df['緯度']
        
        return df
    
    try:
        # 建立轉換器
        transformer = Transformer.from_crs(source_epsg, target_epsg, always_xy=True)
        
        def transform_coords(lon, lat):
            try:
                x, y = transformer.transform(lon, lat)
                return x, y
            except Exception as e:
                print(f"轉換失敗: 經度={lon}, 緯度={lat}, 錯誤={e}")
                return np.nan, np.nan
        
        # 批量轉換
        print("正在轉換座標...")
        coords = df.apply(lambda row: transform_coords(row['經度'], row['緯度']), axis=1)
        
        # 根據目標座標系統設定欄位名稱
        if target_epsg == "EPSG:3826":
            df['TWD97_lon'] = [coord[0] for coord in coords]
            df['TWD97_lat'] = [coord[1] for coord in coords]
            print("已轉換為TWD97公尺座標")
        elif target_epsg == "EPSG:4326":
            df['WGS84_lon'] = [coord[0] for coord in coords]
            df['WGS84_lat'] = [coord[1] for coord in coords]
            print("已轉換為WGS84經緯度座標")
        
        # 移除轉換失敗的記錄
        if target_epsg == "EPSG:3826":
            valid_mask = ~df['TWD97_lon'].isna() & ~df['TWD97_lat'].isna()
        elif target_epsg == "EPSG:4326":
            valid_mask = ~df['WGS84_lon'].isna() & ~df['WGS84_lat'].isna()
        else:
            valid_mask = pd.Series([True] * len(df))
        
        df_valid = df[valid_mask].copy()
        
        print(f"座標轉換完成：{len(df_valid)} 筆成功，{len(df) - len(df_valid)} 筆失敗")
        print(f"已將{source_crs}座標轉換為{target_crs}")
        
        return df_valid
        
    except Exception as e:
        print(f"座標轉換失敗: {e}")
        print("無法建立轉換器，請檢查座標系統設定")
        return df

def detect_and_remove_anomalies(df):
    """
    偵測並移除異常點位 - 使用鄉鎮市區界線shapefile進行空間查詢
    
    Args:
        df (pd.DataFrame): 包含座標的資料框
    
    Returns:
        tuple: (清理後的資料框, 被刪除的異常資料)
    """
    anomalies = []
    
    # 檢查 (0, 0) 座標
    zero_mask = (df['經度'] == 0) | (df['緯度'] == 0)
    zero_anomalies = df[zero_mask].copy()
    anomalies.append(zero_anomalies)
    
    # 使用shapefile進行空間查詢
    print("載入鄉鎮市區界線shapefile...")
    try:
        # 載入shapefile
        shapefile_path = "data/鄉鎮市區界線(TWD97經緯度)/TOWN_MOI_1120317.shp"
        town_boundaries = gpd.read_file(shapefile_path)
        
        # 確保shapefile座標系統為EPSG:3826 (TWD97)
        if town_boundaries.crs != 'EPSG:3826':
            town_boundaries = town_boundaries.to_crs('EPSG:3826')
        
        print(f"已載入 {len(town_boundaries)} 個鄉鎮市區界線")
        
        # 創建點位幾何物件 (使用EPSG3826座標)
        geometry = [Point(xy) for xy in zip(df['TWD97_lon'], df['TWD97_lat'])]
        points_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:3826')
        
        # 空間查查詢：檢查點位是否在鄉鎮市區界線內
        points_within_bounds = gpd.sjoin(points_gdf, town_boundaries, how='inner', predicate='within')
        
        # 找出在邊界外的點位
        points_outside = points_gdf[~points_gdf.index.isin(points_within_bounds.index)]
        outside_anomalies = points_outside.drop(columns=['geometry']).copy()
        anomalies.append(outside_anomalies)
        
        print(f"空間查詢完成：{len(points_within_bounds)} 個點位在邊界內，{len(points_outside)} 個點位在邊界外")
        
    except Exception as e:
        print(f"無法載入shapefile或進行空間查詢: {e}")
        print("改用傳統的邊界範圍檢查...")
        
        # 備用方案：使用傳統的邊界範圍檢查
        # 台灣邊界大約：經度 119-123，緯度 21-26
        outside_mask = ((df['經度'] < 119) | (df['經度'] > 123) | 
                       (df['緯度'] < 21) | (df['緯度'] > 26)) & ~zero_mask
        outside_anomalies = df[outside_mask].copy()
        anomalies.append(outside_anomalies)
    
    # 合併所有異常資料
    if anomalies:
        deleted_data = pd.concat(anomalies, ignore_index=True)
    else:
        deleted_data = pd.DataFrame()
    
    # 移除異常資料
    if 'points_within_bounds' in locals():
        # 使用空間查詢結果
        clean_data = points_within_bounds.drop(columns=['geometry', 'index_right']).copy()
    else:
        # 使用傳統方法結果
        clean_data = df[~zero_mask & ~outside_mask].copy()
    
    print(f"偵測到 {len(deleted_data)} 筆異常資料")
    print(f"- (0,0) 座標: {len(zero_anomalies)} 筆")
    print(f"- 邊界外座標: {len(outside_anomalies)} 筆")
    print(f"清理後剩餘 {len(clean_data)} 筆資料")
    
    return clean_data, deleted_data

def save_deleted_shelters(deleted_data, output_path):
    """
    保存被刪除的避難收容處所資料，移除shapefile相關欄位
    
    Args:
        deleted_data (pd.DataFrame): 被刪除的資料
        output_path (str): 輸出檔案路徑
    """
    # 移除shapefile相關欄位
    shapefile_columns = ['TOWNID', 'TOWNCODE', 'COUNTYNAME', 'TOWNNAME', 'TOWNENG', 'COUNTYID', 'COUNTYCODE']
    
    # 只移除存在的欄位
    columns_to_remove = [col for col in shapefile_columns if col in deleted_data.columns]
    
    if columns_to_remove:
        deleted_data_filtered = deleted_data.drop(columns=columns_to_remove)
        print(f"已移除shapefile欄位: {', '.join(columns_to_remove)}")
    else:
        deleted_data_filtered = deleted_data
    
    if not deleted_data_filtered.empty:
        deleted_data_filtered.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"已保存 {len(deleted_data_filtered)} 筆刪除資料到 {output_path}")
    else:
        print("沒有異常資料需要保存")

def classify_shelter_type(df):
    """
    根據避難收容處所名稱判斷室內外類型
    
    Args:
        df (pd.DataFrame): 包含避難收容處所資料的資料框
    
    Returns:
        pd.DataFrame: 加入is_indoor欄位的資料框
    """
    # 室外類型關鍵字
    outdoor_keywords = ['公園', '廣場', '操場', '體育場', '運動場', '球場', '停車場']
    
    # 室內類型關鍵字
    indoor_keywords = ['學校', '活動中心', '禮堂', '辦公處', '教會', '廟', '教室', '會堂', '中心', '大樓', '大廈', '圖書館', '社區中心', 
                      '廳舍', '民宿', '體育館', '地下室', '老人館', '管理中心', '育樂中心', '管理室']
    
    def classify_shelter(shelter_name):
        """
        根據避難收容處所名稱分類室內外
        
        Args:
            shelter_name (str): 避難收容處所名稱
        
        Returns:
            bool: True為室內，False為室外
        """
        if pd.isna(shelter_name) or shelter_name == '':
            return False  # 空值預設為室外
        
        shelter_name = str(shelter_name).strip()
        
        # 優先檢查直接關鍵字
        if '戶外' in shelter_name or '室外' in shelter_name:
            return False  # 直接設定為室外
        if '室內' in shelter_name:
            return True   # 直接設定為室內
        
        # 初始化標記
        has_outdoor_keyword = False
        has_indoor_keyword = False
        
        # 檢查所有室外關鍵字
        for keyword in outdoor_keywords:
            if keyword in shelter_name:
                has_outdoor_keyword = True
        
        # 檢查所有室內關鍵字
        for keyword in indoor_keywords:
            if keyword in shelter_name:
                has_indoor_keyword = True
        
        # 判斷邏輯：
        # - 如果同時包含室內和室外關鍵字，設定為True（室內）
        # - 如果只包含室內關鍵字，設定為True（室內）
        # - 如果只包含室外關鍵字，設定為False（室外）
        # - 如果都沒有，預設為True（室內）
        if has_indoor_keyword and has_outdoor_keyword:
            return True  # 同時包含時，優先考慮室內
        elif has_indoor_keyword:
            return True  # 只有室內關鍵字
        elif has_outdoor_keyword:
            return False  # 只有室外關鍵字
        else:
            return True  # 都沒有時，預設為室內
    
    # 套用分類函數
    df['is_indoor'] = df['避難收容處所名稱'].apply(classify_shelter)
    
    # 統計結果
    indoor_count = df['is_indoor'].sum()
    outdoor_count = len(df) - indoor_count
    
    print(f"避難處所分類完成：")
    print(f"- 室內避難處所: {indoor_count} 筆")
    print(f"- 室外避難處所: {outdoor_count} 筆")
    
    # 顯示一些範例
    print("\n室內避難處所範例：")
    indoor_examples = df[df['is_indoor'] == True]['避難收容處所名稱'].head(3).tolist()
    for example in indoor_examples:
        print(f"  - {example}")
    
    print("\n室外避難處所範例：")
    outdoor_examples = df[df['is_indoor'] == False]['避難收容處所名稱'].head(3).tolist()
    for example in outdoor_examples:
        print(f"  - {example}")
    
    return df

def save_cleaned_data(clean_data, output_path):
    """
    保存清理後的資料，移除shapefile相關欄位
    
    Args:
        clean_data (pd.DataFrame): 清理後的資料
        output_path (str): 輸出檔案路徑
    """
    # 移除shapefile相關欄位
    shapefile_columns = ['TOWNID', 'TOWNCODE', 'COUNTYNAME', 'TOWNNAME', 'TOWNENG', 'COUNTYID', 'COUNTYCODE']
    
    # 只移除存在的欄位
    columns_to_remove = [col for col in shapefile_columns if col in clean_data.columns]
    
    if columns_to_remove:
        clean_data_filtered = clean_data.drop(columns=columns_to_remove)
        print(f"已移除shapefile欄位: {', '.join(columns_to_remove)}")
    else:
        clean_data_filtered = clean_data
    
    clean_data_filtered.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"已保存 {len(clean_data_filtered)} 筆清理後資料到 {output_path}")

def coordinate_check_main():
    """
    主函數：處理避難收容處所座標資料
    """
    print("台灣避難收容處所座標檢查與清理程式")
    print("="*60)
    
    # 步驟1: 載入.env設定並讀取目標座標系統
    print("\n步驟1: 載入環境設定")
    target_crs = load_env_config()
    print(f"目標座標系統: {target_crs}")
    
    # 步驟2: 載入避難收容處所資料
    print("\n步驟2: 載入避難收容處所資料")
    csv_file_path = "data/避難收容處所點位檔案v9.csv"
    
    try:
        df = pd.read_csv(csv_file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
    
    print(f"檔案載入成功，共 {len(df)} 筆資料")
    
    # 移除缺失值
    df_clean = df.dropna(subset=['經度', '緯度'])
    df_clean['經度'] = pd.to_numeric(df_clean['經度'], errors='coerce')
    df_clean['緯度'] = pd.to_numeric(df_clean['緯度'], errors='coerce')
    df_clean = df_clean.dropna(subset=['經度', '緯度'])
    
    print(f"清理缺失值後，剩餘 {len(df_clean)} 筆有效資料")
    
    # 步驟3: 檢測目前座標系統
    print("\n步驟3: 檢測目前座標系統")
    source_crs = detect_coordinate_system(df_clean['經度'], df_clean['緯度'])
    print(f"偵測到座標系統: {source_crs}")
    
    # 步驟4: 檢查是否需要轉換座標系統
    print(f"\n步驟4: 檢查座標系統轉換需求")
    print(f"來源座標系統: {source_crs}")
    print(f"目標座標系統: {target_crs}")
    
    # 格式化座標系統進行比較
    def format_epsg_for_compare(crs_string):
        """格式化座標系統用於比較"""
        if isinstance(crs_string, str):
            crs_clean = crs_string.strip()
            if crs_clean.upper().startswith('EPSG') and ':' not in crs_clean:
                if crs_clean.upper() == 'EPSG4326':
                    return 'EPSG:4326'
                elif crs_clean.upper() == 'EPSG3826':
                    return 'EPSG:3826'
                elif crs_clean.upper() == 'EPSG3824':
                    return 'EPSG:3824'
        return crs_clean
    
    source_formatted = format_epsg_for_compare(source_crs)
    target_formatted = format_epsg_for_compare(target_crs)
    
    if source_formatted == target_formatted:
        print("✅ 座標系統已符合目標，無需轉換")
        print("為後續空間查詢準備必要的座標欄位")
        
        # 無論目標座標系統是什麼，都需要TWD97欄位供後續空間查詢使用
        if 'TWD97_lon' not in df_clean.columns or 'TWD97_lat' not in df_clean.columns:
            print("為後續空間查詢準備TWD97座標欄位")
            if target_formatted == "EPSG:3826":
                # 如果已經是TWD97，直接複製
                df_clean['TWD97_lon'] = df_clean['經度']
                df_clean['TWD97_lat'] = df_clean['緯度']
            elif target_formatted == "EPSG:4326":
                # 如果是WGS84，需要轉換為TWD97供空間查詢
                print("轉換WGS84座標為TWD97供空間查詢使用")
                transformer = Transformer.from_crs("EPSG:4326", "EPSG:3826", always_xy=True)
                
                def transform_coords(lon, lat):
                    try:
                        x, y = transformer.transform(lon, lat)
                        return x, y
                    except:
                        return np.nan, np.nan
                
                coords = df_clean.apply(lambda row: transform_coords(row['經度'], row['緯度']), axis=1)
                df_clean['TWD97_lon'] = [coord[0] for coord in coords]
                df_clean['TWD97_lat'] = [coord[1] for coord in coords]
                
                # 移除轉換失敗的記錄
                valid_mask = ~df_clean['TWD97_lon'].isna() & ~df_clean['TWD97_lat'].isna()
                df_clean = df_clean[valid_mask].copy()
                print(f"TWD97轉換完成，剩餘 {len(df_clean)} 筆有效資料")
        else:
            print("TWD97座標欄位已存在")
        
        df_converted = df_clean.copy()
    else:
        print(f"⚠️  需要轉換座標系統: {source_formatted} -> {target_formatted}")
        df_converted = convert_to_target_crs(df_clean.copy(), source_crs, target_crs)
    
    # 步驟5: 偵測並刪除異常點位
    print("\n步驟5: 偵測並刪除異常點位")
    clean_data, deleted_data = detect_and_remove_anomalies(df_converted)
    
    # 保存刪除的資料
    deleted_output_path = "outputs/deleted_shelter.csv"
    save_deleted_shelters(deleted_data, deleted_output_path)
    
    # 步驟6: 判斷避難處所室內外類型
    print("\n步驟6: 判斷避難處所室內外類型")
    clean_data_with_type = classify_shelter_type(clean_data)
    
    # 步驟7: 保存清理後的資料
    print("\n步驟7: 保存清理後的資料")
    cleaned_output_path = "data/shelters_cleaned.csv"
    save_cleaned_data(clean_data_with_type, cleaned_output_path)
    
    print("\n" + "="*60)
    print("處理完成！")
    print("="*60)
    print(f"原始資料: {len(df)} 筆")
    print(f"有效資料: {len(df_clean)} 筆")
    print(f"座標轉換成功: {len(df_converted)} 筆")
    print(f"刪除異常: {len(deleted_data)} 筆")
    print(f"最終資料: {len(clean_data_with_type)} 筆")
    print(f"清理後資料已保存至: {cleaned_output_path}")
    print(f"刪除資料清單已保存至: {deleted_output_path}")
    print(f"\n座標轉換說明:")
    print(f"- 來源座標系統: {source_crs}")
    print(f"- 目標座標系統: {target_crs}")
    print(f"- 轉換工具: pyproj Transformer")

# ============================================================================
# AQI地圖與分析功能 (來自 aqi_map.py)
# ============================================================================

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
        
        # 初始化 pyproj Transformer: TWD97(度) EPSG:3824 -> TWD97(公尺) EPSG:3826
        self.twd97_degree_to_meter_transformer = Transformer.from_crs(
            "EPSG:3824",  # TWD97(度)
            "EPSG:3826",  # TWD97(公尺)
            always_xy=True
        )
        
        # 初始化 pyproj Transformer: TWD97(度) EPSG:3824 -> WGS84 EPSG:4326
        self.twd97_degree_to_wgs84_transformer = Transformer.from_crs(
            "EPSG:3824",  # TWD97(度)
            "EPSG:4326",  # WGS84
            always_xy=True
        )
    
    def twd97_degree_to_meter(self, lon_degree, lat_degree):
        """使用pyproj將TWD97(度)轉換為TWD97(公尺)"""
        x_meter, y_meter = self.twd97_degree_to_meter_transformer.transform(
            lon_degree, lat_degree
        )
        return x_meter, y_meter
    
    def twd97_degree_to_wgs84(self, lon_degree, lat_degree):
        """使用pyproj將TWD97(度) EPSG:3824轉換為WGS84 EPSG:4326"""
        wgs84_lon, wgs84_lat = self.twd97_degree_to_wgs84_transformer.transform(
            lon_degree, lat_degree
        )
        return wgs84_lon, wgs84_lat
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """使用Haversine公式計算兩點間的距離（公里）"""
        R = 6371  # 地球半徑（公里）
        
        # 將角度轉為弧度
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # 計算差值
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine公式
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
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
        """使用 TWD97(度) 轉換為 TWD97(公尺) 後計算距離（公里）"""
        # 將 TWD97(度) 轉換為 TWD97(公尺)
        x1, y1 = self.twd97_degree_to_meter(lon1, lat1)
        x2, y2 = self.twd97_degree_to_meter(lon2, lat2)
        
        # 使用 TWD97 平面座標計算歐幾里得距離
        dx = x2 - x1
        dy = y2 - y1
        distance_meters = math.sqrt(dx**2 + dy**2)
        
        # 轉換為公里
        distance_km = distance_meters / 1000
        
        return round(distance_km, 2)
    
    def calculate_distances_to_taipei_station(self, aqi_data):
        """計算每個測站到台北車站的距離 (使用 TWD97(公尺) 座標系)"""
        results = []
        
        taipei_lat = self.taipei_station['latitude']
        taipei_lon = self.taipei_station['longitude']
        
        print(f"台北車站座標 (TWD97度): {taipei_lat}, {taipei_lon}")
        print(f"台北車站座標 (TWD97公尺): X={self.taipei_twd97[0]:.2f}, Y={self.taipei_twd97[1]:.2f}")
        print(f"處理測站座標系統: TWD97(度) EPSG:3824 -> TWD97(公尺) EPSG:3826")
        
        for station in aqi_data:
            try:
                # 獲取測站資訊
                site_name = station.get('sitename', '未知測站')
                county = station.get('county', station.get('sitename', '未知'))
                lat = float(station.get('latitude', 0))  # 這是TWD97(度)
                lon = float(station.get('longitude', 0))  # 這是TWD97(度)
                aqi = station.get('aqi', 'N/A')
                pollutant = station.get('pollutant', 'N/A')
                status = station.get('status', 'N/A')
                
                if lat == 0 or lon == 0:
                    continue
                
                # 使用 TWD97(度) 計算距離
                distance = self.calculate_distance(lat, lon, taipei_lat, taipei_lon)
                
                # 轉換測站座標為 TWD97(公尺)
                station_twd97_x, station_twd97_y = self.twd97_degree_to_meter(lon, lat)
                
                # 轉換TWD97(度)為WGS84 (用於後續避難所距離計算)
                wgs84_lon, wgs84_lat = self.twd97_degree_to_wgs84(lon, lat)
                
                result = {
                    '測站名稱': site_name,
                    '所在縣市': county,
                    'TWD97_lat_度': lat,  # 修正欄位名稱
                    'TWD97_lon_度': lon,  # 修正欄位名稱
                    'WGS84_lat': wgs84_lat,  # 新增真正的WGS84座標
                    'WGS84_lon': wgs84_lon,  # 新增真正的WGS84座標
                    'TWD97_lat_公尺': station_twd97_y,  # 修正欄位名稱
                    'TWD97_lon_公尺': station_twd97_x,  # 修正欄位名稱
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
        
        # 修改斗六測站的AQI值為150
        for data in distance_data:
            if '斗六' in data.get('測站名稱', ''):
                data['AQI'] = 150
                print(f"已將斗六測站的AQI值修改為150")
        
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
    
    def create_map(self, aqi_data=None):
        """建立包含AQI測站和避難收容處所的雙圖層地圖"""
        # 建立以台灣為中心的地圖
        taiwan_center = [23.8, 121.0]
        m = folium.Map(location=taiwan_center, zoom_start=8)
        
        # 添加標題
        title_html = '''
        <h3 align="center" style="font-size:30px"><b>台灣環境與社會資料交集地圖</b></h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # 圖層A: AQI測站
        aqi_layer = folium.FeatureGroup(name='圖層 A: AQI 測站')
        
        # 從aqi_station_distances_twd97.csv讀取座標
        try:
            aqi_df = pd.read_csv('outputs/aqi_station_distances_twd97.csv', encoding='utf-8-sig')
            print(f"地圖載入 {len(aqi_df)} 筆AQI測站資料")
            
            for _, row in aqi_df.iterrows():
                try:
                    # 使用WGS84座標顯示地圖
                    lat_wgs84 = row['WGS84_lat']
                    lon_wgs84 = row['WGS84_lon']
                    
                    site_name = row['測站名稱']
                    county = row['所在縣市']
                    aqi = row['AQI']
                    pollutant = row['主要污染物']
                    status = row['空氣品質狀態']
                    distance = row['距離台北車站_TWD97(公里)']
                    
                    # 獲取顏色
                    color = self.get_aqi_color(aqi)
                    
                    # 建立彈出視窗內容
                    popup_content = f"""
                    <b>{site_name}</b><br>
                    位置: {county}<br>
                    AQI: <span style="color:black; font-weight:bold">{aqi}</span><br>
                    主要污染物: {pollutant}<br>
                    空氣品質: {status}<br>
                    距離台北車站: {distance} 公里<br>
                    WGS84座標: ({lat_wgs84:.4f}, {lon_wgs84:.4f})<br>
                    TWD97座標(度): ({row['TWD97_lat_度']:.4f}, {row['TWD97_lon_度']:.4f})<br>
                    TWD97座標(公尺): ({row['TWD97_lon_公尺']:.2f}, {row['TWD97_lat_公尺']:.2f})
                    """
                    
                    # 添加標記
                    folium.CircleMarker(
                        location=[lat_wgs84, lon_wgs84],
                        radius=8,
                        popup=popup_content,
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.7,
                        weight=2,
                        tooltip=f"{site_name} - AQI: {aqi}"
                    ).add_to(aqi_layer)
                    
                except Exception as e:
                    print(f"處理AQI測站 {row.get('測站名稱', '未知')} 時發生錯誤: {e}")
                    continue
                    
        except Exception as e:
            print(f"讀取AQI測站資料時發生錯誤: {e}")
        
        aqi_layer.add_to(m)
        
        # 圖層B: 避難收容處所
        shelter_layer = folium.FeatureGroup(name='圖層 B: 避難收容處所')
        
        # 從shelters_cleaned.csv讀取避難收容處所資料
        try:
            shelter_df = pd.read_csv('data/shelters_cleaned.csv', encoding='utf-8-sig')
            
            for _, row in shelter_df.iterrows():
                try:
                    # 直接使用原始WGS84座標
                    lat_wgs84 = row['緯度']
                    lon_wgs84 = row['經度']
                    
                    shelter_name = row['避難收容處所名稱']
                    address = row['避難收容處所地址']
                    county = row['縣市及鄉鎮市區']
                    is_indoor = row['is_indoor']
                    
                    # 根據室內外設定圖標顏色
                    if is_indoor:
                        icon_color = 'purple'  # 室內：紫色
                        type_text = '室內'
                    else:
                        icon_color = 'darkblue'  # 室外：深藍色
                        type_text = '室外'
                    
                    # 建立彈出視窗內容
                    popup_content = f"""
                    <b>{shelter_name}</b><br>
                    位置: {county}<br>
                    地址: {address}<br>
                    類型: <span style="color:{icon_color}; font-weight:bold">{type_text}</span><br>
                    WGS84座標: ({lat_wgs84:.4f}, {lon_wgs84:.4f})<br>
                    TWD97座標: ({row['TWD97_lon']:.2f}, {row['TWD97_lat']:.2f})
                    """
                    
                    # 添加標記
                    # 使用自定義圖標移除背景和陰影
                    icon_html = f'''
                    <div style="
                        background-color: transparent;
                        border: none;
                        box-shadow: none;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        width: 20px;
                        height: 20px;
                    ">
                        <i class="fa fa-home" style="
                            color: {icon_color};
                            font-size: 16px;
                            text-shadow: none;
                        "></i>
                    </div>
                    '''
                    
                    custom_icon = folium.DivIcon(
                        html=icon_html,
                        icon_size=(20, 20),
                        icon_anchor=(10, 10),
                        popup_anchor=(0, -10)
                    )
                    
                    folium.Marker(
                        location=[lat_wgs84, lon_wgs84],
                        popup=popup_content,
                        icon=custom_icon,
                        tooltip=f"{shelter_name}"
                    ).add_to(shelter_layer)
                    
                except Exception as e:
                    print(f"處理避難收容處所 {row.get('避難收容處所名稱', '未知')} 時發生錯誤: {e}")
                    continue
                    
        except Exception as e:
            print(f"讀取避難收容處所資料時發生錯誤: {e}")
        
        shelter_layer.add_to(m)
        
        # 添加圖例
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 280px; height: 240px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.2)">
        <h4 style="margin-top: 0; margin-bottom: 10px;">圖例</h4>
        <p style="margin: 5px 0;"><b>圖層 A: AQI 測站</b></p>
        <p style="margin: 3px 0;"><span style="color:green; font-weight:bold">●</span> 良好 (0-50)</p>
        <p style="margin: 3px 0;"><span style="color:orange; font-weight:bold">●</span> 普通 (51-100)</p>
        <p style="margin: 3px 0;"><span style="color:red; font-weight:bold">●</span> 不健康 (101+)</p>
        <p style="margin: 10px 0 5px 0;"><b>圖層 B: 避難收容處所</b></p>
        <p style="margin: 3px 0;"><i class="fa fa-home" style="color:purple;"></i> 室內避難處所</p>
        <p style="margin: 3px 0;"><i class="fa fa-home" style="color:darkblue;"></i> 室外避難處所</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 添加圖層控制
        folium.LayerControl().add_to(m)
        
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
    
    def analyze_shelter_aqi(self):
        """分析避難所與最近測站的AQI關係"""
        print("開始分析避難所與AQI測站的關係...")
        print("避難所距離計算: Haversine公式 (測站WGS84 vs 避難所WGS84)")
        
        # 讀取避難收容處所資料
        try:
            shelters_df = pd.read_csv('data/shelters_cleaned.csv', encoding='utf-8-sig')
            print(f"讀取 {len(shelters_df)} 筆避難收容處所資料")
        except Exception as e:
            print(f"讀取避難收容處所資料時發生錯誤: {e}")
            return
        
        # 讀取AQI測站資料
        try:
            aqi_df = pd.read_csv('outputs/aqi_station_distances_twd97.csv', encoding='utf-8-sig')
            print(f"讀取 {len(aqi_df)} 筆AQI測站資料")
        except Exception as e:
            print(f"讀取AQI測站資料時發生錯誤: {e}")
            return
        
        # 為每個避難所找到最近的測站
        results = []
        
        for _, shelter in shelters_df.iterrows():
            shelter_lat = shelter['緯度']  # WGS84
            shelter_lon = shelter['經度']  # WGS84
            
            min_distance = float('inf')
            nearest_station = None
            
            # 計算到每個測站的距離
            for _, station in aqi_df.iterrows():
                # 使用測站的WGS84座標
                station_lat = station['WGS84_lat']  # WGS84
                station_lon = station['WGS84_lon']  # WGS84
                
                # 使用Haversine公式計算距離 (WGS84球面距離)
                distance = self.haversine_distance(
                    shelter_lat, shelter_lon, station_lat, station_lon
                )
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_station = station
            
            # 建立結果記錄
            if nearest_station is not None:
                result = shelter.to_dict()
                
                # 添加測站資訊
                result['測站名稱'] = nearest_station['測站名稱']
                result['所在縣市'] = nearest_station['所在縣市']
                result['測站緯度(WGS84)'] = nearest_station['WGS84_lat']
                result['測站經度(WGS84)'] = nearest_station['WGS84_lon']
                result['測站TWD97_lat_度'] = nearest_station['TWD97_lat_度']
                result['測站TWD97_lon_度'] = nearest_station['TWD97_lon_度']
                result['測站TWD97_lat_公尺'] = nearest_station['TWD97_lat_公尺']
                result['測站TWD97_lon_公尺'] = nearest_station['TWD97_lon_公尺']
                result['AQI'] = nearest_station['AQI']
                result['主要污染物'] = nearest_station['主要污染物']
                result['空氣品質狀態'] = nearest_station['空氣品質狀態']
                result['避難所到最近測站的距離(公里)'] = round(min_distance, 4)
                
                # 計算Risk Labeling
                aqi_value = nearest_station['AQI']
                is_indoor = shelter['is_indoor']
                
                if aqi_value > 100:
                    result['Risk Labeling'] = 'High Risk'
                elif aqi_value > 50 and not is_indoor:
                    result['Risk Labeling'] = 'Warning'
                else:
                    result['Risk Labeling'] = ''
                
                results.append(result)
        
        # 儲存結果
        if results:
            output_file = 'outputs/shelter_aqi_analysis.csv'
            result_df = pd.DataFrame(results)
            result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            
            print(f"分析完成！結果已儲存至: {output_file}")
            print(f"共分析 {len(results)} 筆避難收容處所資料")
        else:
            print("沒有分析結果")

def aqi_map_main():
    """主程式：AQI地圖生成與分析"""
    if not API_KEY:
        print("錯誤: 請在 .env 檔案中設定 MOENV_API_KEY")
        return
    
    # 檢查必要的CSV檔案是否存在
    aqi_csv_path = 'outputs/aqi_station_distances_twd97.csv'
    shelter_csv_path = 'data/shelters_cleaned.csv'
    
    if not os.path.exists(aqi_csv_path):
        print(f"錯誤: 找不到AQI測站資料檔案")
        print(f"請先執行座標檢查功能來生成: {aqi_csv_path}")
        return
        
    if not os.path.exists(shelter_csv_path):
        print(f"錯誤: 找不到避難收容處所資料檔案")
        print(f"請先執行座標檢查功能來生成: {shelter_csv_path}")
        return
    
    # 建立 AQI 地圖生成器
    generator = AQIMapGenerator(API_KEY)
    
    print(f"讀取現有AQI測站資料: {aqi_csv_path}")
    
    # 建立地圖（直接使用CSV資料，不需要重新獲取API）
    print("\n建立 台灣環境與社會資料交集地圖...")
    aqi_map = generator.create_map(aqi_data=None)
    
    # 儲存地圖
    output_file = generator.save_map(aqi_map)
    
    if output_file:
        print(f"地圖生成完成：{output_file}")
        
        # 執行避難所AQI分析
        print("\n生成避難所距離最近監測站空氣品質報告...")
        generator.analyze_shelter_aqi()
        
        print("\n地圖建立與分析完成！")
        print("提示: 請開啟 outputs/aqi_map.html 查看互動式地圖")
        print("提示: 請查看 outputs/shelter_aqi_analysis.csv 查看分析報告")
    else:
        print("地圖儲存失敗")

# ============================================================================
# 主程式入口
# ============================================================================

def main():
    """
    主程式：提供功能選單
    """
    print("台灣避難收容處所AQI分析系統")
    print("="*60)
    print("請選擇要執行的功能：")
    print("1. 避難收容處所座標檢查與清理")
    print("2. AQI地圖生成與分析")
    print("3. 離開程式")
    print("="*60)
    
    while True:
        try:
            choice = input("\n請輸入選項 (1-3): ").strip()
            
            if choice == '1':
                coordinate_check_main()
                break
            elif choice == '2':
                aqi_map_main()
                break
            elif choice == '3':
                print("\n感謝使用台灣避難收容處所AQI分析系統！")
                break
            else:
                print("無效選擇，請輸入 1-3 的數字")
                
        except KeyboardInterrupt:
            print("\n\n程式中斷，感謝使用！")
            break
        except Exception as e:
            print(f"發生錯誤: {e}")

if __name__ == "__main__":
    main()
