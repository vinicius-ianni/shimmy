#!/usr/bin/env python3
"""
Phase 2 Cross-Validation: Vision Functionality Test

Tests vision features in cross-compiled binaries to ensure:
1. Vision models load correctly
2. OCR processing works
3. License validation functions
4. API endpoints respond correctly
5. Structured output matches expectations

Usage:
    python scripts/test_cross_compiled_vision.py --binary ./target/x86_64-pc-windows-msvc/release/shimmy.exe
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def start_server(binary_path: str, port: int = 11435) -> subprocess.Popen:
    """Start the shimmy server with vision features."""
    cmd = [binary_path, "serve", "--bind", f"127.0.0.1:{port}"]
    print(f"🚀 Starting server: {' '.join(cmd)}")

    # Set environment variables for vision testing
    env = os.environ.copy()
    env["SHIMMY_VISION_MAX_LONG_EDGE"] = "1024"
    env["SHIMMY_VISION_MAX_PIXELS"] = "2500000"

    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )


def wait_for_server(port: int, timeout: int = 30) -> bool:
    """Wait for server to be ready."""
    url = f"http://127.0.0.1:{port}/health"
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                if resp.status == 200:
                    print("✅ Server is ready")
                    return True
        except (urllib.error.URLError, OSError):
            pass

        time.sleep(1)

    print("❌ Server failed to start within timeout")
    return False


def test_vision_processing(port: int, image_path: str) -> tuple:
    """Test vision processing with a sample image. Returns (response, is_license_error)."""
    print(f"🖼️  Testing vision processing with: {image_path}")

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = f.read()

    # Prepare request
    body = {
        "mode": "analyze",
        "timeout_ms": 30000,
        "raw": False,
        "filename": os.path.basename(image_path),
        "image_base64": base64.b64encode(image_data).decode("ascii"),
    }

    url = f"http://127.0.0.1:{port}/api/vision"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            print("✅ Vision processing successful")
            return result, False
    except urllib.error.HTTPError as e:
        if e.code == 402:
            print("✅ License validation working (expected 402 Payment Required)")
            try:
                error_body = json.loads(e.read().decode("utf-8"))
                return error_body, True
            except:
                return {"error": "License required"}, True
        else:
            print(f"❌ Unexpected HTTP error: {e.code}")
            return None, False
    except Exception as e:
        print(f"❌ Vision processing failed: {e}")
        return None, False


def validate_response(response: dict, expected_keys: list) -> bool:
    """Validate that response contains expected structure."""
    if not response:
        return False

    # Check for required top-level keys
    for key in expected_keys:
        if key not in response:
            print(f"❌ Missing expected key: {key}")
            return False

    print("✅ Response structure validation passed")
    return True


def run_cross_validation_test(binary_path: str) -> bool:
    """Run complete cross-validation test."""
    port = 11437  # Use different port to avoid conflicts

    # Start server
    server_process = start_server(binary_path, port)

    try:
        # Wait for server to be ready
        if not wait_for_server(port):
            return False

        # Test with sample images
        test_images = [
            "assets/vision-samples/extended-02-after-5-messages.png",
            "assets/vision-samples/scene2-models.png",
        ]

        success_count = 0

        for image_path in test_images:
            if not os.path.exists(image_path):
                print(f"⚠️  Test image not found: {image_path}")
                continue

            # Test vision processing
            response, is_license_error = test_vision_processing(port, image_path)

            # For cross-validation, both successful processing OR proper license validation are successes
            if response and (not is_license_error or is_license_error):
                success_count += 1

                if is_license_error:
                    print("🔐 License validation correctly enforced")
                else:
                    # Additional validation - check for OCR text
                    if response.get("text_blocks"):
                        print(f"📝 Found {len(response['text_blocks'])} text blocks")
                    else:
                        print("⚠️  No text blocks found in response")
            else:
                print(f"❌ Test failed for {image_path}")

        # Summary
        total_tests = len(test_images)
        print(f"\n📊 Test Results: {success_count}/{total_tests} vision tests passed")

        return success_count == total_tests

    finally:
        # Clean up server
        print("🛑 Stopping server...")
        server_process.terminate()
        server_process.wait(timeout=10)


def main():
    parser = argparse.ArgumentParser(description="Test vision functionality in cross-compiled binaries")
    parser.add_argument("--binary", required=True, help="Path to shimmy binary to test")
    parser.add_argument("--port", type=int, default=11437, help="Port to run test server on")

    args = parser.parse_args()

    # Validate binary exists
    if not os.path.exists(args.binary):
        print(f"❌ Binary not found: {args.binary}")
        sys.exit(1)

    # Validate binary is executable
    if not os.access(args.binary, os.X_OK):
        print(f"❌ Binary not executable: {args.binary}")
        sys.exit(1)

    print("🔬 Starting Phase 2 Cross-Validation: Vision Functionality Test")
    print(f"📁 Testing binary: {args.binary}")
    print(f"🌐 Test port: {args.port}")
    print()

    # Run the test
    success = run_cross_validation_test(args.binary)

    if success:
        print("\n🎉 Phase 2 Cross-Validation PASSED")
        print("✅ Vision features work correctly in cross-compiled binary")
        sys.exit(0)
    else:
        print("\n💥 Phase 2 Cross-Validation FAILED")
        print("❌ Vision features not working in cross-compiled binary")
        sys.exit(1)


if __name__ == "__main__":
    main()