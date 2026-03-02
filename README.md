# 台灣 AQI 即時地圖分析系統

這個專案透過環境部開放 API 獲取全台即時空氣品質指標 (AQI) 數據，並使用 Folium 在地圖上視覺化顯示，同時計算各測站到台北車站的 TWD97 高精度距離。

## 功能特色

- 🌍 串接環境部 `data.moenv.gov.tw/api/v2/aqx_p_432` API 獲取即時 AQI 數據
- 📍 在互動式地圖上標示所有測站位置
- 🎨 根據 AQI 值使用不同顏色顯示空氣品質狀況
- 📏 使用 `geo_coor` 套件進行 WGS84 到 TWD97 座標轉換
- 📐 計算各測站到台北車站的高精度距離
- 📊 匯出距離數據為 CSV 格式
- 🔧 模組化架構，所有功能透過 `main.py` 統一管理

## 專案架構

```
python_project/
├── main.py                 # 主程式入口
├── .env                   # 環境變數設定
├── requirements.txt        # Python 套件需求
├── .gitignore            # Git 忽略檔案
├── scripts/              # 核心程式模組
│   ├── aqi_map.py       # AQI 地圖生成器
│   ├── setup.py         # 環境設定工具
│   └── test_api.py      # API 連線測試
├── outputs/             # 輸出檔案目錄
│   ├── aqi_map.html    # 互動式地圖
│   └── aqi_station_distances_twd97.csv  # 距離數據
└── docs/               # 文檔目錄
    ├── README.md
    ├── GITHUB_SETUP.md
    ├── GITHUB_COMMANDS.md
    └── DEPLOY_STEPS.md
```

## 快速開始

### 1. 環境設定

```bash
# 執行自動設定
python main.py
# 選擇選項 1: 環境設定安裝
```

### 2. 設定 API Key

編輯 `.env` 檔案，將 `your_api_key_here` 替換為您的環境部 API Key：

```bash
# Environment Variables
MOENV_API_KEY=your_actual_api_key_here
```

### 3. 執行程式

```bash
# 執行主程式
python main.py
```

**選單選項：**
- `1` - 環境設定安裝
- `2` - 生成 AQI 地圖
- `3` - 測試 API 連線
- `4` - 顯示系統資訊
- `5` - 離開程式

## 技術規格

### 🌐 API 端點

**主要 API (已驗證可用):**
```
https://data.moenv.gov.tw/api/v2/aqx_p_432
```
- ✅ 需要 API Key
- ✅ 回傳 84+ 筆即時測站數據
- ✅ 支援 JSON 格式

### 📏 距離計算

**座標轉換流程：**
1. **WGS84 → TWD97**: 使用 `geo_coor.wgs84_2_twd97()`
2. **距離計算**: TWD97 平面座標歐幾里得公式
3. **精度**: < 1 公尺誤差

**台北車站基準點：**
- 🌍 WGS84: (25.0478, 121.5170)
- 📏 TWD97: (302139.68, 2783634.00)

### 🎨 AQI 顏色對應

| AQI 範圍 | 狀態 | 地圖標記顏色 |
|----------|------|-------------|
| 0-50 | 良好 | 🟢 綠色 |
| 51-100 | 普通 | 🟡 黃色 |
| 101+ | 不健康 | 🔴 紅色 |

## 輸出檔案

### 📍 互動式地圖
- **檔案**: `outputs/aqi_map.html`
- **特色**: 
  - 響應式設計
  - 彈出視窗顯示詳細資訊
  - 滑鼠懸停提示
  - AQI 數值統一黑色顯示

### 📊 距離數據
- **檔案**: `outputs/aqi_station_distances_twd97.csv`
- **欄位**:
  - 測站名稱
  - 所在縣市
  - 緯度(WGS84)
  - 經度(WGS84)
  - 距離台北車站_TWD97(公里)
  - AQI
  - 主要污染物
  - 空氣品質狀態

## 開發工具

### 📦 套件需求

```txt
requests>=2.28.0
folium>=0.14.0
python-dotenv>=0.19.0
pandas>=1.5.0
geo_coor>=0.0.0
```

### 🧪 測試工具

```bash
# 測試 API 連線
python scripts/test_api.py

# 直接執行 AQI 分析
python scripts/aqi_map.py

# 環境設定
python scripts/setup.py
```

## 系統需求

- Python 3.8+
- 網路連線 (用於 API 存取)
- 2GB+ RAM
- 100MB+ 硬碟空間

## 故障排除

### 常見問題

**Q: API 連線失敗**
- 檢查網路連線
- 確認 API Key 正確設定
- 執行 `python main.py` 選擇選項 3 測試連線

**Q: 地圖無法顯示**
- 確認 `outputs/aqi_map.html` 檔案存在
- 使用現代瀏覽器開啟 (Chrome, Firefox, Edge)

**Q: 距離計算錯誤**
- 確認 `geo_coor` 套件正確安裝
- 檢查測站座標格式

## 版本資訊

- **版本**: 1.0.0
- **最後更新**: 2026-03-02
- **作者**: AQI Analysis Team
- **授權**: MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request 來改善這個專案！

## 授權

MIT License - 詳見 LICENSE 檔案
