# 项目组织

## 目录职责

```text
Alark-Books/
├── vault/                       Obsidian 原稿与素材，保留原有组织
├── design/                      视觉方案、HTML 原型、品牌标志与字体
├── docs/                        使用规范、系统说明、验证记录
├── website/
│   ├── templates/               PDF / HTML 模板
│   └── styles/                  PDF / HTML / EPUB 样式
├── scripts/
│   ├── publish.py               日常出版命令
│   ├── check_epub.py            EPUBCheck 命令
│   ├── alark_publishing/        内部出版引擎
│   ├── tests/                   自动测试
│   └── …                       字体、素材、预览和浏览器工具
├── exports/                     可重新生成的成品与报告，不提交 Git
├── publishing.yml              全局品牌与页面尺寸
├── environment.yml             Conda 环境与原生库
├── requirements.txt            出版运行依赖
└── requirements-dev.txt        可选浏览器检查依赖
```

`vault` 是内容源；`design` 解释视觉决策；`website` 实现这些设计；`scripts` 执行转换；`exports` 保存输出。书籍自己的标题、章节顺序和主题选择仍由原有 `book.yml` 管理，不再建立第二份书籍目录配置。

## 出版引擎

| 模块 | 职责 |
| --- | --- |
| `paths.py` | 仓库根目录、原稿、样式与模板路径；不依赖执行命令时的目录 |
| `themes.py` | 主题名称与 PDF / HTML 模板、CSS、EPUB CSS、横版分栏策略 |
| `cli.py` | 命令参数、构建流程、暂存发布、书架生成 |
| `manuscript.py` | Markdown、Obsidian 链接、章节与资源校验 |
| `epub.py` | EPUB 包、导航、字体裁剪与流式正文 |
| `preflight.py` | PDF / EPUB 检查与页面缩略图 |
| `epubcheck.py` | 调用本地 EPUBCheck |
| `runtime.py` | Conda 动态库与缓存环境准备 |

公开入口仍是 `python scripts/publish.py …` 和 `python scripts/check_epub.py …`。内部模块使用包内相对导入；环境准备只在命令入口执行，导入引擎不会重启 Python 进程。

## 添加设计

1. 在 `design/` 写下视觉方案，并更新设计索引。
2. 在 `website/styles/` 添加纸张、屏幕和 EPUB 样式；有需要时新增模板。
3. 在 `scripts/alark_publishing/themes.py` 登记资源与横版分栏策略。
4. 若有新的正文结构，如宣言页，在对应模板与 EPUB 组装逻辑中同时实现。
5. 经内容维护者授权后，在书籍配置中选择新主题，再检查三种页面与 EPUB。

当前摄影书刊和极简随笔共用 `editorial`，另有 `spectacle`、`business`、`investment`、`folio` 四个主题。颜色变量不等于完整设计语言。

## 读写边界与测试

常规构建读取 `vault`，输出写入 `exports`。`init` 和素材生成脚本会写入 `vault`，只有确实需要创建书籍或重建素材时才执行；详见 [脚本说明](../scripts/README.md)。

转换测试使用系统临时目录里的独立原稿、图片和配置，不依赖已有样书素材，也不在 `vault` 内创建临时文件。现有导出 EPUB 的检查只读 `exports`；尚未构建时显示跳过。主题资源测试检查登记的模板、样式是否存在。

本次组织调整保留 `website` 名称，避免仅为改名迁移所有资源引用。样式文件数量目前可直接浏览，继续按主题前缀分组；后续主题显著增加时再拆分主题子目录。


当前整体复核与后续重点见 [项目复核](project-review.md)。
