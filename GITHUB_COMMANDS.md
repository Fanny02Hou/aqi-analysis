# 🚀 GitHub CLI 雲端備份 - 完整命令清單

## 📋 請依序執行以下命令

### 1️⃣ 開啟命令提示字元
- 按 `Win + R`
- 輸入 `cmd` 
- 按 Enter

### 2️⃣ 切換到專案目錄
```cmd
cd C:\Users\97000\CascadeProjects\python_project
```

### 3️⃣ 檢查 Git 是否可用
```cmd
git --version
```
如果顯示錯誤，請重新啟動命令提示字元或重新安裝 Git

### 4️⃣ 初始化 Git 倉庫
```cmd
git init
```

### 5️⃣ 設定 Git 使用者資訊 (首次使用)
```cmd
git config --global user.name "您的姓名"
git config --global user.email "您的郵箱"
```

### 6️⃣ 添加所有檔案
```cmd
git add .
```

### 7️⃣ 提交變更
```cmd
git commit -m "Initial commit: AQI Analysis System with geo_coor TWD97 Conversion"
```

### 8️⃣ 登入 GitHub
```cmd
gh auth login
```
按照指示選擇登入方式 (建議選擇瀏覽器登入)

### 9️⃣ 建立 GitHub 倉庫
```cmd
gh repo create aqi-analysis --public --description "台灣空氣品質指標(AQI)分析系統 - 使用geo_coor套件進行TWD97高精度距離計算與即時地圖視覺化"
```

### 🔟 推送代碼
```cmd
git remote add origin https://github.com/YOUR_USERNAME/aqi-analysis.git
git branch -M main
git push -u origin main
```

## ⚠️ 重要提醒

- 將 `YOUR_USERNAME` 替換為您的 GitHub 使用者名稱
- 確保已完成 Git 安裝並重新啟動命令提示字元
- 如果 `gh auth login` 失敗，請嘗試 `gh auth login --web`

## ✅ 成功指標

完成後您應該看到：
- ✅ Git 倉庫初始化成功
- ✅ 檔案提交成功  
- ✅ GitHub 倉庫建立成功
- ✅ 代碼推送成功

## 🌐 最終結果

您的專案將在：`https://github.com/YOUR_USERNAME/aqi-analysis`

**包含內容：**
- 🐍 完整的 AQI 分析系統 (使用 geo_coor 套件)
- 🗺️ 互動式地圖視覺化
- 📏 TWD97 高精度距離計算
- 📊 CSV 數據匯出
- 📚 詳細文檔說明
- 🔧 requirements.txt (包含 geo_coor 套件)

**特色功能：**
- 🌍 真實環境部 API 數據
- 📐 專業 geo_coor 套件 WGS84 → TWD97 轉換
- 🎯 台灣地區高精度距離計算
- 🎨 優化分色顯示系統
- 🔒 完整的 API Key 保護機制

## 🔍 故障排除

### 如果 'origin' 不存在錯誤

**症狀:** `fatal: 'origin' does not appear to be a git repository`

**解決方案:**
```cmd
# 檢查遠端設定
git remote -v

# 如果沒有 origin，重新添加
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/aqi-analysis.git

# 重新推送
git push -u origin main
```

### 如果推送失敗

**症狀:** 推送時出現權限錯誤

**解決方案:**
1. 確認 GitHub 使用者名稱正確
2. 檢查倉庫是否已存在
3. 重新登入 GitHub CLI: `gh auth login --web`

### 如果倉庫已存在

**症狀:** `Repository already exists`

**解決方案:**
```cmd
# 直接推送到現有倉庫
git remote add origin https://github.com/YOUR_USERNAME/aqi-analysis.git
git push -u origin main
```

## 📊 專案統計

**推送成功後，您的 GitHub 倉庫將包含：**
- 📁 4 個核心檔案 (main.py + scripts/)
- 📄 4 個文檔檔案 (.md)
- 📋 1 個設定檔案 (requirements.txt)
- 🔒 1 個環境檔案 (.env - 被保護)
- 📦 1 個忽略規則檔案 (.gitignore)

**總計約 15+ 個檔案，完整呈現您的 AQI 分析系統！**
