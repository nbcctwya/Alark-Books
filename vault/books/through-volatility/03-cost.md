---
subtitle: 给一个经常被省略的变量留出位置。
kicker: COST OF OWNERSHIP
statement: 小数点后面的数字，也属于结果的一部分。
---
# 费用怎样进入时间

费用可以在交易时发生，也可能持续按期收取。Investor.gov 的教育材料提醒读者，费用会减少留在投资中的金额，因此比较成本时应理解收费方式与频率。[^fees]

本章设计一个纯数学例子：初始值为 100，每年费用前增长固定为 4%，在每年末按当时资产值扣除费用，持续 20 年。我们分别代入 0%、0.5% 和 1.5% 三种年费率。

![[assets/through-volatility/fee-drag.svg|图 3-1　假设路径下的费用演示。所有参数均为设计样例，不是实际收益数据。]]

## 把假设放在图旁边

计算式为：100 × [1.04 ×（1 − 年费率）] 的 20 次方。模型没有纳入税费、交易成本、追加资金、取款或收益波动，也没有模拟具体产品。参数写在图旁边，读者才能知道结论依赖什么。

在这个给定模型中，不同费用会形成不同的期末值。这并不意味着现实中只需比较一个费率；产品提供什么、风险来自哪里、还有哪些费用，都需要进一步阅读资料。

> [!note] 阅读注记
> 图表数据由脚本按上述公式计算，输入和输出保存在素材目录的 data.json，便于复查。

[^fees]: 参考：Investor.gov，[How Fees and Expenses Affect Your Investment Portfolio](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/updated)。查阅于 2026-09-27。
