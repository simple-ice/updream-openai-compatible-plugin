# Updream OpenAI-Compatible Image Plugin

**通用 OpenAI 兼容图片插件 · Updream 插件**

A universal image-generation provider plugin for [Updream](https://www.updream.cn) that talks to **any third-party platform exposing an OpenAI-compatible Images API**.

一个通用的 Updream 图像生成供应商插件，可接入**任何提供 OpenAI 兼容 Images 接口的第三方平台**。

- Author-facing source: this repository
- Installable package: [Releases](../../releases) → `updream-openai-compatible-v1.updplugin`
- License: [MIT](LICENSE)

---

## English

### What it does

Updream ships a few built-in providers. This plugin adds a **generic one** so you can point it at any gateway, aggregator or self-hosted service that speaks the OpenAI Images protocol:

```
POST {base_url}/images/generations
Authorization: Bearer <API_KEY>
Content-Type: application/json

{"model": "...", "prompt": "...", "size": "1024x1024", "n": 1}
```

### When to use it

Use this plugin when the upstream:

- exposes a Base URL like `https://api.example.com/v1`
- serves the endpoint `/images/generations`
- authenticates with `Authorization: Bearer <API_KEY>`
- accepts `model` / `prompt` / `size` / `n` in the JSON body

### When NOT to use it

| Upstream shape | Use instead |
| --- | --- |
| Only `/v1/responses` text-to-image | Updream built-in **OpenAI Responses API** |
| Only `/v1/chat/completions` text-to-image | Updream built-in **OpenAI Chat Completions** |
| Google Gemini native `generateContent` | A Gemini-native plugin |
| Asynchronous video / task-polling API | Not an image plugin |

### Install

1. Open the Updream desktop app.
2. Click **导入插件 / Import plugin**.
3. Select `updream-openai-compatible-v1.updplugin`.
4. Review `plugin.py`, then confirm the install.
5. Click **添加 Key / Add Key**.
6. Choose the provider protocol **通用 OpenAI 兼容图片**.

### Configuration

| Field | Required | Notes |
| --- | --- | --- |
| API-Key | yes | Your third-party key. Read at runtime, never stored in this repo. |
| Base URL | yes | e.g. `https://api.example.com/v1`. Defaults to `https://api.openai.com/v1`. |
| Model | yes | Whatever image model name the upstream accepts, e.g. `gpt-image-1`, `flux-1-kontext-pro`, `nano-banana`. |
| Endpoint ID | no | If set, it **overrides** the Model field as the final `model` value. Usually leave empty. |

### Size mapping

The plugin maps Updream's resolution tier + aspect ratio onto a concrete `size` string:

| Tier | 1:1 | 16:9 | 9:16 | 4:3 | 3:4 |
| --- | --- | --- | --- | --- | --- |
| 1K | 1024x1024 | 1280x720 | 720x1280 | 1024x768 | 768x1024 |
| 2K | 2048x2048 | 2048x1152 | 1152x2048 | 2048x1536 | 1536x2048 |

An upstream-specific `extra.size` value, if provided, takes precedence over the table.

### Advanced options (`config.extra`)

| Key | Purpose |
| --- | --- |
| `n` | Number of images, clamped to 1–4. Default `1`. |
| `quality` | Passed through verbatim, e.g. `high`. |
| `style` | Passed through verbatim, e.g. `vivid`. |
| `background` | e.g. `transparent`. |
| `moderation` | e.g. `low`. |
| `output_format` | `b64_json` (default) or `url`. |
| `endpoint_path` | Default `/images/generations`; change for non-standard paths. |
| `size` | Hard override of the computed size. |
| `default_model` / `default_size` / `default_aspect_ratio` | Fallbacks when Updream does not supply a value. |
| `passthrough` | Arbitrary dict merged into the request body for provider-specific fields. Never overwrites a field already set. |

### Supported response shapes

The plugin is deliberately tolerant about what comes back:

- `data[].url` — remote image URL
- `data[].b64_json` — base64 payload
- `data[].b64` — non-standard base64 field
- `data[].image` — string, either raw base64 or a full `data:` URI
- top-level `url` / `b64_json` for single-image responses

MIME type is sniffed from the base64 prefix (`/9j/` → JPEG, `UklGR` → WebP, otherwise PNG). Top-level `usage` is forwarded when present.

### Security

This plugin contains **no credentials**. It reads the API key from Updream's own configuration store at run time:

```python
api_key = (cfg.get('api_key') or '').strip()
```

Never commit a real key to this repository, to an issue, or to the README. If you fork this project, keep it that way.

### Packaging a release

`.updplugin` is a plain ZIP archive. To rebuild it:

```bash
zip -r updream-openai-compatible-v1.updplugin plugin.py manifest.json README.md
```

Update `version` in `manifest.json` first. The ZIP must contain `plugin.py` at the root, matching `entry` in the manifest.

---

## 中文

### 作用

Updream 内置了若干供应商，本插件补上**通用的一类**：只要你的第三方平台说 OpenAI Images 协议，就能接进来。

### 适用 / 不适用

**适用**：Base URL 形如 `https://api.example.com/v1`、接口路径 `/images/generations`、鉴权 `Authorization: Bearer <API_KEY>`、请求体接受 `model` / `prompt` / `size` / `n`。

**不适用**：只有 `/v1/responses` 或 `/v1/chat/completions` 文生图的，请用 Updream 内置的对应协议；Google Gemini Native `generateContent` 请用 Gemini 专用插件；异步轮询式的视频接口更不适用。

### 安装

1. 打开 Updream 桌面端，点「导入插件」。
2. 选择 `updream-openai-compatible-v1.updplugin`。
3. 审核 `plugin.py` 后确认安装。
4. 点「添加 Key」。
5. 供应商协议选「通用 OpenAI 兼容图片」。

### 需要填写

- **API-Key**：第三方平台的 Key。
- **API 地址**：如 `https://api.example.com/v1`。
- **模型**：填对方支持的图像模型名，如 `gpt-image-1`、`flux-1-kontext-pro`。
- **Endpoint ID**：通常留空；若填写，会覆盖「模型」字段。

### 尺寸映射

见上方表格。Updream 的「清晰度 + 比例」会被自动换算成常见的 `size` 字符串；若在 `extra.size` 里硬写了值，则以硬写的为准。

### 安全说明

**本插件不含任何密钥**，Key 由 Updream 自己保存、运行时读取。请不要把真实 Key 写进代码、README 或 Issue。

### 自己重新打包

`.updplugin` 本质就是一个 ZIP。先改 `manifest.json` 里的 `version`，再执行：

```bash
zip -r updream-openai-compatible-v1.updplugin plugin.py manifest.json README.md
```

ZIP 根目录必须直接包含 `plugin.py`，与 manifest 的 `entry` 字段一致。

---

## Credits

Based on the OpenAI image-provider example in the official Updream plugin development guide.
