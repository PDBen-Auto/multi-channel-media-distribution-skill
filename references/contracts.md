# 本地数据合同与操作命令

## 范围

`campaign.py`只管理离线记录。不会生成媒体、登录、上传、读网页或自动发布。它执行结构校验与文件指纹校验；实际读原始证据、确认账号、审查内容和遵守授权仍由执行者负责。填写true并不制造事实。

## Brief v1

`examples/neutral-product/brief.json`可直接作为合成演练输入。真实使用前另存新JSON并填写真实资料，`evidenceMode`改为`real`。只复制必要的业务事实，不复制私人聊天、凭据和登录态。

| 字段 | 类型 / 必需 | 意义、来源、校验 |
|---|---|---|
| schemaVersion | integer=1 / 是 | 本地合同版本 |
| campaignId | string / 是 | 小写kebab-case，稳定交付标识 |
| evidenceMode | real或synthetic / 是 | 整个campaign证据性质；不能混用合成记录声称真实执行 |
| goal / audience / language / cta | nonempty string / 是 | 目标、受众假设/证据、输出语言、希望读者做什么；由当前需求及资料确定 |
| channels | unique array / 是 | 受支持平台名的子集，同时决定报告顺序；区分大小写 |
| facts | array / 是 | 至少一项`claim`与`source`字符串；来源可以是获准文件+日期或URL，助手仍需阅读 |
| unknowns | array / 是 | 未知项，可空数组，不能把未知写成false/0 |
| permissions | object / 是 | 与channels键完全一致；逐项`prepareEditor:boolean`、`submitActor:none/user/assistant`、`authorizationSource:string` |

本地only权限示例：`{"prepareEditor":false,"submitActor":"none","authorizationSource":"Local drafting only"}`。有外写权限时必须给当前授权来源的简述/私有引用，不粘贴原始通信。旧示例不构成真实权限。

初始化固定brief的SHA256。发生新业务/权限基线时保留旧目录，新建经过审阅的campaign版本并引用旧来源；本轻量工具不提供带旧事件的自动重基线功能。不要手改brief/state绕过校验。

## Event v1

每个事件一个JSON，`record --event`读入。本工具在state中追加事件，按channel维护哈希链，使用写锁和原子替换。事件文件本身可放本campaign的`work/`，但不能在追加后改变已引用证据。

```json
{
  "id": "linkedin-manual-001",
  "at": "2026-01-01T12:00:00+00:00",
  "status": "assets_waiting_manual",
  "actor": "none",
  "summary": "Approved copy is ready locally; file selection is still required.",
  "nextAction": "User selects the approved image; operator then checks preview.",
  "checks": {},
  "evidence": [{"path": "work/evidence/manual-handoff.md", "sha256": "REPLACE_WITH_ACTUAL_64_HEX_SHA256"}]
}
```

这是格式示意，哈希占位符**不能执行通过**。用下面命令获取真实字节哈希，再填写；路径是campaign根内实际文件，采用`/`分隔，不接受绝对路径、`..`、冒号或逃逸链接：

```sh
python -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('campaign-a/work/evidence/manual-handoff.md').read_bytes()).hexdigest())"
python scripts/campaign.py record --campaign ./campaign-a --channel LinkedIn --event ./reviewed-event.json
```

| 字段 | 要求 |
|---|---|
| id | 本campaign唯一非空字符串；重复拒绝，不隐式覆盖或再次追加 |
| at | 实际观察/记录时间ISO8601，必须含时区；工具不提供可信时间戳认证 |
| status | 见浏览器参考中的状态；初始queued由工具生成 |
| actor | none/user/assistant；提交状态需与brief获准提交者一致；cancelled_by_user必须为user |
| summary | 证据支持的非空结论，合成演练明确synthetic |
| nextAction | blocked、cancelled_by_user、assets_waiting_manual必需；取消可写“保持取消，不重试” |
| checks | 对象，未检查不要填true；具体放行键见下文 |
| evidence | 至少一项campaign内文件path + 实际sha256；不能只是网页URL |
| postId / url | 核验层级需实际postId；public_verified另需https URL。演练用明确synthetic标识 |

不要输入`previousEventSha256`/`eventSha256`，由工具生成。证据文件可保存最小必要观察记录、核查结果或已脱敏截图；不保存cookie、令牌、密码、session dump或无关私有正文。

## 放行检查

- `editor_ready_unpublished`：brief允许prepareEditor；checks里的`accountVerified`、`destinationVerified`、`rulesRead`、`duplicatesChecked`、`mediaVerified`、`copyVerified`、`previewVerified`、`disclosuresResolved`、`reviewPassed`全部为布尔true。
- `submitted_processing` / `submission_unknown`：前状态为ready；actor必须是获准的user或assistant。未知状态恢复时必须检查`reconciledPriorAttempt:true`，同时遵循恢复结论。
- `manager_verified` / `account_post_verified` / `public_verified`：此前有提交阶段或核验阶段；分别需要`managerRecordVerified` / `accountPostVerified` / `publicPageVerified:true`和实际postId。公开层需实际https URL。
- 已取消不可在原campaign静默恢复。已提交不能退回content_candidate/manual再绕过查重。已核验不能直接退回ready重复发。
- blocked或submission_unknown后如果有旧提交历史，重新ready需`reconciledPriorAttempt:true`及`priorAttemptNotPublished:true`。blocked后核实已有帖子则可用reconciledPriorAttempt和对应核验键直接记录该核验层级。这是用户/执行者真实核验结论的记录，不是脚本自动查到的。
- 某些平台无manager页面，可从真实提交层直接写account_post_verified，同时说明缺少单独管理记录；不要伪造中间步骤。

工具不强制所有渠道都经过候选、自检、审查等编辑阶段才可记事件，因此真实工作仍需逐项验收。结构性“ready”键只能承载已做的检查，不替代检查本身。

## 报告与失败

```sh
python scripts/campaign.py validate --campaign ./campaign-a
python scripts/campaign.py report --campaign ./campaign-a --out ./report-revision-1
```

`validate`返回schema/基线/事件链/证据字节的结果，明确`liveSemanticsVerified:false`。`report`创建新目录内的UTF-8 `report.md`和自包含`report.html`，所有动态文字HTML转义；不内嵌原始证据文件。synthetic模式有醒目标识，不做真实发布统计。

退出0表示本地所请求操作通过；退出2表示输入/路径/权限/状态/哈希校验失败，保留具体错误。失败不修改已存state；原子替换前崩溃可能留下锁或临时文件，先核真实写入者和文件完整性，不自动删活跃锁。目录存在则init/report/demo拒绝覆盖。

工具不创建后台任务，不自动重试平台，不签署证据，也不能防止拥有文件写权限的人重写整个链。`state.json`是当前本地事实索引，不是第三方不可篡改账本。
