import pathlib

root = pathlib.Path(r"D:\ComfyTesla124\.venv\Lib\site-packages\comfy_kitchen")

fixed = 0
for path in root.rglob("*.py"):
    lines = path.read_text(encoding="utf-8").split("\n")
    text = "\n".join(lines)

    needs_module = "typing." in text
    has_module_import = any(l.strip().startswith("import typing") for l in lines)

    if needs_module and not has_module_import:
        # вставляем import typing: после from __future__, иначе в самое начало
        idx = 0
        for i, l in enumerate(lines):
            if l.startswith("from __future__"):
                idx = i + 1
                break
        lines.insert(idx, "import typing")
        path.write_text("\n".join(lines), encoding="utf-8")
        fixed += 1
        print("Added import typing:", path)

print("Files fixed:", fixed)
