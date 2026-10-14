# WXLPub — wxl-physics 自动编译仓库

推送到 GitHub 后 Actions 自动编译 wxl-physics.dll 和 phy2 生成器 EXE。

## 结构
- `.github/workflows/` — 两个编译工作流
- `src/` + `wxl.json` — wxl-physics 扩展源码（从 wxl-equip-plus 裁剪，只保留物理）
- `phy2_dd/` — 拖放生成 .phy2 的工具（EXE 由 workflow 打包）

## 产物获取
Actions → 最新成功运行 → Artifacts 下载
