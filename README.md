# AIark / Alark Books

在 Obsidian 中写作，用一份 Markdown 生成带封面、目录、章节页、图注、页眉页脚的 PDF，以及可调整字号的 EPUB。

## 六款设计样书

项目目前包含六本独立样书，覆盖摄影书刊、极简随笔、奢华传播、商业蓝图、投资年鉴和图片为主的摄影集。整体以纸本书籍与杂志为视觉方向，每本均可生成竖版、横版、A4 PDF，以及流式 EPUB 和 HTML 阅读版。

| 样书 / 原稿 | 章节 | 视觉方向 | `design` 配置 |
| --- | --- | --- | --- |
| [内容的复利](vault/books/layout-lab/) | 11 | 摄影书刊：宋体、自然纸白、摄影图版 | `editorial`，摄影封面 |
| [留一点时间思考](vault/books/field-notes/) | 10 | 极简随笔：纯字封面、细线与留白 | `editorial`，纯字封面 |
| [欲望制造](vault/books/desire-manufacture/) | 10 | 奢华传播：黑红银、巨幅字排、广告摄影 | `spectacle` |
| [生意的结构](vault/books/business-architecture/) | 10 | 商业蓝图：钴蓝、工程网格、流程图与经营算式 | `business` |
| [穿越波动](vault/books/through-volatility/) | 10 | 投资年鉴：深绿、米纸色、宋体、细金线与数据图版 | `investment` |
| [岸与间](vault/books/shore-and-space/) | 24 | 影像札记：纯白纸面、完整画幅、双图、组照与满版 | `folio` |

六款视觉方案对应五个代码主题：摄影书刊与极简随笔共用 `editorial`，通过封面、素材与内容节奏形成不同表达。商业和投资样书中的案例、图表采用明确标注的虚构数据或数学演示。

**在 GitHub 阅读设计说明：** [纸本与摄影方向](design/editorial-direction.md) · [奢华传播](design/spectacle.md) · [商业蓝图与投资年鉴](design/business-investment.md) · [FOLIO 摄影集](design/folio.md) · [写作规范](docs/writing-guide.md)

**在本地查看成品：** 完成下方构建后，用浏览器打开 `exports/index.html` 查看作品书架，打开 `design/five-designs.html` 并排比较六款设计。`exports/visual-review/five-designs.png` 是原有五张实际 PDF 封面的组合预览；摄影集预览见 `design/folio.html`。

> GitHub 仓库保存原稿、代码、设计说明和素材。`exports/` 下的 PDF、EPUB、HTML、截图与报告均为本地构建产物，不提交 Git；设计 HTML 中引用的封面和样张也需要先构建，GitHub 文件页面不会直接呈现完整的本地预览。

主力书系正在围绕《内容的复利》深化，最新改动见 [内页打磨说明](design/editorial-refinement.md)。本地构建后执行 `python scripts/make_editorial_review.py` 可生成实际 PDF 对页预览。

## 摄影集样书

**FOLIO /《岸与间》扩篇版**：24 章、20 张 AI 生成影像，竖版 **31 页**、横版 **30 页**、A4 **28 页**。新增黑白、朱红、暖橙、霓虹、青绿、粉彩、运动模糊与蓝晒风格；提供单图、双图、四图组照、图文随笔、满版五种版式。构建后运行 `python scripts/make_folio_review.py`，打开 [实际书页预览](design/folio.html)。大图页保留素材分辨率提醒；原图与生成提示词见 [素材来源](vault/assets/shore-and-space/SOURCE.md)。

## 长篇排版实验版

原有五本已扩展为 **51 章、约 5.18 万中文字符**，竖版分别为 **42 / 38 / 50 / 37 / 40 页**。包含密集正文、摄影图版、访谈、案例、跨页长表与注释，新增 13 张原创矢量图。详见 [扩篇说明与页数](docs/longform-samples.md)。

构建后运行 `python scripts/review_longform.py`，打开本地 `exports/longform-review/index.html`，可以直接比较各书新增的密集页与图文页。

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

`build --all` 会导出所有含 `book.yml` 的书籍目录，目前为上表中的六本样书。现有 `vault/books/ai-media` 保持原样，尚未配置 `book.yml`，因此不会参与自动构建。

## 目录约定

| 目录 / 文件 | 作用 |
| --- | --- |
| `vault/books/<slug>/` | 每个目录一本书，Markdown 正文 + `book.yml` |
| `vault/assets/` | Obsidian 图片、图表与其他写作素材 |
| `design/` | 视觉方案、设计原型、标志与字体授权 |
| `docs/` | 项目组织、出版系统、写作规范与验证记录 |
| `website/styles/` | PDF、HTML 与 EPUB 的样式代码 |
| `website/templates/` | 书籍与作品书架的 HTML 模板 |
| `scripts/` | 面向使用者的构建、校验和素材工具入口 |
| `scripts/alark_publishing/` | 出版引擎：解析、主题登记、PDF / EPUB 构建与检查 |
| `scripts/tests/` | 使用系统临时目录的转换测试与资源检查 |
| `exports/` | 生成的书、网页、封面、页面联系表与检查报告；不提交 Git |
| `publishing.yml` | 全局 IP 名称、作者默认值、页面规格 |

完整目录职责与扩展方式见 [项目组织](docs/architecture.md)，当前检查结果见 [项目整体复核](docs/project-review.md)，命令读写范围见 [脚本说明](scripts/README.md)，设计资料索引见 [设计目录](design/README.md)。

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
design: editorial  # editorial / spectacle / business / investment / folio
theme: vermilion    # 基础主题色，可选 vermilion / forest
cover_image: assets/editorial/coastal-study.png
cover_alt: 海岸与自然光
chapters:
  - 01-observe.md
  - 02-system.md
  - 03-business.md
  - 04-review.md
  - 05-specimens.md
```

`chapters` 是唯一的章节顺序来源。提纲、草稿、参考笔记只有被列入时才会进入成书。添加、删去或调整章节，只需修改该列表。`init` 会生成稳定的 UUID，不覆盖已存在的目录。标题必填，其他字段参见样书；日期建议用引号。

`design` 决定设计语言，`theme` 是基础配色字段；`spectacle`、`business`、`investment`、`folio` 在各自样式中定义专属色板。`editorial` 不设置 `cover_image` 时使用纯字封面；封面图支持 PNG、JPEG、SVG，路径相对于 `vault/`。新建书籍请使用 `init` 生成自己的编号，不复用示例 UUID。

其他主题还使用 `cover_title_lines` 控制封面标题换行，以及章节 frontmatter 中的 `kicker`、`subtitle`、`statement`。完整配置可直接参考上表中各书的 `book.yml` 与正文文件。

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
python scripts/publish.py build --all --profile all
python scripts/make_design_boards.py
python scripts/make_editorial_review.py
python scripts/review_longform.py
python scripts/make_folio_review.py
```

仓库已包含六本样书所需的素材，常规构建无需重新生成。修改图表后，可运行 `python scripts/make_finance_samples.py` 重建商业与投资 SVG，或运行 `python scripts/make_samples.py` 重建基础图文测试素材，再构建对应书籍。`make_design_boards.py` 依赖五本书已经生成的封面与两本新书的竖版 PDF。

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

视觉回归脚本需先完成六本书的构建和预览图生成，并安装 Playwright 的 Chromium：

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python scripts/browser_check.py
```

`python scripts/browser_check.py` 使用 Playwright 与 Chromium（本机已有）。它检查书架、六款设计对照、视觉手册、HTML 正文和 EPUB XHTML 在桌面及 390 px 手机宽度下的溢出、图片加载和字体状态，并保存截图到 `exports/visual-review/`。它不替代 Apple Books、微信读书等实际阅读器的实机测试。

当前十七项测试通过，转换用例均在系统临时目录运行；视觉检查覆盖 76 个浏览器页面与视口组合。原有五本书的十五份 PDF 无检查提醒，六本 EPUBCheck 均零错误、零警告。新增摄影集的三份 PDF 无结构错误，保留大图分辨率提醒。详细记录见 [验证记录](docs/validation.md)。

## 定稿和印刷

这是可工作的出版排版基础，输出为 RGB 数字阅读 PDF，不宣称已经符合某家印厂的 PDF/X、CMYK、出血与装订标准。送印前应按实际印厂规格设置裁切、出血、纸张、颜色配置与书脊，完成全书人工校对，并确认图片使用权。正文排版与用于胶装的整张封面是不同交付物，目前封面是单页阅读封面。

自动检查无法判断论述质量，也不能完全代替对孤行、连续多页留白、超长标题、过高表格行和图表字号的人工复核。复杂表格应先整理信息结构。Mermaid、LaTeX 数学、Obsidian Dataview、笔记嵌入与块引用 `^id` 暂未转换；图表可先导出为 SVG 或高分辨率 PNG。

设计与实现依据见 [出版系统说明](docs/publishing-system.md)。
