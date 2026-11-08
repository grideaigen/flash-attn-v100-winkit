import pathlib

root = pathlib.Path(r"D:\ComfyTesla124\.venv\Lib\site-packages\comfy_kitchen")

for path in root.rglob("*.py"):
    lines = path.read_text(encoding="utf-8").split("\n")
    original = lines[:]

    # 1) убираем ранее вставленные строки "import typing"
    lines = [l for l in lines if l.strip() != "import typing"]

    # 2) если файл использует typing.* и не имеет импорта — вставляем в начало
    text = "\n".join(lines)
    if "typing." in text:
        has_import = any(
            l.strip().startswith(("import typing", "from typing import"))
            for l in lines
        )
        if not has_import:
            idx = 0
            for i, l in enumerate(lines):
                if l.startswith("from __future__"):
                    idx = i + 1
                    break
            lines.insert(idx, "import typing")

    if lines != original:
        path.write_text("\n".join(lines), encoding="utf-8")
        print("Fixed:", path)

print("Done")
