# 脚本入口与读写范围

在项目根目录激活 `webproj` 后执行。日常命令放在本目录，样张工具放在 `previews/`，会写入原稿素材的工具放在 `assets/`；`alark_publishing/` 是内部引擎，不需要直接运行其中的文件。

| 命令 | 作用 | 写入位置 |
| --- | --- | --- |
| `python scripts/publish.py list` | 列出已配置书籍 | 无；运行环境可能初始化缓存 |
| `python scripts/publish.py build <slug> --profile all` | 构建书籍与书架 | `exports/`、`.cache/` |
| `python scripts/publish.py init <slug> --title 标题` | 创建新书 | **`vault/books/`** |
| `python scripts/publish.py check <file>` | 检查成品 | 无；结果输出到终端 |
| `python scripts/check_epub.py <file.epub>` | 正式 EPUBCheck | 输入文件旁的校验报告 |
| `python scripts/bootstrap_fonts.py` | 下载和生成字体 | `design/fonts/` |
| `python scripts/assets/make_samples.py` | 重建基础测试图片 | **`vault/assets/layout-lab/`** |
| `python scripts/assets/make_finance_samples.py` | 重建商业和投资图表 | **`vault/assets/business-architecture/`、`vault/assets/through-volatility/`** |
| `python scripts/assets/make_longform_assets.py` | 重建长篇样书的原创插画与图表 | **`vault/assets/longform-lab/`** |
| `python scripts/previews/review_longform.py` | 统计篇幅并生成实际正文样张 | `exports/longform-review/` |
| `python scripts/previews/make_folio_review.py` | 生成摄影集实际书页与对页预览 | `exports/shore-and-space/previews/` |
| `python scripts/previews/make_design_boards.py` | 拼合实际导出页预览 | `exports/` |
| `python scripts/previews/make_editorial_review.py` | 生成主力书系的实际 PDF 对页 | `exports/visual-review/` |
| `python scripts/previews/review_refinement.py` | 生成修改前后真实书页对照；`--focus aesthetics` 展示审美精修，`--focus spectacle` 展示摄影杂志改版，`--focus tension` 展示构图张力精修 | `exports/refinement-review/`、`exports/aesthetic-review/` 、`exports/spectacle-redesign/` 或 `exports/spectacle-tension/` |
| `python scripts/browser_check.py` | 浏览器展示检查 | `exports/visual-review/` |
| `python -m unittest discover -s scripts/tests -v` | 转换、主题和已有 EPUB 检查 | 系统临时目录；Python 字节码缓存 |

基础预览拼图和浏览器检查需要先构建原有五本样书；摄影集构建后会自动加入浏览器检查；浏览器工具额外依赖 `requirements-dev.txt` 和 Playwright Chromium。普通出版只需 `requirements.txt` 与 Conda 原生库。

[项目组织](../docs/architecture.md) · [日常使用](../README.md)

## 路径调整

样张脚本由 `scripts/<文件名>.py` 移至 `scripts/previews/<文件名>.py`，三个素材生成脚本移至 `scripts/assets/`。`vault/assets/*/SOURCE.md` 内的旧脚本路径保留为素材生成时的历史出处，新入口见上表。整理过程不运行素材生成器。
