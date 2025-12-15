# Shimmy Vision — Production Readiness Checklist

> Last audit: 2025-01-xx by Copilot  
> Target: 95%+ production ready before private crate split

---

## ✅ COMPLETED — Blocking items resolved

### 1. Test Files Testing Removed Dev Mode Bypass
**Status:** ✅ FIXED  
**What was done:**
- Removed `test_dev_mode_bypasses_all_license_checks()` from `vision_license_flow_tests.rs`
- Removed `test_dev_mode_bypass()` from `vision_license_simple_tests.rs`
- Removed `test_check_vision_access_dev_mode_bypass()` from `vision_license_tests.rs`
- Updated `vision_api_integration.rs` to use pre-seeded license cache instead of dev mode bypass
- Added helper `create_test_router_with_license()` for tests needing valid license context

---

### 2. VS Code Tasks Updated
**Status:** ✅ FIXED  
**What was done:**
- Removed `SHIMMY_VISION_DEV_MODE=1` from all task commands in `.vscode/tasks.json`
- Tasks now use standard licensing (require valid license or env var)

---

### 3. Docs Updated
**Status:** ✅ FIXED  
**What was done:**
- Removed `SHIMMY_VISION_DEV_MODE=1` from `docs/vision-timings.md` example commands

---

### 4. Obsolete Analysis File
**Status:** ✅ DELETED  
**What was done:**
- Deleted `VISION_LICENSE_TEST_COVERAGE_ANALYSIS.md`

---

## 🟡 HIGH PRIORITY — Should fix before release

### 5. Private Crate Migration (source protection)
**Status:** Not started  
**Documented in:** `docs/VISION_PRIVATE_SPLIT_REPORT.md`

**Steps:**
1. Create private GitHub repo `shimmy-vision-private`
2. Extract `src/vision.rs` and `src/vision_license.rs` (~2,073 lines total)
3. Create public adapter trait `VisionProvider` in main repo
4. Add optional git dependency in public `Cargo.toml`:
   ```toml
   [dependencies.shimmy-vision]
   git = "git@github.com:yourorg/shimmy-vision-private.git"
   optional = true
   ```
5. Set up CI with deploy key for private repo access
6. Update feature flags: `vision = ["shimmy-vision"]`
7. Test that `cargo build --features vision` fails without private repo access

---

### 6. License Verification Before Model Download
**Status:** UNVERIFIED — punch list item  
**Requirement:** License check must happen BEFORE any HuggingFace model download begins.

**Action:** Add integration test that mocks HF download and confirms license error fires first.

---

### 7. End-to-End Functional Test Script
**Status:** Missing  
**From punch list:** "Add an end-to-end functional test script that starts `serve-vision-gpu` and runs 1 image + 1 URL request"

**Action:** Create `scripts/vision-e2e-test.sh` that:
1. Starts vision server via task
2. Waits for health check
3. Sends test image request
4. Sends test URL request (to allowed domain)
5. Validates response structure
6. Exits with clear pass/fail

---

## 🟢 RECOMMENDED — Nice to have before release

### 8. Resumable Model Downloads
**Status:** Not implemented  
**Impact:** Better UX for interrupted downloads (~5.7GB total)

**Action:** Implement HTTP range requests in `ensure_download_and_verify()`.

---

### 9. HTTP Rate Limiting for Vision API
**Status:** Not implemented  
**Impact:** Prevents abuse of `/api/vision` endpoint

**Action:** Add rate limiting middleware (especially for `--url` mode).

---

### 10. Structured Logging Fields
**Status:** Partial  
**From punch list:** "Add structured fields for: mode, image dimensions, duration, error category"

**Action:** Audit vision request logging path for consistent structured output.

---

### 11. Troubleshooting Documentation
**Status:** Missing  
**From punch list:** "Add troubleshooting section for: missing CUDA, missing Chromium, model checksum mismatch, and license validation failures"

**Action:** Add to `docs/SHIMMY_VISION_SPEC.md` or create `docs/VISION_TROUBLESHOOTING.md`.

---

## ✅ VERIFIED — Already done

### Production Code Clean
- [x] No `SHIMMY_VISION_DEV_MODE` bypass in `src/vision.rs`
- [x] No `SHIMMY_VISION_DEV_MODE` bypass in `src/vision_license.rs`
- [x] `check_vision_access()` always enforces license
- [x] `api.rs` uses dev mode only for error verbosity (not bypass)

### Security Hardening
- [x] SSRF protections (localhost/private IP blocking)
- [x] URL fetch size limit (25MB)
- [x] URL fetch timeout (30s)
- [x] Web mode page load timeout (60s)
- [x] Domain allowlist enforcement

### Model Bootstrap
- [x] HuggingFace download with SHA256 verification
- [x] In-process download lock (prevents concurrent downloads)
- [x] Hard-locked to MiniCPM-V model

### Licensing
- [x] Keygen integration with Ed25519 signature verification
- [x] Hard-coded account ID (prevents key-swapping)
- [x] License caching with 24h grace period
- [x] Usage metering with monthly reset

### Clippy
- [x] `cargo clippy --features llama,vision -- -D warnings` passes

---

## Deterministic Execution Order

Run these in order to reach production readiness:

```bash
# 1. Fix broken tests
# Delete dev-mode-bypass tests from:
#   - tests/vision_license_flow_tests.rs
# 1. Tests already fixed (see section above)

# 2. tasks.json already fixed (see section above)

# 3. docs/vision-timings.md already fixed (see section above)

# 4. Obsolete analysis file already deleted

# 5. Run test suite
cargo test --features llama,vision --lib -- vision

# 6. Run clippy
cargo clippy --features llama,vision -- -D warnings

# 7. Verify license flow manually
# Export SHIMMY_LICENSE_KEY=<your-test-key>
# Run shimmy vision --image test.png --mode ocr

# 8. Create private repo and extract vision code (separate workflow)
```

---

## Files Summary

| Category | Files | Status |
|----------|-------|--------|
| Production code | `src/vision.rs`, `src/vision_license.rs`, `src/api.rs` | ✅ Clean |
| Tests | `tests/vision_*.rs` (4 files) | ✅ Fixed |
| Tasks | `.vscode/tasks.json` | ✅ Fixed |
| Docs | `docs/vision-timings.md` | ✅ Fixed |
| Analysis | `VISION_LICENSE_TEST_COVERAGE_ANALYSIS.md` | ✅ Deleted |

---

*Generated by production audit. All blocking items resolved.*
*Remaining: Private crate migration (HIGH PRIORITY) and nice-to-have items.*
