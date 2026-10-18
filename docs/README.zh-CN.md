# Ace Data Cloud 的 ComfyUI Seedance 节点

在 ComfyUI 画布中通过 **Ace Data Cloud 使用 Seedance**：只提交一次，保存返回的任务 ID，再查询并预览或保存成品。独立安装本服务包，无需本地模型或显卡；收费以你自己的 Ace 账户权限、余额和当前价格为准。

生成前查看[当前模型价格](https://platform.acedata.cloud/models?utm_source=comfyui&utm_medium=referral&utm_campaign=evergreen&utm_content=seedancecomfyui_readme_zh_cn_pricing)与应用余额。

[English guide](../README.md)

## 官方安装

打开官方 [Seedance by Ace Data Cloud Registry 页面](https://registry.comfy.org/nodes/ace-seedance)，或在 **Manager → Custom Nodes Manager** 搜索 **Seedance**；找不到时再搜 **Ace Data Cloud**。选择 **Seedance by Ace Data Cloud**，核对发布者 **acedatacloud** 和源码仓库 [`AceDataCloud/SeedanceComfyUI`](https://github.com/AceDataCloud/SeedanceComfyUI)，再点击 **Install**。在 **Select Version** 版本对话框明确选择已批准的 Registry 稳定版 **0.1.0**；普通对话框可能默认高亮 **nightly**，本教程不要直接接受该选项。保留依赖自动安装。出现 **Restart Required** 后重启 ComfyUI，并刷新浏览器。Registry ID 为 `ace-seedance`。

![真实 Manager 列表中的本服务节点包](images/manager-discovery.png)

![安装并重启后的真实 Manager 列表](images/manager-installed.png)

以上原图来自 **2026-10-16、Linux ComfyUI 0.41.0** 的发布者品牌搜索安装验收，不是本轮新生成，也不是服务词搜索实拍；见[图片来源与边界](screenshot-sources.json)。

这条 Registry 稳定版安装路径已于 **2026-10-16 在原版 Linux CPU ComfyUI 0.41.0** 验证；该次安装验收没有提交生成或聊天请求。更新的宿主版本及每个收费动作仍需分别验证，模型可用性与价格以当前服务规则为准。

## 注册并获取 API Token

### 复制或创建自己的 API Token

Ace 应用页与其他集成共用：图中 **1** 复制已有 Token，**2** 打开**管理 Key**，再选**创建**。新账户先注册/登录并初始化**通用应用**；确认本服务权限、当前价格、余额、有效期和允许的 API 限制。

![Ace 应用页：复制 Token 或管理 Key](images/get-api-key-en.png)

![Ace 创建 Key 对话框](images/create-api-key-en.png)

以上是 **2026-10-08** 的真实脱敏 Ace 控制台原图，复用自 SunoDify；第二图示例名为 `Dify tutorial`，此处请命名为 `ComfyUI`。本次未创建凭据。Token 只配在**启动 ComfyUI 的进程环境变量** `ACEDATACLOUD_API_KEY` 中并重启；节点没有图示的 Key 输入框，不要贴进提示词、JSON 参数或工作流文件。其他终端的 export 不会配置已经运行的 Desktop 进程。

1. 登录 [Ace Data Cloud → 应用](https://platform.acedata.cloud/console/applications?utm_source=comfyui&utm_medium=referral&utm_campaign=evergreen&utm_content=seedancecomfyui_readme_zh_cn_api_key)。新账户没有通用应用时，先选择**初始化通用应用**。
2. 打开**通用应用**，确认已开通本节点使用的服务。单服务应用的 Key 只限该服务。可复制已有 API Key；需要独立 Key 时，选择**管理 Key → 创建**，命名为 `ComfyUI`。
3. 只复制 Token 字符串，不加 `Bearer ` 或引号。平台管理 Token 不能代替节点调用 API 的 Key。若启用**允许的 API**限制，需同时包含工作流用到的提交和任务查询路径；收费动作前核对当前价格与 Credits 余额。

终端启动示例（只在私有终端粘贴自己的 Token，然后从同一终端启动）：

```bash
export ACEDATACLOUD_API_KEY='在此粘贴自己的私有Token'
python main.py --cpu
```

在**实际 ComfyUI 进程环境**中设置 `ACEDATACLOUD_API_KEY`（也接受 `ACEDATACLOUD_API_TOKEN`），不要写进工作流或仓库。每个 Dify 工具对应一个节点；model/action 选择器覆盖 Dify YAML 的固定选项，其他字段有具名输入框，留空则省略。数组/对象字段在输入框填 JSON 字符串；高级参数也可放进 `parameters_json` JSON 对象，非空具名字段优先。选 `(from JSON/default)` 则使用 JSON 或 API 默认值。任务查询节点可填 `task_id`，批量查询节点可填 `ids_json`。完整字段和 model 列表见[英文主文档](../README.md)。

导入 [01-configure-and-run.json](../examples/01-configure-and-run.json)，先填任务 ID 或 JSON 参数再运行。提交成功不代表媒体完成；用同一个任务 ID 查询至 `succeeded`，把 Ace CDN URL 接到相应 `VIDEO` 节点。收费提交失败时不会自动重试，先查请求记录和价格。删除/归档类动作仍需在 JSON 明确设置 `confirm: true`。详见[隐私说明](PRIVACY.md)。

## 首次工作流：提交一次，再查询原生成品

1. 通过 **File → Open** 导入 [02-submit-once.json](../examples/02-submit-once.json)。确认 Seedance 权限、所选模型与当前价格后，这张**收费提交**工作流只运行一次，从 Preview as Text 复制 task ID；不要把整张生成图用于轮询。
2. 导入 [03-retrieve-native-media.json](../examples/03-retrieve-native-media.json)，粘贴同一个 ID。图中连接 **Retrieve Task → Load Video → Save Video**，状态另有文本预览；这张图不会新建生成任务。
3. 只有状态 succeeded 且成品能预览/保存才算完成。pending 时只重跑查询图；提交超时没拿到 ID，先查请求记录再决定是否付费重发。

这些是可导入配置文件，2026-10-18 已离线校验 API 合同和连接；没有新收费调用，也没有声称已实拍新工作流。
