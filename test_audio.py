from pathlib import Path

sounds_dir = Path("sounds/packs/default")

print(f"Looking in: {sounds_dir.absolute()}")
print(f"Exists: {sounds_dir.exists()}")

if sounds_dir.exists():
    for category in ["elimination", "countdown", "winner"]:
        folder = sounds_dir / category
        print(f"\n{category}/")
        print(f"  Exists: {folder.exists()}")
        if folder.exists():
            files = list(folder.iterdir())
            print(f"  Files: {files}")
