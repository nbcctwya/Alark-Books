# SPECTACLE / 欲望制造

第三套独立设计语言：**奢侈品广告 × 高冲击编辑设计**。样书位于 `vault/books/desire-manufacture`，包含四章：先被看见、让人记住、值得渴望、兑现承诺。

[视觉方案](spectacle.html) · [作品书架](../exports/index.html)

## 视觉机制

黑、红、银是这一套视觉的主要材料。黑底让金属反光与丝带成为画面主角，红页承担明确的停顿，暖白正文页让读者进入解释与论述。

封面以大字号中文书名与 DESIRE 字排形成双重重心，局部文字与图像交叠。章节开启采用独立整页、巨幅编号、英文题签与一句短宣言。读者翻页时，能分辨宣传式画面、章节转换与正文阅读的不同节奏。

大图、短句与稳定的视觉线索被当作传播设计的假设进行演示。正文用虚构品牌「无声剧场」贯穿案例，讨论吸引注意、建立识别、表达向往与兑现承诺；没有把某一种版式宣称为必然带来传播效果的公式。

## 复用

在书籍 `book.yml` 中指定：

```yaml
design: spectacle
cover_image: assets/my-book/cover.png
cover_alt: 图像说明
cover_credit: 图像作者与来源
cover_title_lines: [欲望, 制造]
manifesto_lines: [先让人停下。, 再值得留下。]
manifesto_caption: ATTENTION IS THE ENTRANCE.
end_lines: [制造期待。, 兑现期待。]
```

章节 YAML 可以增加：

```yaml
subtitle: 为第一眼设置一个鲜明的理由。
kicker: ATTENTION
statement: 没有停顿，就没有下一句。
```

`design` 与原有的强调色 `theme` 分开。未指定 `design` 时继续使用 `editorial`；因此《内容的复利》的纸本摄影风格可以继续单独使用。

当前样式适合短书名、短章节名与精炼宣言。更长的文字需要调整独立样式中的字号并检查各开本，避免把大字当成无条件适配所有内容的规则。

## 文件

- `website/templates/spectacle.html.j2`：封面、宣言、章节开场与收尾。
- `website/styles/spectacle.css`：纸面色彩、巨幅字排、横竖版规则。
- `website/styles/spectacle-screen.css`：手机与桌面阅读适配。
- `website/styles/spectacle-epub.css`：流式 EPUB 样式。

EPUB 保留图像、色彩、章标题、宣言与章节内容；巨幅整页海报转换为可重排文字，便于读者调整字号。

## 图像

两张图像均由内置 imagegen 生成，原图与完整提示词已保存到 [素材来源记录](../vault/assets/desire-manufacture/SOURCE.md)：

- [chrome-desire.png](../vault/assets/desire-manufacture/chrome-desire.png)：镜面银色瓶身、猩红丝带、黑色舞台。
- [crystal-impact.png](../vault/assets/desire-manufacture/crystal-impact.png)：晶体切面、红色漆面、液态金属反光。

图像中的物品为虚构概念，并非真实品牌广告。当前黑色与红色大面积页面更适合数字阅读；实体制作时可根据纸张、油墨和装订要求调整。
