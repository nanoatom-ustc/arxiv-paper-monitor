# 📬 arXiv + APS 论文每日摘要

这是一个运行在 GitHub Actions 上的论文监控工具。它按关键词查询近期的 **arXiv 预印本**和 **APS（American Physical Society）期刊论文**，合并、去重后通过邮件发送每日摘要。

APS 数据通过 Crossref 公共 API 获取，并限定为 APS DOI 前缀 `10.1103` 下的期刊论文；无需 APS 或 Crossref API 密钥。

## 功能

- 同时查询 arXiv 与 APS，也可单独启用任一数据源
- arXiv 分区过滤，以及可选的 APS 期刊过滤
- 多数据源统一排序、DOI/ID 去重和全局结果数量限制
- HTML 与纯文本邮件
- GitHub Actions 定时运行或手动触发

## 配置

Fork 仓库后，在 `Settings → Secrets and variables → Actions` 中配置。

### Secrets（必填）

| Name | 说明 |
|---|---|
| `EMAIL_SENDER` | 发件邮箱（当前支持 QQ 邮箱、163 邮箱） |
| `EMAIL_PASSWORD` | SMTP 授权码，不是邮箱登录密码 |
| `RECIPIENT_EMAIL` | 收件邮箱 |

### Variables

| Name | 默认值 | 说明 |
|---|---|---|
| `SEARCH_KEYWORDS` | 工作流内置关键词 | 英文逗号分隔；同时用于 arXiv 与 APS |
| `SEARCH_SOURCES` | `arxiv,aps` | 可选 `arxiv`、`aps`，英文逗号分隔 |
| `SEARCH_CATEGORIES` | 空 | arXiv 分区代码，英文逗号分隔；仅影响 arXiv |
| `APS_JOURNALS` | 空 | APS 期刊名称或常用缩写，英文逗号分隔；空表示全部 APS 期刊 |
| `FETCH_DAYS` | `2` | 查询最近几天；`0` 表示不添加日期限制 |
| `MAX_RESULTS` | `20` | 合并所有数据源后邮件中最多保留的论文数 |
| `CROSSREF_MAILTO` | 空 | 可选联系邮箱，建议设置以遵循 Crossref polite-pool 规范 |

配置示例：

```ini
SEARCH_KEYWORDS=Rydberg atom,optical tweezers,nanophotonics
SEARCH_SOURCES=arxiv,aps
SEARCH_CATEGORIES=physics.atom-ph,quant-ph,physics.optics
APS_JOURNALS=Physical Review Letters,Physical Review A,PRX Quantum
FETCH_DAYS=2
MAX_RESULTS=30
CROSSREF_MAILTO=your-email@example.com
```

常用 APS 缩写（例如 `PRL`、`PRA`、`PRB`、`PRX`）也可用于 `APS_JOURNALS`。期刊过滤采用不区分大小写的名称包含匹配或期刊名首字母缩写匹配。

如果希望保持升级前的纯 arXiv 行为，只需设置：

```ini
SEARCH_SOURCES=arxiv
```

## 手动测试

进入仓库 `Actions` 页面，选择 **Daily Paper Digest**，点击 **Run workflow**。定时任务默认每天 UTC 01:00（北京时间 09:00）运行，可在 `.github/workflows/arxiv_daily.yml` 中修改 cron。

本地运行时可在项目根目录创建不提交到 Git 的 `.env` 文件，写入同名配置，然后执行：

```bash
pip install -r requirements.txt
python main.py
```

运行测试：

```bash
python -m unittest discover -s tests -v
```

测试会模拟 Crossref 响应，不访问外部网络。

## 项目结构

```text
arxiv-paper-monitor/
├── .github/workflows/arxiv_daily.yml  # 定时任务
├── main.py                             # 多数据源聚合入口
├── arxiv_fetcher.py                    # arXiv 查询与归一化
├── aps_fetcher.py                      # APS/Crossref 查询与归一化
├── paper_utils.py                      # 通用摘要格式
├── email_sender.py                     # 邮件生成与发送
├── config.py                           # 环境变量配置
├── tests/test_aps_fetcher.py           # APS 数据源测试
└── requirements.txt
```

## APS 数据说明

- 覆盖范围取决于 Crossref 中 DOI 前缀 `10.1103` 的元数据，目标为 APS 注册的期刊文章。
- Crossref 并非每条记录都提供摘要或 PDF 直链；此时邮件仍会给出 DOI 文章链接，并明确提示摘要不可用。
- 查询异常只会跳过 APS 结果并记录日志，arXiv 查询和邮件流程仍可继续，反之亦然。

## License

MIT

