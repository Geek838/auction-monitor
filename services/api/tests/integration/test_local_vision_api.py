"""Optional loopback vision transport tests, not an image-model quality benchmark."""
import base64
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
import json
import socket

from fastapi.testclient import TestClient
from PIL import Image, PngImagePlugin
import pytest

from app.main import app
from app.local_vision.runtime import OllamaRuntime, RuntimeFailure

MODEL = 'test-vision:latest'
DIGEST = 'a' * 64


@pytest.fixture
def client():
    with TestClient(app) as value:
        yield value


def png_bytes(size=(80, 60)):
    out = BytesIO()
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text('PrivateResearchNote', 'DO_NOT_SEND_ORIGINAL_METADATA')
    Image.new('RGB', size, (30, 70, 80)).save(out, format='PNG', pnginfo=metadata)
    return out.getvalue()


def image_input(raw=None, image_id='front'):
    raw = raw if raw is not None else png_bytes()
    return {'image_id': image_id, 'label': 'Engineering image, not a vehicle photograph', 'content_base64': base64.b64encode(raw).decode(), 'sha256': sha256(raw).hexdigest()}


def case():
    return {'url': 'https://iaai.com/VehicleDetail/41000001~US', 'local_processing_permission': True, 'images': [image_input()]}


def output():
    return {'findings': [{'classification': 'OBSERVED', 'component': 'Engineering test pattern', 'region': 'Test square', 'description': 'A transport-double response, not an actual model observation.', 'rationale': 'This test exercises schema and evidence linkage only.', 'confirmation': 'Actual vehicle evidence needs qualified review.', 'image_ids': ['front'], 'confidence': None}], 'limitations': ['This is a transport fixture, not model evaluation.']}


def runtime_double(monkeypatch, *, model_output=None, mutate_answer=None, mutate_inventory=None, mutate_info=None):
    monkeypatch.setenv('LOCAL_VISION_ENABLED', '1')
    monkeypatch.setenv('LOCAL_VISION_MODEL', 'test-vision')
    calls = []
    def request(self, method, path, payload=None):
        calls.append((method, path, deepcopy(payload)))
        if path == '/api/tags':
            inventory = {'models': [{'name': MODEL, 'digest': DIGEST, 'size': 1234}]}
            if mutate_inventory: mutate_inventory(inventory, len([call for call in calls if call[1] == path]))
            return inventory
        if path == '/api/show':
            info = {'capabilities': ['vision'], 'model_info': {'general.architecture': 'engineering-test'}}
            if mutate_info: mutate_info(info)
            return info
        assert path == '/api/chat'
        answer = {'model': MODEL, 'done': True, 'message': {'role': 'assistant', 'content': json.dumps(model_output if model_output is not None else output())}, 'prompt_eval_count': 7, 'eval_count': 11}
        if mutate_answer: mutate_answer(answer)
        return answer
    monkeypatch.setattr(OllamaRuntime, 'request_json', request)
    return calls


def assert_no_report_content(report):
    assert report['outcome'] != 'COMPLETED'
    assert report['images'] == [] and report['findings'] == [] and report['provenance'] is None
    assert report['verification_status'] == 'UNVERIFIED'
    assert report['review_status'] == 'EXPERIMENTAL_UNREVIEWED'


def test_disabled_local_analysis_has_no_transport_or_outbound_dependency(client, monkeypatch):
    monkeypatch.delenv('LOCAL_VISION_ENABLED', raising=False)
    def unexpected(*args, **kwargs): raise AssertionError('disabled analysis attempted I/O')
    monkeypatch.setattr(OllamaRuntime, 'request_json', unexpected)
    monkeypatch.setattr(socket.socket, 'connect', unexpected)
    monkeypatch.setattr(socket, 'getaddrinfo', unexpected)
    status = client.get('/api/v1/local-vision/status')
    assert status.status_code == 200
    assert status.json()['reason_code'] == 'DISABLED' and status.json()['available'] is False
    response = client.post('/api/v1/local-inspections', json=case())
    assert response.status_code == 200
    assert response.json()['reason_code'] == 'DISABLED'
    assert_no_report_content(response.json())


def test_validated_experimental_response_is_bound_to_actual_normalized_pixels(client, monkeypatch):
    calls = runtime_double(monkeypatch)
    request = case()
    request['images'][0]['label'] = '<img src=x onerror=alert(1)>'
    response = client.post('/api/v1/local-inspections', json=request)
    assert response.status_code == 200, response.text
    report = response.json()
    assert report['outcome'] == 'COMPLETED'
    assert report['verification_status'] == 'UNVERIFIED' and report['review_status'] == 'EXPERIMENTAL_UNREVIEWED'
    assert report['reference']['page_id'] == '41000001' and report['reference']['stock_number'] is None
    assert all(item['status'] == 'UNKNOWN' for item in report['checks']) and len(report['checks']) == 6
    assert report['provenance']['model'] == MODEL and report['provenance']['model_digest'] == DIGEST
    assert report['provenance']['prompt_eval_count'] == 7 and report['provenance']['eval_count'] == 11
    chat = next(payload for method, path, payload in calls if path == '/api/chat')
    assert chat['stream'] is False and chat['model'] == MODEL and chat['options']['num_predict'] <= 1500
    assert 'tools' not in chat and chat['format']['type'] == 'object'
    transmitted = base64.b64decode(chat['messages'][1]['images'][0], validate=True)
    assert b'DO_NOT_SEND_ORIGINAL_METADATA' not in transmitted
    assert request['images'][0]['label'] not in json.dumps(chat)
    with Image.open(BytesIO(transmitted)) as decoded:
        assert decoded.format == 'JPEG' and decoded.size == (80, 60)
        assert not decoded.getexif()
    metadata = report['images'][0]
    assert metadata['source_sha256'] == request['images'][0]['sha256']
    assert metadata['inference_sha256'] == sha256(transmitted).hexdigest()
    assert metadata['inference_sha256'] != metadata['source_sha256']
    assert report['provenance']['image_digests'] == {'front': sha256(transmitted).hexdigest()}
    assert 'no-store' in response.headers['cache-control']


@pytest.mark.parametrize('permission', [False, 1, 'true', None])
def test_local_processing_permission_must_be_an_explicit_boolean_true(client, permission):
    payload = case(); payload['local_processing_permission'] = permission
    assert client.post('/api/v1/local-inspections', json=payload).status_code == 422


@pytest.mark.parametrize('mutation', ['duplicates', 'four_images', 'zero_images', 'arbitrary_endpoint', 'image_url', 'provider_override', 'unsafe_image_id'])
def test_request_cannot_choose_destinations_or_unbounded_input(client, mutation):
    payload = case()
    if mutation == 'duplicates': payload['images'].append(deepcopy(payload['images'][0]))
    elif mutation == 'four_images': payload['images'] = [image_input(image_id=f'photo-{i}') for i in range(4)]
    elif mutation == 'zero_images': payload['images'] = []
    elif mutation == 'arbitrary_endpoint': payload['endpoint'] = 'http://169.254.169.254/'
    elif mutation == 'image_url': payload['images'][0]['url'] = 'https://example.invalid/photo.png'
    elif mutation == 'provider_override': payload['model'] = 'hosted-cloud-model'
    elif mutation == 'unsafe_image_id': payload['images'][0]['image_id'] = 'https://example.invalid/'
    assert client.post('/api/v1/local-inspections', json=payload).status_code == 422


@pytest.mark.parametrize('name', ['', 'hosted-cloud', 'https://remote.example/model', '../other-model'])
def test_missing_or_remote_model_names_block_without_transport(client, monkeypatch, name):
    monkeypatch.setenv('LOCAL_VISION_ENABLED', '1'); monkeypatch.setenv('LOCAL_VISION_MODEL', name)
    def unexpected(*args, **kwargs): raise AssertionError('invalid model made runtime request')
    monkeypatch.setattr(OllamaRuntime, 'request_json', unexpected)
    response = client.post('/api/v1/local-inspections', json=case())
    assert response.status_code == 200
    assert response.json()['reason_code'] == 'MODEL_NOT_CONFIGURED'
    assert_no_report_content(response.json())


@pytest.mark.parametrize('mutation,reason', [('hash', 'IMAGE_CHANGED'), ('invalid_base64', 'INVALID_IMAGE'), ('corrupt', 'INVALID_IMAGE'), ('svg', 'INVALID_IMAGE'), ('too_wide', 'INVALID_IMAGE'), ('too_many_pixels', 'INVALID_IMAGE')])
def test_invalid_received_pixels_fail_before_model_dispatch(client, monkeypatch, mutation, reason):
    calls = runtime_double(monkeypatch)
    payload = case()
    if mutation == 'hash': payload['images'][0]['sha256'] = '0' * 64
    elif mutation == 'invalid_base64': payload['images'][0]['content_base64'] = 'not-base64!'
    elif mutation == 'corrupt': payload['images'][0] = image_input(b'not a raster')
    elif mutation == 'svg': payload['images'][0] = image_input(b'<svg xmlns="http://www.w3.org/2000/svg"/>')
    elif mutation == 'too_wide': payload['images'][0] = image_input(png_bytes((2049, 1)))
    elif mutation == 'too_many_pixels': payload['images'][0] = image_input(png_bytes((2048, 2048)))
    response = client.post('/api/v1/local-inspections', json=payload)
    assert response.status_code == 200
    assert response.json()['reason_code'] == reason
    assert_no_report_content(response.json())
    assert calls == []


@pytest.mark.parametrize('mutation,reason', [('missing', 'MODEL_NOT_INSTALLED'), ('remote', 'REMOTE_MODEL_DENIED'), ('text_only', 'MODEL_NOT_VISION'), ('missing_digest', 'INVALID_RUNTIME_RESPONSE'), ('boolean_size', 'REMOTE_MODEL_DENIED')])
def test_inventory_cannot_silently_select_a_different_or_hosted_model(client, monkeypatch, mutation, reason):
    def inventory(value, count):
        if mutation == 'missing': value['models'] = []
        elif mutation == 'remote': value['models'][0]['remote_host'] = 'https://remote.invalid'
        elif mutation == 'missing_digest': value['models'][0].pop('digest')
        elif mutation == 'boolean_size': value['models'][0]['size'] = True
    def info(value):
        if mutation == 'text_only': value['capabilities'] = ['completion']
    calls = runtime_double(monkeypatch, mutate_inventory=inventory, mutate_info=info)
    response = client.post('/api/v1/local-inspections', json=case())
    assert response.status_code == 200
    assert response.json()['reason_code'] == reason
    assert_no_report_content(response.json())
    assert all(path != '/api/chat' for method, path, payload in calls)


@pytest.mark.parametrize('mutation', ['dangling_image', 'missing_evidence', 'confidence', 'financial_extra', 'safety_claim', 'missing_limitations'])
def test_model_output_is_untrusted_and_never_replaced_with_seeded_findings(client, monkeypatch, mutation):
    model_output = output()
    finding = model_output['findings'][0]
    if mutation == 'dangling_image': finding['image_ids'] = ['different-photo']
    elif mutation == 'missing_evidence': finding['image_ids'] = []
    elif mutation == 'confidence': finding['confidence'] = 0.99
    elif mutation == 'financial_extra': finding['repair_cost'] = '100.00'
    elif mutation == 'safety_claim': finding['description'] = 'This vehicle is safe to drive.'
    elif mutation == 'missing_limitations': model_output['limitations'] = []
    runtime_double(monkeypatch, model_output=model_output)
    response = client.post('/api/v1/local-inspections', json=case())
    assert response.status_code == 200
    assert response.json()['reason_code'] == 'INVALID_MODEL_OUTPUT'
    assert_no_report_content(response.json())


@pytest.mark.parametrize('mutation', ['model_mismatch', 'not_done', 'tool_call', 'malformed_json', 'invalid_usage'])
def test_invalid_runtime_completion_and_tool_requests_fail_closed(client, monkeypatch, mutation):
    def mutate(answer):
        if mutation == 'model_mismatch': answer['model'] = 'another-model:latest'
        elif mutation == 'not_done': answer['done'] = False
        elif mutation == 'tool_call': answer['message']['tool_calls'] = [{'function': {'name': 'fetch_url'}}]
        elif mutation == 'malformed_json': answer['message']['content'] = 'not JSON'
        elif mutation == 'invalid_usage': answer['eval_count'] = True
    runtime_double(monkeypatch, mutate_answer=mutate)
    response = client.post('/api/v1/local-inspections', json=case())
    assert response.status_code == 200
    assert response.json()['reason_code'] == 'INVALID_MODEL_OUTPUT'
    assert_no_report_content(response.json())


def test_model_replacement_during_awaited_run_invalidates_findings(client, monkeypatch):
    def replace(inventory, count):
        if count > 1: inventory['models'][0]['digest'] = 'b' * 64
    runtime_double(monkeypatch, mutate_inventory=replace)
    response = client.post('/api/v1/local-inspections', json=case())
    assert response.status_code == 200
    assert response.json()['reason_code'] == 'MODEL_CHANGED'
    assert_no_report_content(response.json())


def test_valid_empty_findings_is_honest_abstention_with_all_six_unknowns(client, monkeypatch):
    runtime_double(monkeypatch, model_output={'findings': [], 'limitations': ['No supported visible feature was identified by this test double.']})
    response = client.post('/api/v1/local-inspections', json=case())
    assert response.status_code == 200
    report = response.json()
    assert report['outcome'] == 'COMPLETED' and report['findings'] == []
    assert len(report['checks']) == 6 and all(check['status'] == 'UNKNOWN' for check in report['checks'])


def test_unavailable_runtime_does_not_generate_fixture_observations(client, monkeypatch):
    monkeypatch.setenv('LOCAL_VISION_ENABLED', '1'); monkeypatch.setenv('LOCAL_VISION_MODEL', 'test-vision')
    def unavailable(*args, **kwargs): raise RuntimeFailure('RUNTIME_UNAVAILABLE', 'Local runtime unavailable.')
    monkeypatch.setattr(OllamaRuntime, 'request_json', unavailable)
    status = client.get('/api/v1/local-vision/status')
    assert status.status_code == 200 and status.json()['available'] is False
    response = client.post('/api/v1/local-inspections', json=case())
    assert response.status_code == 200
    assert response.json()['reason_code'] == 'RUNTIME_UNAVAILABLE'
    assert_no_report_content(response.json())


def test_concurrent_local_inference_is_blocked_before_pixels_or_runtime_are_processed(client, monkeypatch):
    from app.local_vision.service import INFERENCE_LOCK
    calls = runtime_double(monkeypatch)
    assert INFERENCE_LOCK.acquire(blocking=False)
    try:
        response = client.post('/api/v1/local-inspections', json=case())
    finally:
        INFERENCE_LOCK.release()
    assert response.status_code == 200
    assert response.json()['reason_code'] == 'BUSY'
    assert_no_report_content(response.json())
    assert calls == []


def test_decoded_byte_limit_is_checked_even_when_base64_padding_length_fits_the_schema(client, monkeypatch):
    calls = runtime_double(monkeypatch)
    raw = png_bytes()
    # 2MiB and 2MiB+1 encode to the same base64 length because of padding.
    too_large = raw + b'\x00' * (2 * 1024 * 1024 + 1 - len(raw))
    response = client.post('/api/v1/local-inspections', json={**case(), 'images': [image_input(too_large)]})
    assert response.status_code == 200
    assert response.json()['reason_code'] == 'IMAGE_TOO_LARGE'
    assert_no_report_content(response.json())
    assert calls == []


def test_animated_png_is_not_a_single_frame_analysis_input(client, monkeypatch):
    calls = runtime_double(monkeypatch)
    out = BytesIO()
    Image.new('RGB', (20, 20), 'red').save(out, format='PNG', save_all=True, append_images=[Image.new('RGB', (20, 20), 'blue')], duration=100, loop=0)
    response = client.post('/api/v1/local-inspections', json={**case(), 'images': [image_input(out.getvalue())]})
    assert response.status_code == 200
    assert response.json()['reason_code'] == 'INVALID_IMAGE'
    assert_no_report_content(response.json())
    assert calls == []


def test_jpeg_orientation_is_applied_and_original_exif_is_not_sent_to_the_runtime(client, monkeypatch):
    calls = runtime_double(monkeypatch)
    image = Image.new('RGB', (80, 60), 'green')
    metadata = Image.Exif(); metadata[274] = 6; metadata[270] = 'PRIVATE_ORIGINAL_EXIF'
    raw = BytesIO(); image.save(raw, format='JPEG', exif=metadata)
    response = client.post('/api/v1/local-inspections', json={**case(), 'images': [image_input(raw.getvalue())]})
    assert response.status_code == 200
    report = response.json()
    assert report['outcome'] == 'COMPLETED'
    sent = next(payload for method, path, payload in calls if path == '/api/chat')
    normalized = base64.b64decode(sent['messages'][1]['images'][0])
    assert b'PRIVATE_ORIGINAL_EXIF' not in normalized
    assert report['images'][0]['width'] == 60 and report['images'][0]['height'] == 80
    with Image.open(BytesIO(normalized)) as prepared:
        assert prepared.size == (60, 80) and not prepared.getexif()


def test_large_local_analysis_body_is_rejected_before_framework_json_parsing(client):
    response = client.post('/api/v1/local-inspections', content=iter([b' ' * (9 * 1024 * 1024), b' ']), headers={'Content-Type': 'application/json'})
    assert response.status_code == 413
    assert '9216 KiB' in response.json()['detail']
