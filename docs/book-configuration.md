# 书籍配置与输出规格

[文档导航](README.md) · [写作规范](writing-guide.md)

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

## 定稿和印刷

这是可工作的出版排版基础，输出为 RGB 数字阅读 PDF，不宣称已经符合某家印厂的 PDF/X、CMYK、出血与装订标准。送印前应按实际印厂规格设置裁切、出血、纸张、颜色配置与书脊，完成全书人工校对，并确认图片使用权。正文排版与用于胶装的整张封面是不同交付物，目前封面是单页阅读封面。

自动检查无法判断论述质量，也不能完全代替对孤行、连续多页留白、超长标题、过高表格行和图表字号的人工复核。复杂表格应先整理信息结构。Mermaid、LaTeX 数学、Obsidian Dataview、笔记嵌入与块引用 `^id` 暂未转换；图表可先导出为 SVG 或高分辨率 PNG。

设计与实现依据见 [出版系统说明](../docs/publishing-system.md)。
