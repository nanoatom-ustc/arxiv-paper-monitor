# 📬 arXiv、APS、Nature、Science 与 Optica 论文每日摘要

这是一个运行在 GitHub Actions 上的论文监控工具。它按关键词查询近期的 arXiv 预印本，以及 APS、Nature Portfolio、Science/AAAS 和 Optica Publishing Group 期刊论文，合并、去重后通过邮件发送每日摘要。

期刊数据来自 Crossref 公共 API：APS 使用 DOI 前缀 `10.1103`，Nature Portfolio 使用 `10.1038`，Science/AAAS 使用 `10.1126`，Optica Publishing Group 使用 `10.1364`。无需出版商或 Crossref API Key。

## 默认检索范围

- arXiv：全部分区，可通过 `SEARCH_CATEGORIES` 限制。
- APS：全部 APS 期刊，但默认排除 **Physical Review B（PRB）** 和 **Physical Review D（PRD）**。
- Nature：仅 Nature、Nature Physics、Nature Photonics、Nature Communications、npj Quantum Information 和 Nature Reviews Physics。
- Science：仅 Science 和 Science Advances。
- Optica：仅 Optica 和 Optics Express。

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
| `SEARCH_SOURCES` | `arxiv,aps,nature,science,optica` | 启用的数据源 |
| `SEARCH_CATEGORIES` | 空 | arXiv 分区代码，仅影响 arXiv |
| `APS_JOURNALS` | 空 | APS 期刊允许列表；空表示除排除项外的全部 APS 期刊 |
| `APS_EXCLUDE_JOURNALS` | `Physical Review B,Physical Review D,PRB,PRD` | APS 期刊排除列表 |
| `NATURE_JOURNALS` | 6 本指定期刊 | Nature 期刊允许列表 |
| `SCIENCE_JOURNALS` | `Science,Science Advances` | Science 期刊允许列表 |
| `OPTICA_JOURNALS` | `Optica,Optics Express` | Optica Publishing Group 期刊允许列表 |
| `FETCH_DAYS` | `2` | 查询最近几天；`0` 表示不添加日期限制 |
| `MAX_RESULTS` | `20` | 合并所有数据源后最多保留的论文数 |
| `CROSSREF_MAILTO` | 空 | 可选联系邮箱，建议设置以遵循 Crossref polite-pool 规范 |

示例：

```ini
SEARCH_KEYWORDS=Rydberg atom,optical tweezers,nanophotonics
SEARCH_SOURCES=arxiv,aps,nature,science,optica
SEARCH_CATEGORIES=physics.atom-ph,quant-ph,physics.optics
APS_EXCLUDE_JOURNALS=Physical Review B,Physical Review D,PRB,PRD
NATURE_JOURNALS=Nature,Nature Physics,Nature Photonics,Nature Communications,npj Quantum Information,Nature Reviews Physics
SCIENCE_JOURNALS=Science,Science Advances
OPTICA_JOURNALS=Optica,Optics Express
FETCH_DAYS=2
MAX_RESULTS=30
CROSSREF_MAILTO=your-email@example.com
```

期刊过滤采用不区分大小写的精确名称匹配，也支持常见首字母缩写。这样 `Nature` 不会误匹配 Nature Materials，`Science` 不会误匹配 Science Robotics，`Optica` 也不会放入其他 Optica Publishing Group 期刊。

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
├── optica_fetcher.py
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
