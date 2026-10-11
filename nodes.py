"""Schema-backed ComfyUI nodes for the current SeedanceDify catalog.

Model and action selectors are first-class. Remaining Dify parameters use JSON,
which is validated by the copied published API contract before any request.
"""

from __future__ import annotations

import json
import os

from .client import AceDataSeedanceClient

SERVICE = 'Seedance'
MEDIA_TYPES = ('VIDEO',)
TOOL_SPECS = {'seedance_generate_video': {'models': ['doubao-seedance-1-0-pro-250528',
                                        'doubao-seedance-1-0-pro-fast-251015',
                                        'doubao-seedance-1-5-pro-251215',
                                        'doubao-seedance-1-0-lite-t2v-250428',
                                        'doubao-seedance-1-0-lite-i2v-250428',
                                        'doubao-seedance-2-0-260128',
                                        'doubao-seedance-2-0-fast-260128',
                                        'doubao-seedance-2-0-mini-260615',
                                        'doubao-seedance-2-5-260628'],
                             'actions': [],
                             'operation': 'generate',
                             'label': 'Seedance Generate Video',
                             'description': 'Generate a video with Ace Data Cloud Seedance Videos API.',
                             'required': [],
                             'fields': ['content',
                                        'resolution',
                                        'ratio',
                                        'duration',
                                        'frames',
                                        'seed',
                                        'camerafixed',
                                        'watermark',
                                        'generate_audio',
                                        'callback_url',
                                        'return_last_frame',
                                        'execution_expires_after',
                                        'omni_reference_task_type',
                                        'output_format',
                                        'tools',
                                        'priority',
                                        'safety_identifier',
                                        'prompt',
                                        'first_frame_url',
                                        'last_frame_url',
                                        'reference_image_urls',
                                        'reference_audio_urls',
                                        'reference_video_urls']},
 'seedance_task_retrieve': {'models': [],
                            'actions': [],
                            'operation': 'task',
                            'label': 'Seedance Retrieve Task',
                            'description': 'Retrieve one task, optionally waiting up to 240 seconds.',
                            'required': ['task_id'],
                            'fields': []},
 'seedance_tasks_retrieve_batch': {'models': [],
                                   'actions': [],
                                   'operation': 'batch',
                                   'label': 'Seedance Retrieve Tasks',
                                   'description': 'Retrieve existing tasks by ID without repeating '
                                                  'generation.',
                                   'required': ['ids'],
                                   'fields': []}}
SENTINEL = '(from JSON/default)'


def _credential() -> str:
    token = os.environ.get('ACEDATACLOUD_API_KEY') or os.environ.get('ACEDATACLOUD_API_TOKEN')
    if not token or not token.strip():
        raise RuntimeError('Set ACEDATACLOUD_API_KEY in the ComfyUI process environment and restart.')
    return token.strip()


class _ToolNode:
    RETURN_TYPES = ('STRING', 'STRING', 'STRING', 'STRING', 'STRING', 'STRING')
    RETURN_NAMES = ('status', 'task_id', 'media_urls_json', 'first_media_url', 'result_json', 'trace_id')
    FUNCTION = 'run'
    CATEGORY = 'Ace Data Cloud/' + SERVICE
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        spec = cls.SPEC
        required = {'parameters_json': ('STRING', {'multiline': True, 'default': '{}'})}
        if spec['models']:
            required['model'] = ([SENTINEL, *spec['models']], {'default': SENTINEL})
        if spec['actions']:
            required['action'] = ([SENTINEL, *spec['actions']], {'default': SENTINEL})
        for name in spec['fields']:
            if name == 'confirm':
                required[name] = ('BOOLEAN', {'default': False})
            else:
                required[name] = ('STRING', {'multiline': name in {'prompt', 'lyric', 'lyrics',
                    'image_urls', 'audio_urls', 'video_urls', 'negative_prompt'} or name.endswith('_json'),
                    'default': ''})
        if spec['operation'] == 'task':
            required['task_id'] = ('STRING', {'default': ''})
            required['wait_seconds'] = ('INT', {'default': 0, 'min': 0, 'max': 240})
        if spec['operation'] == 'batch':
            required['ids_json'] = ('STRING', {'multiline': True, 'default': ''})
        return {'required': required}

    def run(self, parameters_json: str, model: str = SENTINEL, action: str = SENTINEL,
            task_id: str = '', wait_seconds: int = 0, ids_json: str = '', **fields):
        try:
            parameters = json.loads(parameters_json)
        except (TypeError, ValueError):
            raise ValueError('parameters_json must contain a JSON object.') from None
        if not isinstance(parameters, dict):
            raise ValueError('parameters_json must contain a JSON object.')
        if model != SENTINEL:
            parameters['model'] = model
        if action != SENTINEL:
            parameters['action'] = action
        for name, value in fields.items():
            if value is not None and value != '':
                parameters[name] = value
        if task_id.strip():
            parameters['task_id'] = task_id.strip()
        if self.SPEC['operation'] == 'task':
            parameters['wait_seconds'] = wait_seconds
        if ids_json.strip():
            try:
                ids = json.loads(ids_json)
            except ValueError:
                raise ValueError('ids_json must be a JSON array of task IDs.') from None
            if not isinstance(ids, list) or not ids:
                raise ValueError('ids_json must be a nonempty JSON array of task IDs.')
            parameters['ids'] = ids
        result = AceDataSeedanceClient(_credential()).invoke(self.TOOL, parameters)
        urls = result.get('media_urls') or []
        if not isinstance(urls, list):
            urls = []
        status = str(result.get('status') or 'unknown')
        resolved_task_id = str(result.get('task_id') or '')
        trace_id = str(result.get('trace_id') or '')
        return {
            'ui': {'text': [f'{SERVICE} status: {status}',
                            f'Task ID: {resolved_task_id or "completed synchronously"}',
                            f'Media URLs: {len(urls)}']},
            'result': (status, resolved_task_id, json.dumps(urls), urls[0] if urls else '',
                       json.dumps(result, ensure_ascii=False, default=str), trace_id),
        }


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
for tool, spec in TOOL_SPECS.items():
    class_name = 'Ace' + ''.join(part.title() for part in SERVICE.split()) + ''.join(
        part.title() for part in tool.split('_')
    )
    node = type(class_name, (_ToolNode,), {'TOOL': tool, 'SPEC': spec,
                                          'DESCRIPTION': spec['description']})
    NODE_CLASS_MAPPINGS[class_name] = node
    NODE_DISPLAY_NAME_MAPPINGS[class_name] = spec['label'] + ' (Ace Data Cloud)'


if MEDIA_TYPES:
    from .media import as_audio, as_image, as_video, download_media


class _LoadImage:
    RETURN_TYPES = ('IMAGE',)
    RETURN_NAMES = ('image',)
    FUNCTION = 'run'
    CATEGORY = 'Ace Data Cloud/' + SERVICE
    DESCRIPTION = 'Load a completed Ace CDN image into ComfyUI IMAGE.'

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'media_url': ('STRING', {'default': ''})}}

    def run(self, media_url: str):
        if not media_url:
            raise ValueError('Task is pending; retrieve the same task ID again.')
        return (as_image(download_media(media_url)),)


class _LoadVideo:
    RETURN_TYPES = ('VIDEO',)
    RETURN_NAMES = ('video',)
    FUNCTION = 'run'
    CATEGORY = 'Ace Data Cloud/' + SERVICE
    DESCRIPTION = 'Load a completed Ace CDN video into native ComfyUI VIDEO.'

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'media_url': ('STRING', {'default': ''})}}

    def run(self, media_url: str):
        if not media_url:
            raise ValueError('Task is pending; retrieve the same task ID again.')
        return (as_video(download_media(media_url)),)


class _LoadAudio:
    RETURN_TYPES = ('AUDIO',)
    RETURN_NAMES = ('audio',)
    FUNCTION = 'run'
    CATEGORY = 'Ace Data Cloud/' + SERVICE
    DESCRIPTION = 'Load a completed Ace CDN audio file into ComfyUI AUDIO.'

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'media_url': ('STRING', {'default': ''})}}

    def run(self, media_url: str):
        if not media_url:
            raise ValueError('Task is pending; retrieve the same task ID again.')
        return (as_audio(download_media(media_url)),)


for media_type, base in {'IMAGE': _LoadImage, 'VIDEO': _LoadVideo, 'AUDIO': _LoadAudio}.items():
    if media_type in MEDIA_TYPES:
        class_name = 'Ace' + ''.join(part.title() for part in SERVICE.split()) + 'Load' + media_type.title()
        NODE_CLASS_MAPPINGS[class_name] = type(class_name, (base,), {})
        NODE_DISPLAY_NAME_MAPPINGS[class_name] = SERVICE + ' Load ' + media_type.title() + ' (Ace Data Cloud)'

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'TOOL_SPECS']
