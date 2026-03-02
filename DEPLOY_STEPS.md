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
**預期輸出:** `git version 2.x.x`

**如果出現錯誤:**
- 重新啟動命令提示字元
- 或重新安裝 Git: https://git-scm.com/download/win

### 步驟 4: 檢查專案結構
```bash
dir
```
**應該看到:**
- `main.py`
- `scripts/` 資料夾
- `.env` 檔案
- `requirements.txt`
- `.gitignore`

### 步驟 5: 初始化 Git 倉庫
```bash
git init
```
**成功訊息:** `Initialized empty Git repository`

### 步驟 6: 設定 Git 使用者資訊
```bash
git config --global user.name "您的姓名"
git config --global user.email "您的郵箱"
```

### 步驟 7: 檢查要提交的檔案
```bash
git status
```
**重要確認:**
- ✅ `.env` 應該在 "Untracked files" 中 (這是正常的)
- ✅ 其他 `.py` 檔案應該在綠色列表中

### 步驟 8: 添加檔案到 Git
```bash
git add .
```

### 步驟 9: 提交變更
```bash
git commit -m "Initial commit: AQI Analysis System with TWD97 distance calculation"
```

### 步驟 10: 檢查 GitHub CLI
```bash
gh --version
gh auth status
```

**如果未登入:**
```bash
gh auth login --web
```

### 步驟 11: 建立 GitHub 倉庫
```bash
gh repo create aqi-analysis --public --description "台灣AQI即時地圖分析系統 - 使用geo_coor套件進行TWD97高精度距離計算"
```

### 步驟 12: 連接遠端倉庫
```bash
git remote add origin https://github.com/YOUR_USERNAME/aqi-analysis.git
```
**重要:** 將 `YOUR_USERNAME` 替換為您的 GitHub 使用者名稱

### 步驟 13: 推送代碼
```bash
git branch -M main
git push -u origin main
```

## 🔍 驗證步驟

### 檢查本地 Git 狀態
```bash
git status
git log --oneline
```

### 檢查遠端連接
```bash
git remote -v
```

### 檢查 GitHub 倉庫
在瀏覽器中訪問: `https://github.com/YOUR_USERNAME/aqi-analysis`

## ⚠️ 常見問題與解決方案

### 問題 1: Git 命令無法識別
**錯誤訊息:** `'git' is not recognized`

**解決方案:**
1. 完全關閉命令提示字元
2. 重新開啟命令提示字元
3. 再次嘗試 `git --version`

### 問題 2: GitHub CLI 未授權
**錯誤訊息:** `not logged in`

**解決方案:**
```bash
gh auth logout
gh auth login --web
```

### 問題 3: 推送權限被拒絕
**錯誤訊息:** `Permission denied`

**解決方案:**
1. 確認 GitHub 使用者名稱正確
2. 檢查倉庫名稱是否正確
3. 確認 GitHub 帳號有建立公開倉庫權限

### 問題 4: 倉庫已存在
**錯誤訊息:** `Repository already exists on remote`

**解決方案:**
```bash
# 直接連接到現有倉庫
git remote add origin https://github.com/YOUR_USERNAME/aqi-analysis.git
git push -u origin main
```

### 問題 5: 網路連線問題
**錯誤訊息:** `unable to access`

**解決方案:**
1. 檢查網路連線: `ping github.com`
2. 檢查防火牆設定
3. 嘗試使用手機熱點

## ✅ 成功指標

完成所有步驟後，您應該看到：

**本地端:**
- ✅ Git 倉庫已初始化
- ✅ 檔案已提交
- ✅ 分支已設定為 main

**GitHub 端:**
- ✅ 倉庫 `aqi-analysis` 已建立
- ✅ 代碼已推送成功
- ✅ 檔案列表正確顯示

**最終驗證:**
```bash
# 檢查推送狀態
git status

# 應該顯示: "nothing to commit, working tree clean"
```

## 🎯 完成後的專案結構

您的 GitHub 倉庫將包含：

```
aqi-analysis/
├── main.py                 # 主程式入口
├── scripts/              # 核心模組
│   ├── aqi_map.py       # AQI 分析系統
│   ├── setup.py         # 環境設定
│   └── test_api.py      # API 測試
├── outputs/             # 輸出目錄 (本地端)
├── .env               # 環境變數 (被保護)
├── requirements.txt    # 套件需求
├── .gitignore         # Git 忽略規則
├── README.md          # 專案說明
├── GITHUB_SETUP.md   # Git 設定指南
├── GITHUB_COMMANDS.md # 命令清單
└── DEPLOY_STEPS.md   # 部署步驟
```

## 🚀 下一步

完成雲端備份後，您可以：
1. **分享專案:** 將 GitHub 連結分享給其他人
2. **協作開發:** 邀請其他開發者貢獻
3. **持續更新:** 使用 `git add/commit/push` 更新代碼
4. **建立版本:** 使用 GitHub Releases 管理版本

**恭喜！您的 AQI 分析系統已成功備份到 GitHub！** 🎉
