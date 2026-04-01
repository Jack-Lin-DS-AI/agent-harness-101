# 約束 — 信任的基礎

## 定義代理不能做什麼

約束層是整個信任模型的基礎。在代理可以做任何事情之前，harness 必須決定它**不能**做什麼。

## ToolPermissionContext — 20 行的權限引擎

claw-code 的 `permissions.py` 可能是最具教學意義的文件之一：僅 20 行 Python 程式碼就實現了完整的權限引擎。

兩種機制：
- **deny_names**：精確名稱比對的阻止列表（frozenset）
- **deny_prefixes**：前綴比對的阻止列表（tuple）

`blocks()` 方法是完整的權限檢查：
1. 工具名稱是否在拒絕列表中？（精確比對）
2. 工具名稱是否以拒絕前綴開頭？（前綴比對）

> 簡潔本身就是教學重點：20 行 Python 編碼了一個完整的權限模型。

## 權限閘門式工具過濾

`filter_tools_by_permission_context()` 在工具到達 LLM 之前過濾它們。被拒絕的工具**永遠不會**出現在模型的工具列表中。這比事後檢查更安全——模型甚至不知道被封鎖的工具存在。

## 權限拒絕追蹤

當工具被拒絕時，harness 記錄：
- **哪個**工具被拒絕（tool_name）
- **為什麼**被拒絕（reason）

拒絕記錄在 TurnResult 中報告，這樣 LLM 就知道為什麼它的請求被拒絕了。透明度是信任的關鍵。

## 信任模式

claw-code 使用二元信任閘門：
- `trusted=True` → 完整功能啟用
- `trusted=False` → 限制模式（延遲初始化被跳過）

Claude Code 有更豐富的 5 種權限模式，但基本原則相同：在啟動時建立信任邊界。

## 沙箱模式（來自 Rust sandbox.rs）

claw-code 的 Rust 層（sandbox.rs，364 行）實現了作業系統級別的隔離：
- Linux 命名空間隔離
- 檔案系統模式：off / workspace_only / allowlist
- 網路存取控制
- 優雅降級：偵測能力，報告為什麼沙箱不可用

## 通用模式

每個安全的代理都需要模型和行動之間的約束層。這個層級回答一個根本問題：**我們信任代理做什麼？**
