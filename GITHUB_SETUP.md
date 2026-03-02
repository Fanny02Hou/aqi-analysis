# GitHub 雲端備份設定指南

## 🚀 快速設定步驟

### 1. 安裝 Git (如果尚未安裝)

**Windows:**
- 下載並安裝 Git for Windows: https://git-scm.com/download/win
- 或使用 Windows Package Manager: `winget install Git.Git`

**驗證安裝:**
```bash
git --version
```

### 2. 安裝 GitHub CLI (已安裝)

**驗證安裝:**
```bash
gh --version
```

### 3. 設定 GitHub CLI

```bash
# 登入 GitHub
gh auth login

# 檢查登入狀態
gh auth status
```

**登入流程:**
1. 選擇 `GitHub.com`
2. 選擇 `HTTPS` 或 `SSH`
3. 選擇瀏覽器登入 (推薦)
4. 在瀏覽器中完成 GitHub 授權

### 4. 專案結構確認

確保您的專案結構如下：
```
python_project/
├── main.py                 # 主程式入口
├── .env                   # 環境變數 (已被 .gitignore 保護)
├── requirements.txt        # 套件需求
├── .gitignore            # Git 忽略規則
├── scripts/              # 核心程式模組
│   ├── aqi_map.py       # AQI 地圖生成器
│   ├── setup.py         # 環境設定
│   └── test_api.py      # API 測試工具
├── outputs/             # 輸出檔案
└── docs/               # 文檔檔案
```

### 5. 檔案保護機制

**✅ 已被 .gitignore 保護的檔案:**
- `.env` - 您的 API Key (絕對安全)
- `__pycache__/` - Python 快取檔案
- `*.pyc` - 編譯檔案
- `venv/`, `env/` - 虛擬環境
- `.vscode/`, `.idea/` - IDE 設定
- `outputs/` - 輸出檔案 (可選)

**🔒 API Key 安全性:**
您的環境部 API Key 在 `.env` 檔案中，已被 `.gitignore` 完全保護，不會上傳到 GitHub。

### 6. 驗證 Git 狀態

```bash
# 檢查 Git 狀態
git status

# 檢查遠端設定
git remote -v
```

## 🔧 常見問題解決

### Git 未找到錯誤

**症狀:** `git: command not found`

**解決方案:**
1. 重新啟動命令提示字元
2. 檢查 Git 是否在 PATH 中: `echo %PATH%`
3. 重新安裝 Git

### GitHub CLI 登入失敗

**症狀:** `gh auth login` 失敗

**解決方案:**
```bash
# 使用瀏覽器登入
gh auth login --web

# 或檢查網路連線
gh auth status
```

### 權限問題

**症狀:** `Permission denied`

**解決方案:**
1. 確認 GitHub 帳號有建立倉庫權限
2. 檢查網路防火牆設定
3. 使用 HTTPS 而非 SSH (初次使用推薦)

## 📋 設定檢查清單

- [ ] Git 已安裝並可執行
- [ ] GitHub CLI 已安裝並登入
- [ ] `.env` 檔案包含正確的 API Key
- [ ] `.gitignore` 檔案存在並包含 `.env`
- [ ] 專案結構正確
- [ ] 網路連線正常

## 🎯 下一步

完成設定後，請參考：
- `GITHUB_COMMANDS.md` - 完整命令清單
- `DEPLOY_STEPS.md` - 詳細部署步驟

## 📞 技術支援

如遇到問題，請檢查：
1. Git 版本: `git --version`
2. GitHub CLI 狀態: `gh auth status`
3. 網路連線: `ping github.com`
4. 防火牆設定
