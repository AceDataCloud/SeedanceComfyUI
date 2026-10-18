# Seedance for ComfyUI by Ace Data Cloud

Use **Seedance through Ace Data Cloud** directly in your ComfyUI workflow: submit once, keep the returned task ID, then retrieve and preview or save the finished media. Install this independent service package; no local model or GPU is needed. Paid calls use your own Ace account and [current service pricing](https://platform.acedata.cloud/models?utm_source=comfyui&utm_medium=referral&utm_campaign=evergreen&utm_content=seedancecomfyui_readme_en_pricing).

[简体中文](docs/README.zh-CN.md) · [Ace Data Cloud](https://platform.acedata.cloud?utm_source=comfyui&utm_medium=referral&utm_campaign=evergreen&utm_content=seedancecomfyui_readme_en_home) · [Issues](https://github.com/AceDataCloud/SeedanceComfyUI/issues)

## Install

Open the official [Seedance by Ace Data Cloud Registry page](https://registry.comfy.org/nodes/ace-seedance), or open **Manager → Custom Nodes Manager** and search **Seedance**. Use **Ace Data Cloud** as a fallback to find this publisher’s packages. Select **Seedance by Ace Data Cloud**, confirm publisher **acedatacloud** and source repository [`AceDataCloud/SeedanceComfyUI`](https://github.com/AceDataCloud/SeedanceComfyUI), then click **Install**. In **Select Version**, explicitly select the approved Registry stable release **0.1.0**. The normal dialog may initially highlight **nightly**; do not accept it for this stable-release tutorial. Keep dependency installation enabled. After **Restart Required**, restart ComfyUI and refresh the browser. Registry ID: `ace-seedance`.

![Actual ComfyUI-Manager list with this Ace service package](docs/images/manager-discovery.png)

![Actual Manager list after installation and restart](docs/images/manager-installed.png)

These are real **2026-10-16, ComfyUI 0.41.0 Linux** screenshots from the publisher-brand installation test, not a new paid request or a screenshot of service-only search. See [image sources and limits](docs/screenshot-sources.json).

This Registry stable installation was verified on **2026-10-16 with original ComfyUI 0.41.0 on Linux CPU**. That test did not submit a generation or chat request. Newer host versions and each paid action require their own checks; model availability and price remain subject to the current service rules.

For local source testing, clone this repository into `ComfyUI/custom_nodes/SeedanceComfyUI` and run `python -m pip install -r requirements.txt` in ComfyUI's environment, then restart. Native media loaders require ComfyUI 0.39.0 or newer. This package uses ComfyUI's existing image/audio/video libraries for decoding.

## Key and tool inputs

### Copy or create your own API Token

The Applications screen is shared across Ace integrations. **1** copies the existing token; **2** opens **Manage Keys**, then **Create**. A new account signs in/registers and initializes **General application** first. Verify this service's access, current price, balance and any expiry/Allowed APIs restrictions.

![Ace Applications: copy token or open Manage Keys](docs/images/get-api-key-en.png)

![Ace Create Key dialog](docs/images/create-api-key-en.png)

These masked **2026-10-08** Ace Console screenshots are reused from SunoDify. The example credential name in the second image is `Dify tutorial`; name yours `ComfyUI`. No credential was created by this guide update. Paste only the token into **the environment of the process that launches ComfyUI** (`ACEDATACLOUD_API_KEY`), then restart. There is no ComfyUI API Key textbox in these nodes; do not paste it into prompt/JSON widgets or the workflow file. An unrelated terminal export does not configure an already-running Desktop process.

1. Sign in to [Ace Data Cloud → Applications](https://platform.acedata.cloud/console/applications?utm_source=comfyui&utm_medium=referral&utm_campaign=evergreen&utm_content=seedancecomfyui_readme_en_api_key). If your account has no General application, choose **Initialize General Application**.
2. Open **General application** and check access to the service used by this package. A service-specific application key is limited to that service. Copy an existing API key, or choose **Manage Keys → Create** for a separate key named `ComfyUI`.
3. Copy only the token string, without `Bearer ` or quotation marks. A platform management token is not the API key these nodes use. If you enable **Allowed APIs**, include every submission and task-query path used by your workflow. Check current pricing and available Credits before a paid action.

For a terminal launch, paste your token only in your private terminal, then start ComfyUI from that same terminal:

```bash
export ACEDATACLOUD_API_KEY='paste-your-private-token-here'
python main.py --cpu
```

Set `ACEDATACLOUD_API_KEY` (or `ACEDATACLOUD_API_TOKEN`) in the **ComfyUI process environment** and restart. Keep the key out of workflow JSON, screenshots, issues, and the repository.

Each Dify tool has its own node. The model and action selectors expose every fixed choice in the source YAML. Other fields appear as named text or confirmation widgets; leave one empty to omit it. `parameters_json` accepts the same API fields as an advanced JSON object. A nonempty widget overrides the matching JSON field; `(from JSON/default)` keeps a model/action supplied by JSON or the API default. Arrays and objects can be entered as JSON strings in their named widgets. Task lookup nodes also offer `task_id` and `wait_seconds`; batch lookup nodes offer `ids_json`. Contract validation happens before a request. Paid submissions are never retried after a connection failure; preserve an accepted task ID and inspect request history before paying again.

| Dify tool | Required fields in JSON | Model choices | Action choices |
| --- | --- | --- | --- |
| `seedance_generate_video` | — | `doubao-seedance-1-0-pro-250528`, `doubao-seedance-1-0-pro-fast-251015`, `doubao-seedance-1-5-pro-251215`, `doubao-seedance-1-0-lite-t2v-250428`, `doubao-seedance-1-0-lite-i2v-250428`, `doubao-seedance-2-0-260128`, `doubao-seedance-2-0-fast-260128`, `doubao-seedance-2-0-mini-260615`, `doubao-seedance-2-5-260628` | — |
| `seedance_task_retrieve` | `task_id` | — | — |
| `seedance_tasks_retrieve_batch` | `ids` | — | — |

Import [01-configure-and-run.json](examples/01-configure-and-run.json) with **File → Open**, fill its placeholder task ID or JSON parameters, then run. The example is a configuration template; it does not submit a paid request by itself. Query the same task ID until `status` is `succeeded`. The node returns status, task ID, all media URLs as JSON, first media URL, normalized result JSON, and trace ID. Connect a completed Ace CDN URL to the provided `VIDEO` loader where applicable.

Check current service pricing before a paid run. Read-only task queries and media downloads should not generate a new paid task. Destructive Dify actions still require an explicit `confirm: true` in JSON. See [privacy notes](docs/PRIVACY.md).

## First workflow: submit once, then retrieve native media

1. Import [02-submit-once.json](examples/02-submit-once.json) with **File → Open**. After checking your Seedance service access, model and current price, run this **paid submission** workflow once. Copy the task ID shown by Preview as Text. It is deliberately separate from polling.
2. Import [03-retrieve-native-media.json](examples/03-retrieve-native-media.json), paste that same ID and run. It connects **Retrieve Task → Load Video → Save Video**, with a separate status preview. This graph never submits a new generation.
3. Wait for status `succeeded` and a real preview/saved file. If still pending, repeat only this retrieve graph with the same ID. If the submit timed out without an ID, inspect request history before paying again.

The JSON files are importable configuration examples; their contracts and links were checked offline on 2026-10-18. No new paid call or screenshot of these new graphs was made.

## Development

```bash
python -m unittest discover -s tests -v
python -m py_compile __init__.py client.py api_contracts.py nodes.py
```

`pyproject.toml` declares short Registry ID `ace-seedance`, publisher `acedatacloud`, and a 400×400 proportional resize of the [canonical Ace logo](https://cdn.acedata.cloud/assets/logo.png).
