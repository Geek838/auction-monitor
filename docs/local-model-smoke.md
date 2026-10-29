# Local-model runtime smoke evidence

Execution date: 29 October 2026 (Asia/Tbilisi). This is a bounded local-runtime experiment using a newly authored geometric engineering image. It is not a vehicle inspection, damage benchmark, source-data integration or qualified safety assessment. **Latest operational result:** the final Qwen3-VL 2B retry completed through the production Next.js proxy and FastAPI in 46.325 seconds with an appropriate no-vehicle abstention. Earlier weak output and timeout results are retained below; automotive quality remains unvalidated.

## Verified sources and artifacts

- Official Ollama release: [v0.40.13](https://github.com/ollama/ollama/releases/tag/v0.40.13). The Linux amd64 archive is 1,525,346,571 bytes. The release's asset digest and [published checksums](https://github.com/ollama/ollama/releases/download/v0.40.13/sha256sum.txt) identify SHA-256 `c9490e0f520be21271d969e6703f012268b1d39f8b70dd58854e5bfef7a75bb6`. The complete downloaded archive matched that size and SHA-256 before extraction. Only the CPU runtime/libraries were extracted (approximately 76 MB); CUDA/Vulkan libraries were excluded.
- Official model: [moondream:1.8b](https://ollama.com/library/moondream:1.8b), advertised as image/text input, 2K context and approximately 1.7 GB. The page warns about inaccurate output and difficulty with intricate instructions. It is an older small model selected for a resource-bounded smoke run, not a claim it is suitable for automotive inspection.
- Registry manifest SHA-256: `55fc3abd386771e5b5d1bbcc732f3c3f4df6e9f9f08f1131f9cc27ba2d1eec5b`, matching the official tag's displayed digest prefix. Language-model blob: `e554c6b9de016673fd2c732e0342967727e9659ca5f853a4947cc96263fa602b` (828,661,152 bytes); vision projector: `4cc1cb3660d87ff56432ebeb7884ad35d67c48c7b9f6b2856f305e39c38eed8f` (909,777,984 bytes). Every downloaded registry blob was checked against its manifest size and full SHA-256 before installation in the local model cache.
- The tag's actual license blob, SHA-256 `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`, contains Apache License 2.0. The [upstream model card](https://huggingface.co/vikhyatk/moondream2) also identifies Apache 2.0; its current revision is not assumed byte-identical to this older Ollama tag. No weights are committed or redistributed by the repository.
- [Official Ollama FAQ](https://github.com/ollama/ollama/blob/main/docs/faq.mdx) documents `OLLAMA_NO_CLOUD=1` and the default loopback binding. The experiment explicitly disables cloud features and binds only `127.0.0.1:11434`.

## Resource and privacy boundary

The cloud machine has x86-64 architecture, five reported logical CPUs and approximately 32 GiB available RAM; no GPU or preinstalled Ollama was detected. Runtime/model files are under ignored `.cache/ollama/`, with an initial official runtime/first-model download budget below 4 GB. The separately authorized second-candidate limit and actual aggregate bytes are recorded below. No system service, public listener, hosted inference, account or paid API is used.

Stock Ollama requires a newly generated identity file in the user's `.ollama` directory. A narrowly scoped filesystem permission was granted for this normal initialization; HOME was not redirected and no existing private credential was read or printed. Model weights, archive and executable stay under the workspace.

The smoke image is a fresh 256×192 RGB drawing: a red rectangle, blue circle and engineering-test labels rendered with Pillow drawing primitives and its bundled font. It contains no vehicle, auction material or personal data. Its SHA-256 is `ff340c88aaf831761b0284eacd7bde13ccda53a0d385b2976147666bea3fef72`. The author explicitly permits this image's local inference smoke use; training is not authorized. Existing Sprint 3 illustrations were not used because their manifest does not grant inference use.

## Runtime result

All three actual inference paths completed against the installed local runtime, without transport doubles:

| Check | Observed result |
| --- | --- |
| Runtime identity | `/api/version` returned `0.40.13`; log confirms `Ollama cloud disabled: true`, CPU inference and listener `127.0.0.1:11434` |
| Installed model | `/api/tags` and `/api/show` returned the exact pinned manifest digest, local nonzero model size and `vision` capability; no remote-model metadata |
| Direct image-caption request | Actual `/api/chat`, temperature 0 and a 40-token cap, completed in **11.641 seconds**, with 746 prompt tokens and 12 generated tokens |
| Full application service | `create_local_inspection` parsed the original URL, verified source pixels, created the metadata-stripped JPEG inference copy, called the actual runtime and validated the result in **24.252 seconds** |
| Actual FastAPI HTTP boundary | In-process `TestClient(app)` GET `/api/v1/local-vision/status` returned HTTP 200 READY, then POST `/api/v1/local-inspections` performed actual local inference and returned HTTP 200 COMPLETED in **21.543 seconds**, with non-cacheable headers, exact source/inference digests and six UNKNOWN physical checks |
| Application outcome | `COMPLETED` / `LOCAL_EXPERIMENT_COMPLETED`, with `UNVERIFIED` identity, `EXPERIMENTAL_UNREVIEWED` review status, six UNKNOWN physical checks, actual model digest and 745 prompt / 163 generated tokens |
| Exact inference copy | SHA-256 `792e75ac74f2631135c0a7c9dfbd67efe849f301f968299970ca9cb8337c76a0`, distinct from the received PNG's recorded source digest |

**Quality limitation observed, not hidden:** the direct caption said “urn of red and blue circles on a white background.” The authored red shape is a rectangle, so that description was inaccurate. The structured application result returned one UNKNOWN entry using “blue circle” and “red box” as component/region and repeated image-label text in rationale/confirmation and limitations. It passed the strict structural contract but does not demonstrate useful automotive reasoning, reliable abstention explanations or professionally actionable recommendations.

This establishes that a real no-paid-API CPU vision runtime can execute through the application adapter. It does **not** establish that this small model is suitable for release as an automotive inspector. Schema validity is separate from semantic quality. No vehicle case, human-adjudicated benchmark, safety accuracy or production 1.0 readiness is claimed. The optional feature must remain experimental and default-disabled until an appropriate installed model and actual evaluation support a narrower claim.

Generated inputs, permission record, exact runtime responses and server log remain ignored local smoke artifacts under `.cache/ollama/`. The JSON results are not seeded app data and must not be reused as analysis for other images. After the final actual API check, the task-owned server received SIGTERM and exited cleanly. Port 11434 was checked closed. Verified binary/model files remain ignored in the workspace for reuse; no process is assumed to survive a task or snapshot. The new normal Ollama identity is local runtime state outside Git. No application source, dependency or test file was changed by this smoke agent.

## Bounded second-candidate follow-up

The initial candidate's semantic weaknesses justified checking one additional permissively licensed model rather than presenting the first structurally valid result as adequate AI.

**Qwen2.5-VL 3B was rejected before downloading weights.** Although its Ollama registry license layer contains Apache 2.0, the canonical [Qwen2.5-VL-3B-Instruct model card](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct) identifies `qwen-research`, and its actual [upstream LICENSE](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct/blob/main/LICENSE) says the grant is “FOR NON-COMMERCIAL PURPOSES ONLY” and commercial users must request a license. A registry wrapper is not sufficient evidence to ignore the canonical upstream restriction. No Qwen2.5-VL 3B weights were downloaded or executed.

The fallback [qwen3-vl:2b](https://ollama.com/library/qwen3-vl:2b) exists in the official library. Its canonical [Qwen3-VL-2B-Instruct card](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct), reviewed at upstream commit `89644892e4d85e24eaac8bacfd4f463576704203`, identifies Apache 2.0; the actual registry license layer matches Apache 2.0 as well. The upstream repository publishes a README/model-card license declaration rather than a separate LICENSE file. This agreement of published sources distinguishes it from the rejected 3B candidate; it is not an automotive-quality endorsement.

- Verified manifest digest: `0635d9d857d497aeadba3d7d27485746c50554446f9f6ec01ef39788221adbe8`.
- Model blob: `ebabfa59b71a5b96e0281ec2994977e785284e0939807a99fc340dec3c6f10de`, 1,889,496,384 bytes, full SHA-256 checked before cache installation.
- Registry license blob: `7339fa418c9ad3e8e12e74ad0fd26a9cc4be8703f9c110728a992b193be85cb2`, 11,355 bytes, verified before downloading large weights.
- Declared artifacts approximately 1.89 GB; aggregate runtime plus both installed candidates approximately **5.16 GB**, within the separately authorized 8 GB follow-up budget. All model files remain ignored.
- The actual runtime reported local Q4_K_M weights, 2.1B parameters, the exact digest and `completion`, `vision`, `tools`, `thinking` capabilities. The application supplies no tools and rejects tool calls. After verifying the official chat API's supported `think` field, the application explicitly disables thinking for its bounded final-JSON task.

### Actual second-candidate API outcome

The same owned geometric image, application prompt and structured contract were used for one actual in-process FastAPI HTTP run. GET `/api/v1/local-vision/status` returned HTTP 200 READY. POST `/api/v1/local-inspections` reached its **60-second application transport deadline** and returned HTTP 200 with domain outcome **FAILED / RUNTIME_UNAVAILABLE** after **60.115 seconds**. Images, findings and model provenance were withheld, and non-cacheable headers were retained. No mock fallback or partial model text was released.

The local server log shows actual CPU image processing followed by token generation, but no completed structured response before the deadline. Therefore no semantic comparison or finding-quality conclusion is possible for this candidate from this attempt. A successfully installed vision-capable model is not the same as a successful application analysis. This cold-start CPU timeout does not prove the model cannot work on other hardware or with a separately validated runtime configuration, and no such performance claim is made.

At that point, no further model requests or candidates were attempted; the separately authorized diagnosed-failure fix and single retry are recorded below. The owned second-candidate runtime was stopped with SIGTERM, port 11434 was verified closed, and no Ollama/llama-server process remained. Runtime/weights remain available only as ignored local files for separately authorized follow-up.

**Release consequence:** neither candidate is established as a reliable automotive-analysis default by these experiments. The first executes but showed semantic weaknesses; the second did not complete the bounded API operation. Keep the feature optional, experimental and default-disabled. These results are concrete engineering evidence and unresolved acceptance work, not a finished automatic-inspection claim.


## Final diagnosed-failure fix and single full-chain retry

The previous real timeout exposed a concrete implementation limit rather than an unavailable model. The bounded chat deadline was increased to **180 seconds**, generation was capped at **1,000 tokens**, and a concise vehicle-specific prompt explicitly requests empty findings when no vehicle/component is visible. The request retains `think: false` and supplies no tools. Prompt provenance changed to **`visible-evidence-v2`**, preserving the distinction from the earlier prompt. Focused contract tests were rerun by the backend agent.

The root agent separately identified the Next.js proxy's default 30-second timeout, which would cut off an otherwise valid local inference from the browser. It configured a finite **210-second proxy timeout**, built the production frontend, and started task-owned Next.js and FastAPI instances. No further model or runtime download was required.

Exactly one final inference request used actual HTTP through **Next.js production port 3000 → FastAPI port 8000 → cloud-disabled local Ollama port 11434**. It used the same owned source image and image permission. The request was not intercepted or replaced by a transport fixture.

| Final check | Observed result |
| --- | --- |
| Client request | HTTP 200, `Cache-Control: no-store, max-age=0` |
| End-to-end wall time | **46.325 seconds**; the response actually exceeded the old 30-second proxy cutoff and still reached the client |
| Application result | `COMPLETED` / `LOCAL_EXPERIMENT_COMPLETED`; `UNVERIFIED` identity and `EXPERIMENTAL_UNREVIEWED` status retained |
| Actual model | `qwen3-vl:2b`, digest `0635d9d857d497aeadba3d7d27485746c50554446f9f6ec01ef39788221adbe8`, prompt `visible-evidence-v2` |
| Actual image evidence | Source `ff340c88aaf831761b0284eacd7bde13ccda53a0d385b2976147666bea3fef72`; inference `792e75ac74f2631135c0a7c9dfbd67efe849f301f968299970ca9cb8337c76a0` |
| Model output | Empty findings; limitation correctly states no vehicle/component is visible and describes the red square and blue circle as synthetic test elements |
| Physical checks | All six systems remain UNKNOWN |
| Reported usage | 1,240 prompt tokens, 178 generated tokens; no invented dollar cost |

The model's actual limitation was: “No vehicle or identifiable vehicle component is visible in the image. The image shows only a red square and blue circle labeled 'RED BOX / BLUE CIRCLE', which are synthetic test elements and not related to a vehicle.” This is stronger instruction-following and abstention evidence on this one engineering input than the first model's label-echo output. It is not a measured automotive benchmark, proof of damage recall or assurance for other images/hardware. Increasing a deadline alone was not described as an accuracy fix.

After this single final request the task-owned Ollama server was stopped cleanly; the root owns stopping its separate web/API processes. Port 11434 was checked closed. The exact final response remains ignored under `.cache/ollama/smoke/qwen3vl-proxy-retry-response.json`. No further requests or candidates are planned by this smoke task.

The optional local-model capability now has an actual completed production-proxy path, while the broader release boundary stays explicit: model installation/hardware is required, runtime deadlines are finite, real vehicle quality is not evaluated here, and the feature remains experimental/default-disabled. The original automatic auction-data access and automotive-validation gates are unchanged.
