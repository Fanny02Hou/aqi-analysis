# GitHub 雲端備份設定指南

## 🚀 快速設定步驟

### 1. 安裝 Git (如果尚未安裝)
**Windows:**
- 下載並安裝 Git for Windows: https://git-scm.com/download/win
- 或使用 Windows Package Manager: `winget install Git.Git`

### 2. 設定 GitHub CLI (已安裝)
```bash
# 登入 GitHub
gh auth login

# 檢查登入狀態
gh auth status
```

### 3. 初始化 Git 倉庫並推送
```bash
# 初始化 Git 倉庫
git init

# 添加所有檔案
git add .

# 提交變更
git commit -m "Initial commit: AQI Analysis System"

# 建立 GitHub 倉庫
gh repo create aqi-analysis --public --description "台灣空氣品質指標(AQI)分析系統 - 即時地圖視覺化與距離計算"

# 推送到 GitHub
git remote add origin https://github.com/YOUR_USERNAME/aqi-analysis.git
git branch -M main
git push -u origin main
```

## 📁 專案檔案結構
```
python_project/
├── aqi_map.py              # 主程式
├── requirements.txt         # Python 套件需求
├── setup.py               # 環境安裝腳本
├── README.md              # 專案說明
├── .env                  # 環境變數 (已加入 .gitignore)
├── .gitignore           # Git 忽略檔案
├── data/                # 資料目錄
├── outputs/             # 輸出目錄
│   ├── aqi_map.html
│   └── aqi_station_distances.csv
└── GITHUB_SETUP.md     # 此檔案
```

## ✅ 功能特色
- 🌍 即時 AQI 數據獲取 (環境部 API)
- 🗺️ 互動式地圖視覺化 (Folium)
- 📏 精確距離計算 (Haversine 公式)
- 📊 CSV 數據匯出
- 🎨 優化分色顯示 (綠/黃/紅)
- 📍 詳細測站資訊

## 🔧 技術規格
- **語言**: Python 3.10+
- **主要套件**: requests, folium, pandas, python-dotenv
- **數據源**: 環境部開放 API (data.moenv.gov.tw)
- **地圖**: OpenStreetMap + Folium
- **計算**: Haversine 距離公式

## 📝 注意事項
- `.env` 檔案包含 API Key，已自動排除在版本控制外
- `outputs/` 目錄包含生成檔案，建議保留或手動添加重要結果
- 請確保在 GitHub 上設定正確的遠端 URL

## 🎯 完成後
您的專案將在: https://github.com/YOUR_USERNAME/aqi-analysis
