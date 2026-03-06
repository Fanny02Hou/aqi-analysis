# 台灣 AQI 即時地圖分析系統

這個專案整合了環境部空氣品質監測數據與避難收容處所資料，提供完整的環境與社會資料交集分析，包含互動式地圖視覺化、風險評估報告等功能。

## 🎯 專案特色

- 🌍 **即時AQI監測**: 串接環境部 `data.moenv.gov.tw/api/v2/aqx_p_432` API 獲取全台即時空氣品質指標
- 📍 **雙圖層地圖**: 使用 Folium 建立互動式地圖，同時顯示AQI測站與避難收容處所位置
- 🎨 **智能視覺化**: 依AQI值自動分級顏色顯示，避難所依室內外使用不同圖標
- 📏 **高精度距離**: 使用 `geo_coor` 套件進行 WGS84 到 TWD97 座標轉換與距離計算
- 🏢 **避難所分析**: 自動偵測異常點位、分類室內外類型、計算到最近測站距離
- ⚡ **風險評估**: 基於AQI值與避難所類型進行風險標籤分類
- 🔧 **整合設計**: 所有功能整合在單一檔案 `shelter_aqi_analysis.py` 中

## 🏗️ 專案架構

```
aqi_analysis/
├── main.py                           # 主程式入口，統一管理所有功能
├── .env                             # 環境變數設定檔案 ⚠️ 重要設定
├── requirements.txt                 # Python 套件依賴清單
├── .gitignore                       # Git 版本控制忽略檔案
├── scripts/                         # 核心程式模組目錄
│   └── shelter_aqi_analysis.py     # 🌟 主要功能檔案 (整合所有功能)
│   ├── setup.py                    # 環境設定與套件安裝工具
│   └── test_api.py                 # API連線測試工具
├── data/                           # 原始資料目錄
│   ├── 避難收容處所點位檔案v9.csv
│   └── shelters_cleaned.csv       # 清理後避難收容處所資料
├── data/鄉鎮市區界線(TWD97經緯度)/   # 台灣行政區界線Shapefile
└── outputs/                        # 輸出檔案目錄
    ├── aqi_map.html                # 互動式雙圖層地圖
    ├── aqi_station_distances_twd97.csv  # AQI測站距離數據
    ├── deleted_shelter.csv        # 異常避難所資料
    ├── shelter_aqi_analysis.csv   # 避難所風險分析報告
    ├── audit_report.md            # 空間審計報告
    └── reflection.md             # 開發反思報告
```

## ⚙️ 重要設定提醒

### � .env 檔案設定

請在專案根目錄的 `.env` 檔案中設定以下環境變數：

```bash
# 環境部 API 金鑰 (必須)
MOENV_API_KEY=your_actual_api_key_here

# ⚠️ 重要：座標系統設定 (必須設定為 EPSG4326)
target_crs=EPSG4326
```

#### 📍 座標系統說明
- **EPSG4326**: WGS84 經緯度座標系統 (Google Maps、GPS 使用)
- **EPSG3824**: TWD97 度座標系統 (環境部測站API使用，以度表示)
- **EPSG3826**: TWD97 公尺座標系統 (台灣政府機構常用)
- **本專案**: 統一使用 **EPSG4326** 進行處理，確保座標一致性
- **環境部API**: 測站座標採用 **EPSG3824** (TWD97度)，程式會自動轉換

## �� 快速開始

### Step 0: 系統說明
```bash
python main.py
# 選擇選項 0: 系統說明
```

### Step 1: 環境設定安裝
```bash
python main.py
# 選擇選項 1: 環境設定安裝
```

### Step 2: 測試 API 連線
```bash
# 選擇選項 2: 測試 API 連線
```
- 測試環境部 API 連線狀況
- 驗證 API 金鑰有效性
- 確認數據獲取正常

### Step 3: AQI資料處理
```bash
# 選擇選項 3: 抓取環境部API資料處理
```
- 獲取全台 AQI 測站即時資料
- 使用 geo_coor 套件計算 TWD97 距離
- 自動修改斗六測站 AQI 值為 150
- 輸出: `outputs/aqi_station_distances_twd97.csv`

### Step 4: 避難收容處所檢查
```bash
# 選擇選項 4: 避難收容處所檢查
```
- 載入避難收容處所點位檔案
- 偵測座標系統 (EPSG:4326/EPSG:3826)
- 移除異常點位 (座標異常、台灣邊界外)
- 使用 Shapefile 進行空間查詢
- 關鍵字分類室內外避難所
- 輸出: `data/shelters_cleaned.csv`
- 輸出: `outputs/deleted_shelter.csv`

### Step 5: 地圖建立與分析
```bash
# 選擇選項 5: 地圖建立與分析
```
- 直接讀取現有 CSV 檔案 (避免重複計算)
- 建立 Folium 雙圖層互動式地圖
  - **圖層 A**: AQI 測站 (依 AQI 值顏色分級)
  - **圖層 B**: 避難收容處所 (室內紫色/室外深藍色)
- 地圖圖例說明：
  - **AQI測站**: 🟢綠色(0-50) 🟡橙色(51-100) 🔴紅色(101+)
  - **室內避難所**: 🏠 紫色房屋圖標
  - **室外避難所**: 🏠 深藍色房屋圖標
- 使用 Haversine 公式計算避難所到最近測站距離
- 風險標籤分類:
  - **High Risk**: AQI > 100
  - **Warning**: AQI > 50 AND is_indoor == False
- 輸出: `outputs/aqi_map.html`
- 輸出: `outputs/shelter_aqi_analysis.csv`

### Step 6: 離開程式
```bash
# 選擇選項 6: 離開程式
```

## 📊 輸出檔案說明

| 檔案名稱 | 描述 | 格式 | 用途 |
|-----------|------|------|------|
| 📄 aqi_map.html | 互動式地圖 | HTML | 網頁地圖視覺化 |
| 📊 aqi_station_distances_twd97.csv | AQI測站資料 | CSV | 測站位置與距離數據 |
| 🏢 shelters_cleaned.csv | 清理後避難所 | CSV | 正常避難所資料 (data目錄) |
| 🗑️ deleted_shelter.csv | 異常避難所 | CSV | 異常點位記錄 |
| 📋 shelter_aqi_analysis.csv | 風險分析報告 | CSV | 避難所風險評估 |
| 🔍 audit_report.md | 空間審計報告 | MD | AI座標品質檢查與分析 |
| 💡 reflection.md | 開發反思報告 | MD | 專案學習與改進方向 |

## 🌐 API 規格

### 主要端點
```
https://data.moenv.gov.tw/api/v2/aqx_p_432
```

### 回傳格式
- ✅ **JSON 格式**
- ✅ **UTF-8 編碼**
- ✅ **84+ 測站數據**
- ✅ **即時更新**

### 數據欄位
```json
{
  "sitename": "測站名稱",
  "county": "所在縣市", 
  "aqi": "AQI數值",
  "pollutant": "主要污染物",
  "status": "空氣品質狀態",
  "latitude": "緯度(WGS84)",
  "longitude": "經度(WGS84)"
}
```

## 🎨 AQI 顏色對應

| AQI 範圍 | 狀態 | 地圖標記顏色 |
|-----------|------|-------------|
| 0-50 | 良好 | 🟢 綠色 |
| 51-100 | 普通 | 🟡 橙色 |
| 101+ | 不健康 | 🔴 紅色 |

## 🏢 避難所分類邏輯

### 室內外判斷
- **室內關鍵字**: 學校、體育館、活動中心、禮堂、寺廟、教堂、管理室、廳舍、民宿、大樓、地下室、老人館、管理中心
- **室外關鍵字**: 公園、廣場、運動場、停車場
- **優先判斷**: 直接包含「室內」、「室外」關鍵字時優先採用

### 風險標籤規則
- **High Risk**: AQI > 100
- **Warning**: AQI > 50 AND is_indoor == False
- **其他**: 無標籤

## 📏 距離計算技術

### 座標轉換
1. **WGS84 → TWD97**: 使用 `geo_coor.wgs84_2_twd97()`
2. **基準點**: 台北車站 (25.0478, 121.5170)
3. **距離公式**: TWD97 平面座標歐幾里得距離

### Haversine 公式
```python
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # 地球半徑(公里)
    # 計算兩點間的最短距離
    return distance_km
```

## 🔧 技術規格

### 開發環境
- **Python**: 3.8+
- **作業系統**: Windows/Linux/macOS
- **網路**: 需要網際網路連線

### 核心套件
```txt
requests>=2.28.0      # HTTP 請求
folium>=0.14.0        # 地圖視覺化
python-dotenv>=0.19.0  # 環境變數管理
pandas>=1.5.0         # 資料處理
geo_coor>=0.0.0       # 座標轉換
numpy>=1.21.0         # 數值計算
geopandas>=0.11.0     # 空間資料處理
pyproj>=3.3.0         # 座標系統轉換
shapely>=1.8.0        # 幾何運算
```

### 系統需求
- **記憶體**: 2GB+ RAM
- **硬碟空間**: 100MB+ 可用空間
- **網路**: 穩定的網際網路連線

## 🛠️ 執行方式

### 主要執行方式
```bash
# 方法1: 透過主選單執行 (推薦)
python main.py

# 方法2: 直接執行整合檔案
python scripts/shelter_aqi_analysis.py

# 方法3: 執行特定功能
python scripts/setup.py
python scripts/test_api.py
```

### 功能選單
```
台灣 AQI 即時地圖分析系統
============================================================
0. 系統說明
1. 環境設定安裝
2. 測試 API 連線
3. 抓取環境部API資料處理
4. 避難收容處所檢查
5. 地圖建立與分析
6. 離開程式
============================================================
```

## 🔍 故障排除

### 常見問題

**Q: API 連線失敗**
- 檢查 `.env` 檔案中的 `MOENV_API_KEY` 是否正確
- 確認網路連線正常
- 查看防火牆設定

**Q: 座標轉換錯誤**
- ⚠️ 確認 `.env` 檔案中的 `target_crs=EPSG4326` 設定正確
- 檢查原始資料座標格式
- 確認 `pyproj` 套件正確安裝

**Q: 地圖無法顯示**
- 確認 `outputs/aqi_map.html` 檔案存在
- 檢查瀏覽器控制台錯誤訊息
- 確認 Folium 版本相容

**Q: 避難所分類錯誤**
- 檢查關鍵字列表設定
- 確認中文編碼處理 (UTF-8-sig)
- 查看原始資料格式

**Q: Shapefile 讀取失敗**
- 確認 `data/鄉鎮市區界線(TWD97經緯度)/` 目錄存在
- 檢查 Shapefile 檔案完整性
- 確認 `geopandas` 套件正確安裝

## 📝 版本資訊

- **目前版本**: 1.0.0
- **最後更新**: 2026-03-06
- **作者**: AQI Analysis Team
- **授權**: MIT License

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request 來改善這個專案！

### 貢獻指南
1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -am 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 建立 Pull Request

## 📄 授權

MIT License - 詳見 [LICENSE](LICENSE) 檔案
