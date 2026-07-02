# -*- coding: utf-8 -*-
"""Diagnostic: capture real captcha images + OCR reads + server login response.
Commits results to captcha_samples/ so they can be inspected without artifact access.
"""
import os
import re
import json
import base64
from playwright.sync_api import sync_playwright

OUT = "captcha_samples"
os.makedirs(OUT, exist_ok=True)

results = {"images": [], "attempts": []}


def main():
    import easyocr
    reader = easyocr.Reader(['en'], gpu=False, verbose=False)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(60_000)

        page.goto("https://mtcbusits.in/")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=f"{OUT}/login_page.png", full_page=True)

        # Info about every <img> on the page, to identify which one is the captcha
        results["imgs_info"] = page.evaluate(
            """() => Array.from(document.querySelectorAll('img')).map(i => ({
                src_prefix: (i.getAttribute('src')||'').slice(0,50),
                w: i.naturalWidth, h: i.naturalHeight,
                cls: i.className, id: i.id, alt: i.alt
            }))"""
        )

        # Does the old DOM-text captcha span still exist?
        try:
            spans = page.locator("span.input-group-addon")
            results["span_input_group_addon"] = [
                spans.nth(i).inner_text(timeout=2000) for i in range(spans.count())
            ]
        except Exception as e:
            results["span_input_group_addon_error"] = str(e)

        # Capture 8 captcha samples with full OCR detail
        for i in range(1, 9):
            src = page.get_attribute('img[src^="data:image"]', "src")
            if not src:
                results["images"].append({"n": i, "error": "no data:image found"})
                break
            img_bytes = base64.b64decode(src.split(",")[1])
            with open(f"{OUT}/captcha_{i:02d}.png", "wb") as f:
                f.write(img_bytes)
            det = reader.readtext(img_bytes, detail=1, mag_ratio=2)
            boxes = [{"text": t, "conf": round(float(c), 3)} for (_, t, c) in det]
            joined = re.sub(r'[^A-Za-z0-9]', '', "".join(t for (_, t, _) in det))
            results["images"].append({"n": i, "bytes": len(img_bytes), "boxes": boxes, "joined": joined})
            print(f"captcha_{i:02d}: boxes={boxes} joined={joined}")

            # refresh captcha for next sample
            old = src
            try:
                page.locator(".k-i-reload").click(timeout=3000)
            except Exception:
                page.reload()
                page.wait_for_load_state("networkidle")
            for _ in range(25):
                page.wait_for_timeout(200)
                new = page.get_attribute('img[src^="data:image"]', "src")
                if new and new != old:
                    break

        # ONE real login attempt, to capture the server's actual response/error
        page.fill("input[name='UserName']", "neelan.ibi")
        page.fill("input[id='password']", os.environ.get("LOGIN_PASSWORD", "Neelan@123"))
        src = page.get_attribute('img[src^="data:image"]', "src")
        guess = ""
        if src:
            img_bytes = base64.b64decode(src.split(",")[1])
            with open(f"{OUT}/attempt_captcha.png", "wb") as f:
                f.write(img_bytes)
            det = reader.readtext(img_bytes, detail=0, mag_ratio=2)
            guess = re.sub(r'[^A-Za-z0-9]', '', "".join(det))
        page.fill("input[formcontrolname='captcha']", guess)
        page.click("button:has-text('Login')")
        page.wait_for_timeout(5000)
        results["attempts"].append({"guess": guess, "url_after": page.url})
        page.screenshot(path=f"{OUT}/after_login_attempt.png", full_page=True)
        try:
            body_text = page.inner_text("body")[:3000]
        except Exception:
            body_text = ""
        with open(f"{OUT}/after_login_body.txt", "w", encoding="utf-8") as f:
            f.write(body_text)

        browser.close()

    with open(f"{OUT}/results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
