# 商业蓝图与投资年鉴

这两套设计分别用于《生意的结构》和《穿越波动》。与摄影书刊、极简随笔、奢华传播一起，构成五款样书方向。[并排比较](five-designs.html)。前两款共用 editorial 引擎，通过封面、素材和内容节奏形成不同表达；后三款具有独立主题样式。

## 04 / 商业蓝图

- 气质：工程手册、商业案例册。用结构与关系传递清晰感。
- 钴蓝 `#1545ba`、冷白 `#fbfcf8`、墨蓝 `#13234a`、少量橙色 `#db652e`。
- 黑体正文，左对齐章标题，右侧大章号；粗蓝线建立层级，橙色细线强调本章命题。
- 封面使用原创工程网格，内页采用流程图、经营算式、整块比较表。图表直接参与叙述。
- 横版采用双栏文字与通栏图表，竖版以单栏阅读为主；EPUB 保留色彩与标题关系并允许重排。
- 样书四章：价值主张、交付流程、单笔经营结构、经营反馈。所有案例和数值为虚构。

在 `book.yml` 中设置 `design: business`，建议封面标题用 `cover_title_lines` 手动控制换行。

## 05 / 投资年鉴

- 气质：投资札记、档案年鉴。以稳定的阅读节奏承载需要反复核对的内容。
- 深绿 `#25483e`、米纸色 `#f4f0e6`、旧金色 `#a67d3f`。
- 宋体正文与居中章标题，细金线、克制的小章号、浅绿表头；批注和来源置于正文附近。
- 封面用抽象时间路径；内页有价值路径与回撤组合图，以及费用演算图。图表不使用真实行情。
- 横版双栏与大图版，竖版单栏；EPUB 使用流式图表与可点击注释。
- 样书四章：时间约束、回撤、费用、决策日志。概念来源见章末 Investor.gov 链接；参数与推导见素材数据文件。

在 `book.yml` 中设置 `design: investment`。图表必须标明数据性质、单位、假设与来源。

## 重建与复用

```bash
conda activate webproj
python scripts/make_finance_samples.py
python scripts/publish.py build business-architecture --profile all --epubcheck
python scripts/publish.py build through-volatility --profile all --epubcheck
python scripts/make_design_boards.py
```

样书图形由脚本生成 SVG，中文字体转换成轮廓，放大不产生位图锯齿。素材目录含来源说明，投资目录另有 `data.json`。无须联网即可重建图形。

样式位于 `website/styles/business*.css`、`investment*.css`；PDF/HTML 共用 `website/templates/studio.html.j2` 的语义骨架，字体、构图与表格规则分别定义。PDF 是数字阅读版，正式印刷仍需按印厂要求准备出血、颜色和 PDF/X 文件。
