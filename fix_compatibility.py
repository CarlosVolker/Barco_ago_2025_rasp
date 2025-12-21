import os
import site
import sys

def patch_aiortc():
    """
    Parches aiortc files to Fix Import Paths
    """
    # 1. Locate aiortc
    aiortc_path = None
    try:
        import aiortc
        aiortc_path = os.path.dirname(aiortc.__file__)
    except ImportError:
        for p in site.getsitepackages():
            candidate = os.path.join(p, "aiortc")
            if os.path.exists(candidate):
                aiortc_path = candidate
                break

    if not aiortc_path or not os.path.exists(aiortc_path):
        print("❌ Error: Could not find 'aiortc' installed folder.")
        sys.exit(1)

    print(f"📍 Found aiortc at: {aiortc_path}")

    # 2. Patch paths
    count = 0
    replacements = {
        # Fix paths where CodecContext lives now
        "from av.video.codeccontext": "from av.codec.context",
        "from av.audio.codeccontext": "from av.codec.context",
        # Ensure imports point to the correct submodules
        "import av.video.codeccontext": "import av.codec.context",
        "import av.audio.codeccontext": "import av.codec.context"
    }

    for root, dirs, files in os.walk(aiortc_path):
        for name in files:
            if name.endswith(".py"):
                path = os.path.join(root, name)
                with open(path, "r", encoding="utf-8") as f:
                    data = f.read()
                
                new_data = data
                changed = False
                for src, dst in replacements.items():
                    if src in new_data:
                        new_data = new_data.replace(src, dst)
                        changed = True
                
                if changed:
                    print(f"🔧 Patching imports in {name}...")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_data)
                    count += 1
    
    if count > 0:
        print(f"✅ Success! Updated imports in {count} files.")
    else:
        print("⚠️ No more path replacements needed (or files already patched).")

if __name__ == "__main__":
    patch_aiortc()
