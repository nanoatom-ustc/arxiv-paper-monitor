# 📬 arXiv、APS、Nature 与 Science 论文每日摘要

这是一个运行在 GitHub Actions 上的论文监控工具。它按关键词查询近期的 arXiv 预印本，以及 APS、Nature Portfolio 和 Science/AAAS 期刊论文，合并、去重后通过邮件发送每日摘要。

期刊数据来自 Crossref 公共 API：APS 使用 DOI 前缀 `10.1103`，Nature Portfolio 使用 `10.1038`，Science/AAAS 使用 `10.1126`。无需出版商或 Crossref API Key。

## 默认检索范围

- arXiv：全部分区，可通过 `SEARCH_CATEGORIES` 限制。
- APS：全部 APS 期刊，但默认排除 **Physical Review B（PRB）** 和 **Physical Review D（PRD）**。
- Nature：`10.1038` 前缀下的 Nature Portfolio 期刊及子刊。
- Science：`10.1126` 前缀下的 Science/AAAS 期刊及子刊，例如 Science Advances、Science Robotics、Science Immunology、Science Signaling 和 Science Translational Medicine。

不同数据源的结果会统一排序、按 DOI/ID 去重，最后共同应用 `MAX_RESULTS` 限制。

## GitHub 配置

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
| `SEARCH_KEYWORDS` | 工作流内置关键词 | 英文逗号分隔，作用于所有数据源 |
| `SEARCH_SOURCES` | `arxiv,aps,nature,science` | 启用的数据源 |
| `SEARCH_CATEGORIES` | 空 | arXiv 分区代码，仅影响 arXiv |
| `APS_JOURNALS` | 空 | APS 期刊允许列表；空表示除排除项外的全部 APS 期刊 |
| `APS_EXCLUDE_JOURNALS` | `Physical Review B,Physical Review D,PRB,PRD` | APS 期刊排除列表 |
| `NATURE_JOURNALS` | 空 | Nature 期刊允许列表；空表示全部 Nature Portfolio 期刊 |
| `SCIENCE_JOURNALS` | 空 | Science 期刊允许列表；空表示全部 Science/AAAS 期刊 |
| `FETCH_DAYS` | `2` | 查询最近几天；`0` 表示不添加日期限制 |
| `MAX_RESULTS` | `20` | 合并所有数据源后最多保留的论文数 |
| `CROSSREF_MAILTO` | 空 | 可选联系邮箱，建议设置以遵循 Crossref polite-pool 规范 |

示例：

```ini
SEARCH_KEYWORDS=Rydberg atom,optical tweezers,nanophotonics
SEARCH_SOURCES=arxiv,aps,nature,science
SEARCH_CATEGORIES=physics.atom-ph,quant-ph,physics.optics
APS_EXCLUDE_JOURNALS=Physical Review B,Physical Review D,PRB,PRD
NATURE_JOURNALS=Nature,Nature Physics,Nature Photonics,Nature Communications
SCIENCE_JOURNALS=Science,Science Advances,Science Robotics
FETCH_DAYS=2
MAX_RESULTS=30
CROSSREF_MAILTO=your-email@example.com
```

期刊过滤支持不区分大小写的名称包含匹配和常见首字母缩写。不要配置 `NATURE_JOURNALS` 或 `SCIENCE_JOURNALS`，即可覆盖对应出版集团的全部主刊与子刊。

## 手动运行和测试

进入仓库 `Actions` 页面，选择 **Daily Paper Digest**，点击 **Run workflow**。定时任务默认每天 UTC 01:00（北京时间 09:00）运行。

本地运行：

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
├── .github/workflows/arxiv_daily.yml
├── main.py
├── arxiv_fetcher.py
├── crossref_fetcher.py
├── aps_fetcher.py
├── nature_fetcher.py
├── science_fetcher.py
├── paper_utils.py
├── email_sender.py
├── config.py
├── tests/test_aps_fetcher.py
└── requirements.txt
```

## 数据说明

- 覆盖范围取决于各出版商在 Crossref 中登记的元数据及 DOI 前缀。
- Crossref 并非每条记录都提供摘要或 PDF 直链；邮件仍会提供 DOI 文章链接。
- 某个数据源查询失败时会记录日志并继续处理其他数据源。
- Science Partner Journals 中使用其他 DOI 前缀的合作期刊不属于 `10.1126` 核心 Science/AAAS 范围。

## License

MIT

