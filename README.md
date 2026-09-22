# Updream 通用 OpenAI 兼容图片插件

**Updream OpenAI-Compatible Image Plugin** · v1.0.0

一个通用的 Updream 图像生成供应商插件，可接入**任何提供 OpenAI 兼容 Images 接口的第三方平台**。

A universal image-generation provider plugin for [Updream](https://www.updream.cn) that talks to any third-party platform exposing an OpenAI-compatible Images API.

- 源码：本仓库
- 安装包：[Releases](https://github.com/hellojint/updream-openai-compatible-plugin/releases) → `updream-openai-compatible-v1.updplugin`
- 许可证：[MIT](LICENSE)

---

## 作用

Updream 内置了若干供应商，本插件补上**通用的一类**：只要你的第三方平台说的是 OpenAI Images 协议，就能接进来。

```
POST {base_url}/images/generations
Authorization: Bearer <API_KEY>
Content-Type: application/json

{"model": "...", "prompt": "...", "size": "1024x1024", "n": 1}
```

## 适用 / 不适用

**适用**——你的上游满足以下全部条件：

- Base URL 形如 `https://api.example.com/v1`
- 接口路径是 `/images/generations`
- 鉴权方式是 `Authorization: Bearer <API_KEY>`
- 请求体接受 `model` / `prompt` / `size` / `n`

**不适用**——遇到以下情况请换别的方案：

| 上游形态 | 应该用什么 |
| --- | --- |
| 只有 `/v1/responses` 文生图 | Updream 内置的 **OpenAI Responses API** |
| 只有 `/v1/chat/completions` 文生图 | Updream 内置的 **OpenAI Chat Completions** |
| Google Gemini 原生 `generateContent` | Gemini 专用插件 |
| 异步轮询式的视频接口 | 不是图像插件该管的事 |

## 安装

1. 打开 Updream 桌面端，点「导入插件」。
2. 选择 `updream-openai-compatible-v1.updplugin`。
3. 审核 `plugin.py` 后确认安装。
4. 点「添加 Key」。
5. 供应商协议选「**通用 OpenAI 兼容图片**」。

## 需要填写

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| API-Key | 是 | 第三方平台的 Key。运行时读取，本仓库不含任何密钥。 |
| API 地址 | 是 | 如 `https://api.example.com/v1`。默认 `https://api.openai.com/v1`。 |
| 模型 | 是 | 填对方支持的图像模型名，如 `gpt-image-1`、`flux-1-kontext-pro`、`nano-banana`。 |
| Endpoint ID | 否 | 若填写，会**覆盖**「模型」字段作为最终 `model` 值。通常留空。 |

## 尺寸映射

Updream 的「清晰度 + 比例」会被自动换算成具体的 `size` 字符串：

| 清晰度 | 1:1 | 16:9 | 9:16 | 4:3 | 3:4 |
| --- | --- | --- | --- | --- | --- |
| 1K | 1024x1024 | 1280x720 | 720x1280 | 1024x768 | 768x1024 |
| 2K | 2048x2048 | 2048x1152 | 1152x2048 | 2048x1536 | 1536x2048 |

如果在 `extra.size` 里硬写了一个值，则以硬写的为准，不走上面这张表。

## 高级参数（`config.extra`）

| 键 | 作用 |
| --- | --- |
| `n` | 生成张数，自动限制在 1–4 之间。默认 `1`。 |
| `quality` | 原样透传，如 `high`。 |
| `style` | 原样透传，如 `vivid`。 |
| `background` | 如 `transparent`。 |
| `moderation` | 如 `low`。 |
| `output_format` | `b64_json`（默认）或 `url`。 |
| `endpoint_path` | 默认 `/images/generations`，非标准路径时改这里。 |
| `size` | 硬覆盖上面算出来的尺寸。 |
| `default_model` / `default_size` / `default_aspect_ratio` | Updream 没给值时的兜底。 |
| `passthrough` | 任意字典，合并进请求体，用于传供应商私有字段。不会覆盖已设过的字段。 |

## 支持的返回格式

插件对上游返回相当宽容，以下形态都能识别：

- `data[].url` —— 远程图片地址
- `data[].b64_json` —— Base64 数据
- `data[].b64` —— 非标准的 Base64 字段
- `data[].image` —— 字符串，原始 Base64 或完整的 `data:` URI
- 顶层 `url` / `b64_json` —— 单图返回的情况

图片类型从 Base64 前缀嗅探（`/9j/` → JPEG，`UklGR` → WebP，其余按 PNG）。顶层若有 `usage` 字段会一并转发。

## 安全说明

**本插件不含任何凭据。** API Key 由 Updream 自己保存，运行时才读取：

```python
api_key = (cfg.get('api_key') or '').strip()
```

请不要把真实 Key 写进代码、README 或 Issue。如果你 fork 了本项目，也请保持这一点。

## 自己重新打包

`.updplugin` 本质就是一个 ZIP。先改 `manifest.json` 里的 `version`，再执行：

```bash
zip -r updream-openai-compatible-v1.updplugin plugin.py manifest.json README.md
```

ZIP 根目录必须直接包含 `plugin.py`，与 manifest 的 `entry` 字段一致。

---

## English

### What it does

Updream ships a few built-in providers. This plugin adds a **generic one**, so you can point it at any gateway, aggregator or self-hosted service that speaks the OpenAI Images protocol (`POST {base_url}/images/generations`, `Authorization: Bearer <API_KEY>`).

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
| Model | yes | The image model name your upstream accepts, e.g. `gpt-image-1`, `flux-1-kontext-pro`. |
| Endpoint ID | no | If set, it **overrides** the Model field as the final `model` value. Usually leave empty. |

### Size mapping

| Tier | 1:1 | 16:9 | 9:16 | 4:3 | 3:4 |
| --- | --- | --- | --- | --- | --- |
| 1K | 1024x1024 | 1280x720 | 720x1280 | 1024x768 | 768x1024 |
| 2K | 2048x2048 | 2048x1152 | 1152x2048 | 2048x1536 | 1536x2048 |

An upstream-specific `extra.size` value, if provided, takes precedence.

### Advanced options (`config.extra`)

`n` (1–4) · `quality` · `style` · `background` · `moderation` · `output_format` (`b64_json` or `url`) · `endpoint_path` · `size` · `default_model` / `default_size` / `default_aspect_ratio` · `passthrough` (arbitrary dict merged into the request body; never overwrites an already-set field).

### Supported response shapes

`data[].url`, `data[].b64_json`, `data[].b64`, `data[].image`, or a top-level `url` / `b64_json`. MIME is sniffed from the base64 prefix (`/9j/` → JPEG, `UklGR` → WebP, otherwise PNG). Top-level `usage` is forwarded when present.

### Security

This plugin contains **no credentials**. It reads the API key from Updream's own configuration store at run time (`cfg.get('api_key')`). Never commit a real key to this repository, to an issue, or to the README.

### Packaging a release

```bash
zip -r updream-openai-compatible-v1.updplugin plugin.py manifest.json README.md
```

Update `version` in `manifest.json` first. The ZIP must contain `plugin.py` at the root, matching `entry` in the manifest.

---

## Credits

Based on the OpenAI image-provider example in the official Updream plugin development guide.
