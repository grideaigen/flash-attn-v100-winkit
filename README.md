# flash-attn-v100 — Windows Native Build Kit

Unofficial helper kit to build [ai-bond/flash-attention-v100](https://github.com/ai-bond/flash-attention-v100) **natively on Windows** (no WSL) for NVIDIA Tesla V100 (sm_70).

**All credit for the FlashAttention-2 kernel implementation belongs to the upstream author
(D. Skryabin, [@ai_bond007](https://t.me/ai_bond007)), BSD 3-Clause.**
This repository contains *only* Windows build fixes and tooling.

## Verified on

| Component | Version |
|---|---|
| Upstream commit | tag `26.10` (`0ababf8`), also applies cleanly to `main` @ `838ec64` (2026-11-08) |
| OS | Windows 10 x64 (build 22631) |
| Python | 3.12 |
| PyTorch | 2.6.0+cu124 |
| CUDA Toolkit | 12.4 |
| Compiler | MSVC 14.38 (VS 2022 17.8+ / VS 18 Insiders) |

Other combinations were **not** tested.

## The fixes (see `0001-fix-msvc-build.patch`)

1. `include/mat_mul.h` — `__tanhf` → `tanhf` (2 places): `__tanhf` is not a device
   function under MSVC, nvcc fails to compile.
2. `setup.py` — added `-Dushort=unsigned short` nvcc flag: the `ushort` typedef
   from CUDA headers is not available under MSVC.
3. `setup.py` — CUDA version check relaxed from `12.9` to `12.4` (the module builds
   and passes smoke tests with torch 2.6.0+cu124).
4. `build_v100.bat` — `MAX_JOBS=4`: with full parallelism nvcc/link on Windows
   intermittently fails (OOM of the compiler process pool).

## Quick start

```bat
git clone https://github.com/ai-bond/flash-attention-v100.git
cd flash-attention-v100
git apply path\to\0001-fix-msvc-build.patch
:: edit settings at the top of build_v100.bat (VENV, REPO, CUDA_HOME)
build_v100.bat
```

Build takes ~15–25 min on a desktop CPU. Then verify:

```
python smoke_test.py
```

## Integrating with ComfyUI (portable / standalone builds)

The upstream project ships a Linux wheel only; native Windows was untested upstream
before this kit. Once installed (`python setup.py install`) into the venv that your
ComfyUI uses, the module appears as `flash_attn_v100` in site-packages.

If your ComfyUI ships the `comfy-kitchen` package, it may fail to import under
Windows because `import typing` is missing in several of its files. Fix:

```
python comfy-kitchen-fix\fix_kitchen2.py
```

(adjust the hardcoded path inside the script first). Re-run it after every
ComfyUI / comfy-kitchen update. No special launch script is needed — the attention
backend is picked up automatically through comfy-kitchen's backend registry.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `nvcc fatal: ... __tanhf` / `tanhf` redefinition errors | patch not applied — run `git apply 0001-fix-msvc-build.patch` |
| `'ushort' : undeclared identifier` | patch not applied (fix #2) |
| `CUDA version ... < 12.9 is not supported` | patch not applied (fix #3) |
| Build dies randomly mid-compile, or linker OOM | `MAX_JOBS=4` set? (fix #4); try `MAX_JOBS=2` |
| `cl` not found | run from the same shell after `vcvarsall.bat x64 -vcvars_ver=14.38` |
| torch reports a different CUDA | rebuild torch or install the matching CUDA Toolkit; mixing cu124 torch with CUDA 12.9 toolkit will not link |

## Files

- `0001-fix-msvc-build.patch` — all code fixes, applies with `git apply`
- `build_v100.bat` — one-shot build script (edit paths at the top)
- `smoke_test.py` — quick functional check after install
- `comfy-kitchen-fix/fix_kitchen2.py` — adds missing `import typing` to comfy-kitchen
- `requirements_flash_attn.txt` — minimal deps
- `requirements_freeze.txt` — exact environment snapshot used for the verified build
- `notes-flash-attn-fix.txt` — short changelog of what was broken and why

## License

Upstream code: BSD 3-Clause, (c) D. Skryabin / @ai_bond007 — see upstream repository.
This kit (build scripts, patches, docs): BSD 3-Clause, see `LICENSE`.
