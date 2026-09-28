# 脚本入口与读写范围

在项目根目录激活 `webproj` 后执行。所有命令入口保留在本目录；`alark_publishing/` 是内部引擎，不需要直接运行其中的文件。

| 命令 | 作用 | 写入位置 |
| --- | --- | --- |
| `python scripts/publish.py list` | 列出已配置书籍 | 无；运行环境可能初始化缓存 |
| `python scripts/publish.py build <slug> --profile all` | 构建书籍与书架 | `exports/`、`.cache/` |
| `python scripts/publish.py init <slug> --title 标题` | 创建新书 | **`vault/books/`** |
| `python scripts/publish.py check <file>` | 检查成品 | 无；结果输出到终端 |
| `python scripts/check_epub.py <file.epub>` | 正式 EPUBCheck | 输入文件旁的校验报告 |
| `python scripts/bootstrap_fonts.py` | 下载和生成字体 | `design/fonts/` |
| `python scripts/make_samples.py` | 重建基础测试图片 | **`vault/assets/layout-lab/`** |
| `python scripts/make_finance_samples.py` | 重建商业和投资图表 | **`vault/assets/business-architecture/`、`vault/assets/through-volatility/`** |
| `python scripts/make_longform_assets.py` | 重建长篇样书的原创插画与图表 | **`vault/assets/longform-lab/`** |
| `python scripts/review_longform.py` | 统计篇幅并生成实际正文样张 | `exports/longform-review/` |
| `python scripts/make_folio_review.py` | 生成摄影集实际书页与对页预览 | `exports/shore-and-space/previews/` |
| `python scripts/make_design_boards.py` | 拼合实际导出页预览 | `exports/` |
| `python scripts/make_editorial_review.py` | 生成主力书系的实际 PDF 对页 | `exports/visual-review/` |
| `python scripts/browser_check.py` | 浏览器展示检查 | `exports/visual-review/` |
| `python -m unittest discover -s scripts/tests -v` | 转换、主题和已有 EPUB 检查 | 系统临时目录；Python 字节码缓存 |

基础预览拼图和浏览器检查需要先构建原有五本样书；摄影集构建后会自动加入浏览器检查；浏览器工具额外依赖 `requirements-dev.txt` 和 Playwright Chromium。普通出版只需 `requirements.txt` 与 Conda 原生库。

[项目组织](../docs/architecture.md) · [日常使用](../README.md)
