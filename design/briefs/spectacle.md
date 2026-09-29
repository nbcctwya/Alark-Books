# SPECTACLE / 欲望制造 · 摄影杂志版

方向：**奢侈品摄影杂志，大图、留白、精致字排**。2026-09-29 根据用户选择重新设计，替换此前每章整页黑红海报的结构。原稿与图片均未修改。

[实际设计预览](../previews/spectacle.html) · [改版前后对照](../../exports/spectacle-tension/index.html) · [作品书架](../../exports/index.html)

## 视觉结构

- **封面**：暖白纸面，放大的酒红 DESIRE 刊头跨越照片上沿。产品图偏向右侧纸边，中文书名以纸白色块叠入照片左下部；保留商品主体与底部署名。
- **色彩**：纸白 `#f9f6ef`、暖黑 `#24201e`、酒红 `#982b37`。鲜红主要来自照片本身，章节不再交替使用整页红黑底。
- **章节**：小型题签、放大章号、宋体标题与酒红色短引导语共同构成正文入口，随后直接开始正文。相同 subtitle / statement 只展示一次。
- **阅读**：首段与小节首段顶格，其后首行缩进；照片保持完整比例，图注跟随图片；引文放大并向右缩进，以酒红细线形成停顿；表格保留紧凑字排。
- **停顿**：开场和结尾各保留一页文字，两行使用不同字号与错位排列，十个章节无需额外海报隔页。

横版采用左侧刊头与书名、右侧大图的封面；A4 放大封面摄影。HTML 在手机上恢复单栏。EPUB 保持流式阅读，不将纸本页面作为正文图片。

## 配置与复用

```yaml
design: spectacle
cover_image: assets/my-book/cover.png
cover_alt: 图像的文字描述
series: MY JOURNAL
volume: '01'
cover_title_lines: [书名]
manifesto_lines: [开场第一句。, 开场第二句。]
manifesto_caption: 开场说明
end_lines: [结尾第一句。, 结尾第二句。]
```

章节的 `kicker`、`subtitle`、`statement` 可分别提供英文题签、引导语和短宣言。缺少短宣言时不预留空框。页眉与目录仍由原稿标题生成。示例书含十章，以虚构香氛品牌「无声剧场」讨论注意力、识别、定位、文案、接触点与交付；不声称该版式已经验证传播效果。

## 构建与实现

```bash
python scripts/publish.py build desire-manufacture --profile all --epubcheck
python scripts/previews/review_refinement.py --focus tension
```

模板：`website/templates/spectacle.html.j2`；样式：`website/styles/spectacle.css`、`spectacle-screen.css`、`spectacle-epub.css`。这次重写主题规则，未在旧的红黑章节布局上继续叠加覆盖。此前版本的演进见 [验证记录](../../docs/history/validation.md)。

## 素材边界

两幅产品摄影风格图像均为 AI 生成的虚构商品，来源见 `vault/assets/desire-manufacture/SOURCE.md`。原图为 1254 × 1254 像素。横版封面约 228 DPI，A4 封面约 197 DPI，低于项目 250 DPI 检查阈值，报告保留提醒；数字审阅可使用，正式大幅印刷需换入更高分辨率原片。
