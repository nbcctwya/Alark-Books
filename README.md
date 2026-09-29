# AIark / Alark Books

在 Obsidian 中写作，用 Markdown 生成具有纸本风格的 PDF、可调整字号的 EPUB 和 HTML 阅读版。

## 从这里开始

- **写书、导出**：[安装与检查](docs/setup.md) · [写作规范](docs/writing-guide.md) · [书籍配置](docs/book-configuration.md)
- **选设计、看样张**：[设计资料索引](design/README.md) · [六款设计对照](design/previews/collection.html)
- **维护项目**：[项目组织](docs/architecture.md) · [脚本说明](scripts/README.md) · [全部文档](docs/README.md)

本地成品入口为 `exports/index.html`；`website/index.html` 也会打开同一书架。HTML 设计预览需要本地打开，实际书页图片需先构建。GitHub 保存原稿、代码与设计资料，`exports/` 不入库。

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

`build --all` 会导出所有含 `book.yml` 的书籍目录，目前为下方列出的六本样书。现有 `vault/books/ai-media` 保持原样，尚未配置 `book.yml`，因此不会参与自动构建。

## 目录职责

```text
vault/               Obsidian 原稿与素材
design/             设计资料（详见下方）
website/             实际模板与 PDF / HTML / EPUB 样式
scripts/             出版入口、引擎、测试、预览与素材工具
docs/                使用文档与历史记录
exports/             生成的成品、样张和报告，不入 Git
```

`design/briefs/` 放方案说明，`design/previews/` 放 HTML 设计预览，品牌与字体仍在 `design/brand/`、`design/fonts/`。全局品牌和页面尺寸配置为 `publishing.yml`，每本书的配置在其 `book.yml` 中。

## 六款设计样书

项目目前包含六本独立样书，覆盖摄影书刊、极简随笔、奢华影像、商业蓝图、投资年鉴和图片为主的摄影集。整体以纸本书籍与杂志为视觉方向，每本均可生成竖版、横版、A4 PDF，以及流式 EPUB 和 HTML 阅读版。

| 样书 / 原稿 | 章节 | 视觉方向 | `design` 配置 |
| --- | --- | --- | --- |
| [内容的复利](vault/books/layout-lab) | 11 | 摄影书刊：宋体、自然纸白、摄影图版 | `editorial`，摄影封面 |
| [留一点时间思考](vault/books/field-notes) | 10 | 极简随笔：纯字封面、细线与留白 | `editorial`，纯字封面 |
| [欲望制造](vault/books/desire-manufacture) | 10 | 奢华影像：暖白纸面、酒红刊头、大幅摄影 | `spectacle` |
| [生意的结构](vault/books/business-architecture) | 10 | 商业蓝图：钴蓝、工程网格、流程图与经营算式 | `business` |
| [穿越波动](vault/books/through-volatility) | 10 | 投资年鉴：深绿、米纸色、宋体、细金线与数据图版 | `investment` |
| [岸与间](vault/books/shore-and-space) | 24 | 影像札记：纯白纸面、完整画幅、双图、组照与满版 | `folio` |

六款视觉方案对应五个代码主题：摄影书刊与极简随笔共用 `editorial`，通过封面、素材与内容节奏形成不同表达。商业和投资样书中的案例、图表采用明确标注的虚构数据或数学演示。

优先打磨《内容的复利》的长篇阅读和 FOLIO 的摄影编排。当前页数与内容见 [长篇样书](docs/longform-samples.md)、[FOLIO 说明](design/briefs/folio.md)，最新纸本调整见 [内页打磨](design/briefs/editorial-refinement.md)。

构建后运行 `python scripts/previews/review_refinement.py`，可查看 [真实书页对照](exports/refinement-review/index.html)。其他样张生成命令见 [脚本说明](scripts/README.md)。

最新审美精修：运行 `python scripts/previews/review_refinement.py --focus aesthetics` 后查看 [《内容的复利》与《欲望制造》书页对照](exports/aesthetic-review/index.html)。

《欲望制造》采用奢侈品摄影杂志方向，以偏置大图、叠压书名和字号反差增强构图张力，查看 [新版设计](design/previews/spectacle.html) 与 [改版前后对照](exports/spectacle-tension/index.html)。
