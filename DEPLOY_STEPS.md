# 🚀 GitHub 雲端備份實作步驟

## 📋 操作清單

### 步驟 1: 開啟命令提示字元或 PowerShell
1. 按 `Win + R` 開啟執行對話框
2. 輸入 `cmd` 或 `powershell` 按 Enter
3. 或在 VS Code 中按 `Ctrl + ` ` (反引號) 開啟終端機

### 步驟 2: 切換到專案目錄
```bash
cd C:\Users\97000\CascadeProjects\python_project
```

### 步驟 3: 檢查 Git 是否正常運作
```bash
git --version
```
如果顯示版本號碼表示 Git 正常，如果顯示錯誤請重新啟動命令提示字元

### 步驟 4: 初始化 Git 倉庫
```bash
git init
```

### 步驟 5: 設定 Git 使用者資訊 (首次使用)
```bash
git config --global user.name "您的姓名"
git config --global user.email "您的郵箱"
```

### 步驟 6: 添加檔案到 Git
```bash
git add .
```

### 步驟 7: 提交變更
```bash
git commit -m "Initial commit: AQI Analysis System"
```

### 步驟 8: 登入 GitHub (如果尚未登入)
```bash
gh auth login
```
按照指示選擇瀏覽器登入或 token 登入

### 步驟 9: 建立 GitHub 倉庫
```bash
gh repo create aqi-analysis --public --description "台灣空氣品質指標(AQI)分析系統 - 即時地圖視覺化與距離計算"
```

### 步驟 10: 連接遠端倉庫
```bash
git remote add origin https://github.com/YOUR_USERNAME/aqi-analysis.git
```
(請將 YOUR_USERNAME 替換為您的 GitHub 使用者名稱)

### 步驟 11: 推送到 GitHub
```bash
git branch -M main
git push -u origin main
```

## 🔍 可能遇到的問題與解決方案

### 問題 1: Git 命令無法識別
**解決方案**: 
1. 重新啟動命令提示字元
2. 或檢查 Git 安裝路徑是否在系統 PATH 中

### 問題 2: GitHub CLI 登入失敗
**解決方案**:
1. 確保網路連線正常
2. 使用 `gh auth login --web` 選擇瀏覽器登入

### 問題 3: 推送失敗 - 權限錯誤
**解決方案**:
1. 確認 GitHub 倉庫名稱正確
2. 檢查是否有推送權限
3. 使用 `gh auth status` 檢查登入狀態

## ✅ 成功指標
完成後您應該看到：
- Git 倉庫初始化成功
- 檔案提交成功
- GitHub 倉庫建立成功
- 代碼推送成功

## 🌐 結果
您的專案將在：https://github.com/YOUR_USERNAME/aqi-analysis

包含：
- 完整的 AQI 分析系統
- 即時地圖視覺化
- 距離計算結果
- 詳細文檔說明
