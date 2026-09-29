# 安装、构建与检查

[文档导航](README.md) · [项目首页](../README.md)

以下命令在项目根目录运行。

## 安装与复现

当前 `webproj` 已安装并运行通过。另一台机器可执行：

```bash
conda env update -f environment.yml
conda activate webproj
python scripts/bootstrap_fonts.py
python scripts/publish.py build --all --profile all
python scripts/previews/make_design_boards.py
python scripts/previews/make_editorial_review.py
python scripts/previews/review_longform.py
python scripts/previews/make_folio_review.py
python scripts/previews/review_refinement.py
python scripts/previews/review_refinement.py --focus aesthetics
python scripts/previews/review_refinement.py --focus spectacle
python scripts/previews/review_refinement.py --focus tension
```

仓库已包含六本样书所需的素材，常规构建无需重新生成。修改图表后，可运行 `python scripts/assets/make_finance_samples.py` 重建商业与投资 SVG，或运行 `python scripts/assets/make_samples.py` 重建基础图文测试素材，再构建对应书籍。`make_design_boards.py` 依赖五本书已经生成的封面与两本新书的竖版 PDF。

字体脚本需要网络，只从 Google Fonts 官方仓库下载 Noto Serif SC / Noto Sans SC，生成常规字重。大型 TTF 不入 Git，OFL 许可证保留在 `design/fonts/`。PDF 自动嵌入用到的字体；EPUB 嵌入按本书内容裁剪的字体，并附许可证。首次安装需要 Pango 原生库，已经写入 Conda 配置。Linux 启动脚本会自动发现当前环境的动态库路径。

构建本身无需网络。文章中的远程图片请先保存到 `vault/assets`。外部网页链接可以保留，构建不会访问它们。

## 检查与视觉复核

```bash
python -m unittest discover -s scripts/tests -v
python scripts/publish.py check exports/layout-lab/layout-lab-portrait.pdf
python scripts/publish.py check exports/layout-lab/layout-lab.epub
```

每本书的 `checks.json` 记录本次构建的产物、页面尺寸、可提取文字、页面外文字、字体与图片清晰度、EPUB 资源与锚点检查。产物检查失败时返回非零状态，报告写入 `exports/<slug>-failed-checks.json`，已发布的成书不会被本次失败替换。配置或解析阶段出错时会直接提示错误，可能尚未生成检查报告。样书的 `previews/*-contact.png` 是所有页面的缩略图，方便观察节奏和留白。

正式 EPUB 校验使用 [W3C EPUBCheck](https://github.com/w3c/epubcheck)。本机已下载 5.3.0 到 `.cache/tools/epubcheck-5.3.0`。新机器下载该版本的发布 ZIP 解压到 `.cache/tools/`，或将 `EPUBCHECK_JAR` 指向已安装的 jar；需要 Java。

```bash
python scripts/publish.py build --all --profile all --epubcheck
# 单独校验已有书籍
python scripts/check_epub.py exports/layout-lab/layout-lab.epub
```

视觉回归脚本需先完成六本书的构建和预览图生成，并安装 Playwright 的 Chromium：

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python scripts/browser_check.py
```

`python scripts/browser_check.py` 使用 Playwright 与 Chromium（本机已有）。它检查书架、六款设计对照、视觉手册、HTML 正文和 EPUB XHTML 在桌面及 390 px 手机宽度下的溢出、图片加载和字体状态，并保存截图到 `exports/visual-review/`。它不替代 Apple Books、微信读书等实际阅读器的实机测试。

当前二十九项测试通过，转换用例均在系统临时目录运行；视觉检查覆盖 80 个浏览器页面与视口组合。六本 EPUBCheck 均零错误、零警告。PDF 均无结构错误；摄影集及《欲望制造》横版、A4 大图封面保留分辨率提醒。详细记录见 [验证记录](../docs/history/validation.md)。

## 构建报告

只导出 HTML 的新书也会显示在书架，无封面图片时显示文字封面。重新生成 EPUB 时会清除旧正式校验报告；`checks.json` 的 `epubcheck_status` 记录本次状态。需要正式校验时添加 `--epubcheck`。

书架会列出已有的竖版、横版和 A4 HTML。没有成品的草稿不参与书架信息解析；已有成品但配置暂时无效的书会以目录名展示，并在终端提示。实际构建仍会严格校验该书配置。
