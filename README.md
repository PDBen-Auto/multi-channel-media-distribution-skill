# 七渠道媒体分发 Skill

**一份资料 → 共同事实与素材 → 七平台分别改稿 → 内容审查 → 串行编辑 → 按授权提交 → 分层回查与复盘。**

这是从实际媒体分发项目提炼的完整 Agent Skill。适合新品预览、产品介绍、行业信息等同时面向 Facebook、Reddit、TikTok、YouTube、X、Instagram、LinkedIn 的传播任务。可以只选择部分平台，也可以由一个代理串行执行，无需七个账号同时在线。

它提供工作方法、可复用合同、完整前置条件、脱敏案例和可运行的本地状态/报告工具。**不内置账号，不自动安装 MCP，不是一键群发器，也不承诺流量、销量或七站全部发布成功。**

## 快速使用

将本仓库根目录作为名为 `multi-channel-media-distribution` 的技能文件夹放入宿主支持的 Skill 目录。以当前 Codex 的用户级 `.agents/skills` 为例：

```sh
git clone https://github.com/PDBen-Auto/multi-channel-media-distribution-skill.git
# macOS / Linux
mkdir -p ~/.agents/skills
cp -R multi-channel-media-distribution-skill ~/.agents/skills/multi-channel-media-distribution
```

Windows PowerShell：

```powershell
git clone https://github.com/PDBen-Auto/multi-channel-media-distribution-skill.git
$skillParent = Join-Path $env:USERPROFILE '.agents/skills'
New-Item -ItemType Directory -Force -Path $skillParent | Out-Null
Copy-Item -LiteralPath './multi-channel-media-distribution-skill' -Destination (Join-Path $skillParent 'multi-channel-media-distribution') -Recurse
```

先确认目标同名目录不存在，更新时检查差异，不盲目覆盖。宿主若使用其他目录，按它当前文档放置；不要同时安装两个同名副本。技能未被识别时重新检查目录及宿主的加载方式。没有 Skill 功能的代理可以显式读取 `SKILL.md`，但不能假称已原生安装。

在对话中调用：

> 使用 $multi-channel-media-distribution，把这份产品资料做成英文七渠道传播包。先核实事实和素材，制作三张主题图及竖横视频，完成审查后按渠道顺序编辑，最终发布由我点击。

这是一份调用示例，不是对每次运行授予上传或发布权限。也可以说“仅制作，不登录”“只做 Reddit 和 LinkedIn”“恢复上次未完成的分发”。

## 到底需要准备什么

| 条件 | 谁提供 / 如何检查 | 缺失时怎样继续 |
|---|---|---|
| 支持读取技能的代理及可写工作目录 | 使用者；确认能读取 `SKILL.md`、写入本次目录 | 只交付文字方案，不能声称本地文件已生成 |
| 传播目标、受众、语言、CTA、渠道 | 使用者或代理根据资料提出明确假设 | 先做标注为假设的本地候选，关键歧义再问 |
| 可核实产品事实与原始素材 | 使用者文件或获准研究；读取内容及来源 | 未知参数不写，证据不足不编造 |
| 素材可用范围与品牌/商业关系 | 使用者说明、授权记录和来源 | 不伪造版权证明；实拍、样件、AI示意分别标明 |
| 图像生成/编辑能力 | 仅当要新图；由宿主提供，核实可用及计费 | 可用原素材裁切/排版；不能把提示词当成图片 |
| 视频制作与检查能力 | 仅当要视频；建议 FFmpeg/ffprobe 及实际播放工具 | 可交脚本/分镜但视频项保持未完成 |
| Python 3.10+ | 只运行附带工具时需要；`python --version` | 核心方法可手工执行，无 pip 运行依赖 |
| 当前规则、账户及可信浏览器/API | 仅编辑/发布时；核实实际身份、权限和页面 | 独立本地制作继续，受阻步骤明确人工交接 |
| 当前操作授权 | 逐渠道明确：准备编辑器、谁点击提交、目标和可见性 | 默认不外写，不根据案例继承旧授权 |
| 数据和预算 | 复盘用真实导出；外部收费服务另有预算 | 无数据记 unknown；不自动购买/投放 |

详细安装、版本检查、账号/凭据、费用、网络和缺依赖处理见 [前置条件](references/prerequisites.md)。换电脑迁移的是方法、模板及经选择的项目状态，**不会迁移登录态、聊天侧栏或账号权限**。

## 完整流程及验收

| 阶段 | 实际工作 | 可检查产物 / 放行条件 |
|---|---|---|
| 1. 当前要求与需求基线 | 恢复最新要求、取消项、质量标准、权限，分配 campaignId | brief、验收项、输入字节指纹；不用旧提示覆盖新要求 |
| 2. 事实与素材 | 区分事实/推断/unknown，检查来源、样件/渲染差异和使用权 | facts、rights/source map、受众假设、CTA |
| 3. 渠道研究与分工 | 核实实际内容形式、官方规则与社区规则；明确共享制作和各渠道职责 | 每渠道来源读取记录、位置、正文结构和限制 |
| 4. 共享创意制作 | 根据需求制作图片、视频、封面、字幕及横竖适配 | 真正可读文件；产品外形和事实一致，声音可用 |
| 5. 七渠道改稿 | 根据读者、发布位置、媒体形式改写，不做同文复制 | 标题/正文/标签/ALT/CTA、替代稿、素材映射与披露 |
| 6. 自检与独立审查 | 审事实、观看体验、读者相关性、权利与版本 | 当前哈希对应逐项结论；自检不冒充独立审查或用户采用 |
| 7. 串行编辑 | 一个浏览器操作者；核身份、查重、正常上传、核数量/排序/裁切/封面/文案/可见性 | 实际编辑器预览；未上传不称就绪，权限不足人工选文件 |
| 8. 提交与回查 | 只执行已授权动作；分辨用户提交、处理中、账号内记录与公开页 | ID、时间、URL和证据各自核实；未知结果先查再重试 |
| 9. 交付与复盘 | 汇总全部渠道、版本、阻塞和下一步，按可比窗口复盘 | 自包含HTML、MD、证据清单；不将早期指标当增长证明 |

完整执行细节见 [流程与角色](references/workflow.md)、[渠道方法](references/channels.md)、[创意验收](references/creative-review.md)、[浏览器与发布](references/browser-publishing.md)。原项目采用稳定渠道职责和独立审核，移植时可选单代理；创建对话、派发或并行须遵循宿主和用户授权，安装技能不会自动创建任何任务。

## 离线演练与状态工具

在仓库目录执行：

```sh
python scripts/demo.py --out ./offline-demo
python scripts/campaign.py validate --campaign ./offline-demo/campaign
python -m unittest discover -s tests -v
```

打开 `offline-demo/report/report.html` 即可，无需 localhost。演练是**合成数据**：演示一个账号内记录、多个编辑/上传交接、取消项、未知提交和未完成项；不连接平台、不生成真实媒体、不证明实战发布。输出目录必须是新目录，避免覆盖上一轮。

真实任务起步：

```sh
python scripts/campaign.py init --brief examples/neutral-product/brief.json --out ./campaign-a
# 修改 campaign-a/brief.json 为本轮真实资料后，先完成事实/素材/审查工作。
# record 写入的是你实际核验后的事件，不会替你操作浏览器。
python scripts/campaign.py record --campaign ./campaign-a --channel LinkedIn --event ./reviewed-event.json
python scripts/campaign.py report --campaign ./campaign-a --out ./campaign-a-report
```

`brief.json` 是示例输入，真实初始化前最好直接准备新的 brief；初始化后若修改 brief，必须在尚无事件的阶段重建新目录，已有事件不允许静默换基线。事件 JSON 的完整字段、示例和不允许的状态跳跃见 [数据合同](references/contracts.md)。

## 脱敏案例与证据边界

[案例全文](examples/neutral-product/case-study.md) 使用中性的“户外配件预览”重建，去掉品牌、账号、人物、客户、目录、项目/对话ID、帖子链接与原始媒体，保留有复用价值的决策：

- 20秒视频虽然可播放，因像幻灯片被退回；18秒返工加强真实运动、节奏和文字动效，再按新标准审查。
- 样件实拍与产品渲染有差异，分别披露，不能拼成最终量产产品证据。
- 上传受限时停在人工选文件；没有图/视频就不是编辑完成。
- 部分渠道只核验账号内帖子；部分尚在编辑；一项取消，不伪造七平台全发。
- 音轨技术检查与主观试听分开；本地播放不代表平台裁切和重编码已验证。

这不是原始项目转储，也没有承诺完整匿名不可重识别。公共包重新撰写并排除原图、原片、截图、私人对话、业务链接和会话信息；运行真实任务后产生的工作目录仍可能包含隐私，禁止直接提交仓库。

还附有可读的[七渠道文案](examples/neutral-product/channel-copy.md)、[共享创意分镜与审查表](examples/neutral-product/creative-plan.md)和[离线演练HTML](examples/neutral-product/report.html)。它们都是中性合成示例，不是原客户成品或真实平台记录。

## 目录

```text
SKILL.md                       技能入口
agents/openai.yaml             Codex UI 元数据
references/                    流程、前置条件、渠道、创意、浏览器与数据合同
examples/neutral-product/      脱敏案例和中性输入
scripts/campaign.py            本地初始化、事件校验、MD/HTML报告
scripts/demo.py                离线合成演练
tests/                         状态、权限、证据和恢复测试
VALIDATION.md                  发布时已验证/未验证范围
```

## 安全、授权与许可

脚本只读写用户指定的本地目录，不包含平台API、不读取凭据、不投放、不发私信、不修改安全配置。工具校验能核对字段、路径、哈希和状态前提；**不能证明证据内容真实、账号有权或创意足够好**，这些仍需实际读取、观看和判断。

仓库公开供查看与本人的跨电脑恢复使用。本次没有替权利人新增开源许可或转授第三方素材权利；如需对外再分发、商业集成或开源授权，请先确认权利人的明确许可。Skill规范和平台条款不由本仓库授予。

参考：[Codex Skills](https://developers.openai.com/codex/skills)、[Agent Skills 规范](https://agentskills.io/specification)、[FFmpeg 文档](https://ffmpeg.org/documentation.html)。平台规范入口及核查方式列于渠道参考，执行时必须重新读取当前适用条款。
