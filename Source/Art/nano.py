"""Ask Google's Nano Banana image models for art, with reference images.

    GEMINI_API_KEY=... python3 Source/Art/nano.py OUT.png "prompt" [ref.png ...] [--model M] [--size 2K]

The key is read from the environment and never written anywhere. Writes the first image
the model returns to OUT.png and prints any text it sends back.
"""
import base64
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request

API = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent"


def generate(out, prompt, refs, model="gemini-3-pro-image", size="2K", aspect="1:1"):
    parts = [{"text": prompt}]
    for ref in refs:
        mime = mimetypes.guess_type(ref)[0] or "image/png"
        with open(ref, "rb") as f:
            parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(f.read()).decode()}})
    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"aspectRatio": aspect, "imageSize": size},
        },
    }
    req = urllib.request.Request(API % model, json.dumps(body).encode(), {
        "Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        print("HTTP %d: %s" % (e.code, e.read().decode(errors="replace")[:1500]))
        sys.exit(1)
    saved = False
    for cand in data.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            blob = part.get("inlineData") or part.get("inline_data")
            if blob and not saved:
                with open(out, "wb") as f:
                    f.write(base64.b64decode(blob["data"]))
                saved = True
            elif part.get("text") and not part.get("thought"):
                print(part["text"])
    if not saved:
        print(json.dumps(data)[:2000])
        sys.exit(1)
    print("wrote", out)


if __name__ == "__main__":
    args = sys.argv[1:]
    opts = {}
    for flag in ("--model", "--size", "--aspect"):
        if flag in args:
            i = args.index(flag)
            opts[flag[2:]] = args[i + 1]
            del args[i:i + 2]
    generate(args[0], args[1], args[2:], **opts)
