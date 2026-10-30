# Optional local photo-analysis experiment

This is an opt-in **local-model experiment**, separate from provider matching, the manual review, and the authored MOCK preview. No paid inference API or API key is required. CPU/GPU time, RAM, disk, electricity, model downloads and any hosting still have costs. It is not a measured automotive inspection capability or a production safety assessment.

## What the implementation does

`GET /api/v1/local-vision/status` checks configuration and the installed local model. `POST /api/v1/local-inspections` accepts one to three user-permitted PNG/JPEG images and an original Copart/IAAI URL. The URL is parsed locally; no auction page, provider record or remote image is fetched. Vehicle/listing identity remains **UNVERIFIED**, and findings remain **EXPERIMENTAL_UNREVIEWED**.

The client must explicitly acknowledge local processing. Unlike the manual review, this separate operation sends selected photo pixels to the application's local backend and then to the fixed Ollama endpoint `http://127.0.0.1:11434`. The backend receives no caller-selected service URL, model override or tool definition. Normal operation does not contact a commercial model API. The Ollama instance must itself be trusted and configured with cloud features disabled; a loopback address alone cannot audit another program's network behavior.

Per-image limits are 2 MiB received bytes, 2048 pixels per side and 4 million decoded pixels; total received image bytes are at most 6 MiB. The JSON request is separately bounded to 9 MiB. Strict base64 decoding, SHA-256 comparison, actual single-frame PNG/JPEG verification and full pixel decoding occur before dispatch. The backend removes original metadata and prepares an RGB JPEG copy. Source-byte and actual inference-byte digests are recorded separately; neither proves auction identity or image ownership.

The configured model must appear in the local inventory with a content digest, positive local weight size, nonempty weight metadata and an advertised `vision` capability. Cloud model names and runtime remote-model metadata are rejected. The adapter checks model identity/digest again before releasing output. One inference operation per API process is allowed; concurrent operations return `BUSY`, rather than building a model queue. Use one API worker for this local workflow.

The model receives a fixed versioned task, the selected image pixels and opaque image IDs. The request includes `think: false` and a bounded generation budget of at most 1,000 predicted tokens, but model/runtime combinations may ignore the thinking preference: the installed `qwen3-vl:2b` thinking renderer did so on a real damaged-vehicle test and exhausted its output budget without final JSON. Prompt revision `visible-evidence-v2` asks for short vehicle-specific evidence and explicit abstention when no vehicle/component is visible. Earlier smoke records used the longer v1 prompt and a 60-second inference limit; they are retained separately rather than relabelled as v2 results. Vehicle VINs, listing URLs, user captions and original filenames are not included in its task. Embedded image text remains untrusted data. Structured output is validated against a separate strict schema: OBSERVED/SUSPECTED findings need in-request image references, no confidence scores/localization/financial/part fields are accepted, and known safety-verdict phrases fail validation. This narrow validation is not a general safety classifier or proof of prompt-injection resistance. Malformed, unsupported, unavailable or failed output never falls back to seeded findings.

Six safety-critical systems remain UNKNOWN with qualified physical-inspection questions regardless of model observations: structure, SRS/airbags, ADAS, cooling, suspension and mechanical function. A `COMPLETED` operation means validated experimental output was received; it does not mean the vehicle passed an inspection or the findings are correct.

## Configuration and local startup

The feature is disabled by default. For the tested setup, install [Ollama from its official distribution](https://ollama.com/download) and use `qwen3-vl:2b`, whose actual model/card/license evidence is recorded below. Other models require a separate supported-input and license review. A code repository's license does not automatically license separately distributed weights. The current implementation does not download models or install/start a daemon from an HTTP request.

On Windows, the optional `scripts/start-local-vision.ps1` launcher consolidates the steps below. Run `scripts/setup.ps1`, install Ollama separately, stop any existing Ollama desktop service, and run `.\scripts\start-local-vision.ps1` in the API terminal. It starts its own loopback-only service with cloud features disabled, downloads `qwen3-vl:2b` if missing (approximately 1.9 GB), and starts the API with local analysis enabled. Start `scripts/start-web.ps1` in another terminal. The launcher refuses an occupied Ollama port and only stops its own process tree. This PowerShell path has not yet been executed on a native Windows machine; the manual commands below remain available. Model quality and source-image rights still require separate validation.

Use one trusted local Ollama instance, with these variables set **in its process before startup**, then start or restart that instance through its normal controls:

```powershell
$env:OLLAMA_HOST = "127.0.0.1:11434"
$env:OLLAMA_NO_CLOUD = "1"
$env:OLLAMA_NUM_PARALLEL = "1"
$env:OLLAMA_MAX_QUEUE = "1"
ollama serve
```

Do not start a duplicate daemon or stop an unrelated process merely because this port is occupied. Existing desktop/tray instances need the same cloud-disable setting applied when they start. Keep the enabled app/runtime on a trusted local machine; public or untrusted-LAN deployment needs separately scoped access controls and resource protection.

After `ollama pull qwen3-vl:2b` has installed the tested model, set the API process variables and restart the backend using its normal command:

```powershell
$env:LOCAL_VISION_ENABLED = "1"
$env:LOCAL_VISION_MODEL = "qwen3-vl:2b"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port 8000
```

Linux/macOS equivalent: export the same variables in the corresponding shells before `ollama serve` and the backend command. No remote API credential is needed. No default model, model license, download size or hardware-performance promise is invented by setting a feature flag. The API's status distinguishes disabled, missing configuration, unavailable runtime, absent model, non-vision model and ready inventory.

## Verified local smoke candidates

The separate [runtime smoke record](local-model-smoke.md) records pinned official runtime/model hashes, model-card/license review, actual requests, failures and final results. Neither candidate has an automotive-quality benchmark.

- `moondream:1.8b`: official image/text tag, approximately 1.7 GB and 2K context. Its actual tag license blob is Apache 2.0. It completed an earlier real local operation but showed poor semantics even on geometric engineering material; it is not the recommended example for reviewing vehicle photos.
- `qwen3-vl:2b`: the pinned tag and canonical upstream model card identify Apache 2.0. An initial 60-second CPU operation timed out. With the final bounded 180-second transport, 1,000-token cap and `visible-evidence-v2` prompt, one real Next.js → FastAPI → Ollama request completed in 46.325 seconds. It correctly returned no vehicle findings for an owned image containing only geometric shapes. This demonstrates one end-to-end abstention case and a working local inference path, not damage-detection precision, general accuracy or a latency guarantee.

To reproduce the final candidate after installing the official runtime, run `ollama pull qwen3-vl:2b`, then set `LOCAL_VISION_MODEL=qwen3-vl:2b` in the API shell. The approximately 1.89 GB model download is not a paid inference API call. Keep cloud features disabled as above and read the actual pinned-source review. Do not confuse installed/available status or a successful engineering smoke with qualified vehicle analysis. Qwen2.5-VL 3B was rejected because its upstream research-only terms did not match the registry wrapper; it was not downloaded.

A later [real damaged-vehicle engineering investigation](research/local-vision-real-vehicle-2026-10-31.md) returned invalid model output on its first run and a timeout on its second. Neither released findings. The geometry smoke must not be presented as evidence that the model reliably analyzes actual vehicle damage.

## CPU request limits

The final request traversed production Next.js, FastAPI and the local model, returning validated output in 46.325 seconds. It correctly abstained on a synthetic non-vehicle image. Prompt revision `visible-evidence-v2` asks for concise vehicle evidence, requests thinking disabled and caps generation at 1,000 tokens. A later actual vehicle attempt showed that the installed thinking renderer could still emit thinking until it consumed the budget. The model-call deadline is 180 seconds; inventory calls remain 5 seconds, and the Next.js rewrite proxy is bounded at 210 seconds so its previous 30-second default does not cut off valid CPU inference. These are engineering limits, not promised model latency. Earlier 60-second/longer-prompt attempts remain separately recorded.

## Lifecycle and evidence

Images and results are transient application memory; no server image/report database or automatic shared history is added. A client cancel clears its view but cannot guarantee stopping inference already running in Ollama; the HTTP transport has a finite 180-second inference timeout and 5-second inventory/info timeout. Timeout does not guarantee termination inside the runtime. Generated normalized copies are not persisted by this adapter. The runtime's own logging/storage configuration and downloaded weights have their own lifecycle.

The adapter records the actual selected model/digest, prompt/schema/adapter revisions, sent-image digests, operation time and usage counts only when returned. Dollar costs and model accuracy are not invented. Synthetic transport tests establish contract behavior; an actual model smoke result, if executed, must be recorded separately and cannot establish damage-detection accuracy. Existing authored fixture illustrations retain their original use restrictions; they are not a real-image evaluation set or an inference-license grant.

## Reviewed official implementation references

Reviewed 29 October 2026 (Asia/Tbilisi), ordinary bounded HTTPS reads:

- [Ollama API documentation](https://github.com/ollama/ollama/blob/main/docs/api.md): documents `GET /api/tags`, `POST /api/show`, `POST /api/chat`, base64 `images`, non-streaming responses, JSON-schema `format`, generation options and returned usage counts. Its `/api/show` example includes the `vision` capability. The raw official document was retrieved successfully; separate guessed `docs/vision.md` and `docs/structured-outputs.md` paths returned 404 and are not used as evidence.
- [Official API response types](https://github.com/ollama/ollama/blob/main/api/types.go): expose remote-model/remote-host information, supporting rejection of reported remote inference.
- [Official environment configuration](https://github.com/ollama/ollama/blob/main/envconfig/config.go): describes `OLLAMA_NO_CLOUD` as disabling cloud features, including remote inference and web search; the setting also has a server-configuration equivalent. The app cannot remotely prove this process setting.
- [Ollama project](https://github.com/ollama/ollama): official runtime/distribution reference. Its runtime license and a chosen model's weight license are separate.
