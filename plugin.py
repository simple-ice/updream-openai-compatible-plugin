
import json
import httpx

_SIZE = {
    '1K': {
        '1:1': '1024x1024',
        '16:9': '1280x720',
        '9:16': '720x1280',
        '4:3': '1024x768',
        '3:4': '768x1024',
    },
    '2K': {
        '1:1': '2048x2048',
        '16:9': '2048x1152',
        '9:16': '1152x2048',
        '4:3': '2048x1536',
        '3:4': '1536x2048',
    },
}


def _fail(msg):
    return {'status': 'failed', 'error': str(msg)}


def _mime_from_b64_head(b64):
    if b64.startswith('/9j/'):
        return 'image/jpeg'
    if b64.startswith('UklGR'):
        return 'image/webp'
    return 'image/png'


def generate_image(params):
    cfg = params.get('config') or {}
    extra = cfg.get('extra') or {}

    api_key = (cfg.get('api_key') or '').strip()
    if not api_key:
        return _fail('未填写 API-Key')

    base_url = (cfg.get('base_url') or 'https://api.openai.com/v1').strip().rstrip('/')
    model = (params.get('endpoint_id') or params.get('model') or extra.get('default_model') or 'gpt-image-1').strip()
    prompt = (params.get('prompt') or '').strip()
    if not prompt:
        return _fail('Prompt 不能为空')

    size_tier = (params.get('size') or extra.get('default_size') or '1K').upper()
    aspect_ratio = (params.get('aspect_ratio') or extra.get('default_aspect_ratio') or '1:1').strip()
    resolved_size = extra.get('size') or _SIZE.get(size_tier, _SIZE['1K']).get(aspect_ratio, '1024x1024')

    n = extra.get('n', 1)
    try:
        n = int(n)
    except Exception:
        n = 1
    n = 1 if n < 1 else (4 if n > 4 else n)

    quality = extra.get('quality')
    style = extra.get('style')
    background = extra.get('background')
    moderation = extra.get('moderation')
    output_format = (extra.get('output_format') or 'b64_json').strip()
    endpoint_path = (extra.get('endpoint_path') or '/images/generations').strip()
    if not endpoint_path.startswith('/'):
        endpoint_path = '/' + endpoint_path

    body = {
        'model': model,
        'prompt': prompt,
        'size': resolved_size,
        'n': n,
    }
    if output_format in ('b64_json', 'url'):
        body['response_format'] = output_format
    if quality:
        body['quality'] = quality
    if style:
        body['style'] = style
    if background:
        body['background'] = background
    if moderation:
        body['moderation'] = moderation

    # Optional provider-specific pass-through fields.
    passthrough = extra.get('passthrough')
    if isinstance(passthrough, dict):
        for k, v in passthrough.items():
            if k not in body:
                body[k] = v

    headers = {
        'Authorization': 'Bearer ' + api_key,
        'Content-Type': 'application/json',
    }

    try:
        resp = httpx.post(base_url + endpoint_path, headers=headers, json=body, timeout=180)
    except Exception as e:
        return _fail('请求失败: %s' % e)

    if resp.status_code >= 400:
        text = (resp.text or '')[:1000]
        return _fail('HTTP %s: %s' % (resp.status_code, text))

    try:
        data = resp.json()
    except Exception:
        return _fail('接口返回的不是合法 JSON')

    images = []
    for item in data.get('data', []) or []:
        if isinstance(item, dict):
            if item.get('url'):
                images.append(item['url'])
            elif item.get('b64_json'):
                b64 = item['b64_json']
                images.append('data:%s;base64,%s' % (_mime_from_b64_head(b64), b64))
            elif item.get('b64'):
                b64 = item['b64']
                images.append('data:%s;base64,%s' % (_mime_from_b64_head(b64), b64))
            elif item.get('image'):
                val = item['image']
                if isinstance(val, str) and val.startswith('data:'):
                    images.append(val)
                elif isinstance(val, str):
                    images.append('data:image/png;base64,%s' % val)

    # Some providers may return a single url / b64 at top level.
    if not images:
        if isinstance(data.get('url'), str):
            images.append(data['url'])
        elif isinstance(data.get('b64_json'), str):
            b64 = data['b64_json']
            images.append('data:%s;base64,%s' % (_mime_from_b64_head(b64), b64))

    if not images:
        return _fail('未返回图片；响应片段: %s' % json.dumps(data, ensure_ascii=False)[:500])

    result = {'status': 'success', 'images': images}
    usage = data.get('usage')
    if isinstance(usage, dict):
        result['usage'] = usage
    return result
