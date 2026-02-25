# 台灣 AQI 即時地圖

這個專案透過環境部開放 API 獲取全台即時空氣品質指標 (AQI) 數據，並使用 Folium 在地圖上視覺化顯示。

## 功能特色

- 🌍 串接環境部 `aqx_p_432` API 獲取即時 AQI 數據
- 📍 在互動式地圖上標示所有測站位置
- 🎨 根據 AQI 值使用不同顏色顯示空氣品質狀況
- 🔧 自動環境安裝設定
- 📱 響應式設計，支援各種裝置

## 快速開始

### 1. 設定 API Key

編輯 `.env` 檔案，將 `your_api_key_here` 替換為您的環境部 API Key：

```bash
# Environment Variables
API_KEY=your_actual_api_key_here
DATABASE_URL=your_database_url_here
SECRET_KEY=your_secret_key_here
```

### 2. 自動安裝環境

執行安裝腳本：

```bash
python setup.py
```

### 3. 執行程式

```bash
python aqi_map.py
```

執行完成後，地圖會儲存至 `outputs/aqi_map.html`，用瀏覽器開啟即可查看。

## 手動安裝

如果自動安裝失敗，可以手動安裝：

```bash
pip install -r requirements.txt
```

## 專案結構

```
python_project/
├── data/              # 資料目錄
├── outputs/           # 輸出目錄
├── .env              # 環境變數設定
├── .gitignore        # Git 忽略檔案
├── requirements.txt  # Python 套件需求
├── setup.py          # 環境安裝腳本
├── aqi_map.py        # 主程式
└── README.md         # 說明文件
```

## AQI 顏色對應

- 🟢 **綠色** (0-50): 良好
- 🟡 **黃色** (51-100): 普通
- 🟠 **橙色** (101-150): 對敏感族群不健康
- 🔴 **紅色** (151-200): 對所有族群不健康
- 🟣 **紫色** (201-300): 非常不健康
- ⚫ **褐紅色** (300+): 危害

## API 資訊

- **API 端點**: `https://data.epa.gov.tw/api/v2/aqx_p_432`
- **資料格式**: JSON
- **更新頻率**: 即時

## 需求套件

- `requests`: HTTP 請求
- `folium`: 地圖視覺化
- `python-dotenv`: 環境變數管理
- `pandas`: 資料處理

## 注意事項

1. 需要有效的環境部 API Key 才能獲取數據
2. 確保網路連線正常
3. 地圖檔案可能較大，建議使用現代瀏覽器開啟

## 授權

MIT License
