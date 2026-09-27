# AIark / Alark Books

在 Obsidian 中写作，用一份 Markdown 生成带封面、目录、章节页、图注、页眉页脚的 PDF，以及可调整字号的 EPUB。

**先看成品：** [作品书架](exports/index.html) · [视觉设计手册](design/visual-system.html) · [写作规范](design/writing-guide.md)

当前视觉方向为**纸本与摄影刊物**：宋体标题、首行缩进、自然纸白、外侧页码、细线表格，并提供摄影／纯字体两种封面。详见 [v0.2 设计调整](design/editorial-direction.md)。

另有独立的 **SPECTACLE 高冲击编辑主题**，用于《欲望制造》：黑红银广告图像、巨幅字排与整页宣言。[查看视觉方案](design/spectacle.html) · [配置说明](design/spectacle.md)。

```bash
python scripts/publish.py build desire-manufacture --profile all --epubcheck
```

## 五款设计样书

[打开五款设计对照](design/five-designs.html) · [商业与投资主题说明](design/business-investment.md)

| 书名 | 视觉方向 | 主题配置 |
| --- | --- | --- |
| 内容的复利 | 摄影书刊 | editorial + 摄影封面 |
| 留一点时间思考 | 极简随笔 | editorial + 纯字封面 |
| 欲望制造 | 奢华传播 | spectacle |
| 生意的结构 | 商业蓝图 | business |
| 穿越波动 | 投资年鉴 | investment |

两本新样书各四章，均提供竖版、横版、A4 PDF 与流式 EPUB。商业案例与投资图表使用明确标注的虚构数据。封面支持 PNG、JPEG 和 SVG。

```bash
python scripts/publish.py build business-architecture --profile all --epubcheck
python scripts/publish.py build through-volatility --profile all --epubcheck
```

## 日常使用

```bash
conda activate webproj

# 看有哪些书（没有 book.yml 的目录不会自动导出）
python scripts/publish.py list

# 新建一本书，然后在 Obsidian 中打开 vault/books/my-book
python scripts/publish.py init my-book --title "我的新书"

# 导出竖版 PDF、EPUB、可在浏览器阅读的 HTML
python scripts/publish.py build my-book

# 同时生成竖版、横版与 A4；EPUB 只生成一份
python scripts/publish.py build my-book --profile all

# 只导出一种格式
python scripts/publish.py build my-book --profile landscape --format pdf

# 导出所有已经配置的书籍
python scripts/publish.py build --all --profile all
```

每本书的结果保存在 `exports/<书籍目录名>/`。`exports/index.html` 在构建后自动更新，可以直接用浏览器打开。`website/index.html` 是同一书架的入口。

本次提供两本独立样书：五章图文长书 `layout-lab`《内容的复利》，以及两章文字札记 `field-notes`《留一点时间思考》。现有 `vault/books/ai-media` 未改动，也没有被添加到自动构建列表。

## 目录约定

| 目录 / 文件 | 作用 |
| --- | --- |
| `vault/books/<slug>/` | 每个目录一本书，Markdown 正文 + `book.yml` |
| `vault/assets/` | Obsidian 图片、图表与其他写作素材 |
| `design/` | 品牌视觉手册、排版决策、写作规范、标志与字体授权 |
| `website/styles/` | PDF、HTML 与 EPUB 的样式代码 |
| `website/templates/` | 书籍与作品书架的 HTML 模板 |
| `scripts/` | 构建、校验、字体安装和原创样例图片脚本 |
| `exports/` | 生成的书、网页、封面、页面联系表与检查报告；不提交 Git |
| `publishing.yml` | 全局 IP 名称、作者默认值、页面规格 |

保留 `website` 这个名字：它既承载出版样式，也提供轻量的本地阅读入口，不需要引入前端框架。

## 一本书的配置

```yaml
title: 内容的复利
subtitle: 从 AI 创作到可持续的个人商业
author: Alark
language: zh-CN
identifier: urn:uuid:e428ca94-ac38-4113-98cd-34e1783d7c91
series: CREATOR SYSTEMS
volume: '01'
date: '2026-09'
edition: 第一版
theme: vermilion  # 或 forest
chapters:
  - 01-preface.md
  - 02-system.md
```

`chapters` 是唯一的章节顺序来源。提纲、草稿、参考笔记只有被列入时才会进入成书。添加、删去或调整章节，只需修改该列表。`init` 会生成稳定的 UUID，不覆盖已存在的目录。标题必填，其他字段参见样书；日期建议用引号。

品牌从 AIark 改为 Alark 时，修改 `publishing.yml` 的 `brand.name`；两者的准确拼写会保留在元数据里。书籍可以覆盖作者署名，所有已配置书籍重新构建后使用新的品牌。

## 版式

| 配置 | 页面 | 用途 |
| --- | --- | --- |
| `portrait` | 148 × 210 mm | 单栏长文、中文阅读 |
| `landscape` | 240 × 170 mm | 双栏文本组、通栏图表、方法论展示 |
| `a4` | 210 × 297 mm | 工作手册、较大的图表与打印阅读 |
| EPUB | 流式重排，无固定页数 | 手机、电纸书；读者可调整字号 |

这里的“竖版”是纵向纸张，正文仍从左至右横排；不包含传统中文竖排。EPUB 以本次第一个页面配置的封面作为书架封面，正文始终流式排版。

PDF 支持嵌入中文字体、可点击目录与书签、页码、跨章跳转、跨页重复表头、章末注与自动分页。HTML 是连续阅读预览，PDF 才是最终分页依据。正文采用接近纸白的底色，印厂版本可另行配置。

## 安装与复现

当前 `webproj` 已安装并运行通过。另一台机器可执行：

```bash
conda env update -f environment.yml
conda activate webproj
python scripts/bootstrap_fonts.py
python scripts/make_samples.py
python scripts/publish.py build --all --profile all
```

字体脚本需要网络，只从 Google Fonts 官方仓库下载 Noto Serif SC / Noto Sans SC，生成常规字重。大型 TTF 不入 Git，OFL 许可证保留在 `design/fonts/`。PDF 自动嵌入用到的字体；EPUB 嵌入按本书内容裁剪的字体，并附许可证。首次安装需要 Pango 原生库，已经写入 Conda 配置。Linux 启动脚本会自动发现当前环境的动态库路径。

构建本身无需网络。文章中的远程图片请先保存到 `vault/assets`。外部网页链接可以保留，构建不会访问它们。

## 检查与视觉复核

```bash
python -m unittest discover -s scripts/tests -v
python scripts/publish.py check exports/layout-lab/layout-lab-portrait.pdf
python scripts/publish.py check exports/layout-lab/layout-lab.epub
```

每本书的 `checks.json` 记录本次构建的产物、页面尺寸、可提取文字、页面外文字、字体与图片清晰度、EPUB 资源与锚点检查。失败时返回非零状态，报告写入 `exports/<slug>-failed-checks.json`，已发布的成书不会被本次失败替换。样书的 `previews/*-contact.png` 是所有页面的缩略图，方便观察节奏和留白。

正式 EPUB 校验使用 [W3C EPUBCheck](https://github.com/w3c/epubcheck)。本机已下载 5.3.0 到 `.cache/tools/epubcheck-5.3.0`。新机器下载该版本的发布 ZIP 解压到 `.cache/tools/`，或将 `EPUBCHECK_JAR` 指向已安装的 jar；需要 Java。

```bash
python scripts/publish.py build --all --profile all --epubcheck
# 单独校验已有书籍
python scripts/check_epub.py exports/layout-lab/layout-lab.epub
```

视觉回归脚本 `python scripts/browser_check.py` 需要 Playwright 与 Chromium（本机已有）。它检查书架、视觉手册、HTML 正文和 EPUB XHTML 在桌面及 390 px 手机宽度下的溢出、图片加载和字体状态，并保存截图到 `exports/visual-review/`。它不替代 Apple Books、微信读书等实际阅读器的实机测试。

## 定稿和印刷

这是可工作的出版排版基础，输出为 RGB 数字阅读 PDF，不宣称已经符合某家印厂的 PDF/X、CMYK、出血与装订标准。送印前应按实际印厂规格设置裁切、出血、纸张、颜色配置与书脊，完成全书人工校对，并确认图片使用权。正文排版与用于胶装的整张封面是不同交付物，目前封面是单页阅读封面。

自动检查无法判断论述质量，也不能完全代替对孤行、连续多页留白、超长标题、过高表格行和图表字号的人工复核。复杂表格应先整理信息结构。Mermaid、LaTeX 数学、Obsidian Dataview、笔记嵌入与块引用 `^id` 暂未转换；图表可先导出为 SVG 或高分辨率 PNG。

设计与实现依据见 [出版系统说明](design/publishing-system.md)。
