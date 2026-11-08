Цель
Быстро и без сюрпризов развернуть flash-attn-v100 после переустановки системы/окружения, чтобы ComfyUI мог использовать оптимизированное внимание на V100 (sm_70).

Что должно быть в архиве
flash-attn-v100-source.zip — папка с исходниками (включая уже исправленный include/mat_mul.h).
build_v100.bat — твой скрипт сборки.
requirements_flash_attn.txt — список зависимостей.
smoke_test.py — тест forward/backward.
notes-flash-attn-fix.txt — краткая памятка: «__tanhf → tanhf», «MAX_JOBS=4».
Шаг 1. Подготовка системы (до окружения)
Visual Studio Build Tools 2022 (MSVC 14.38):
Компоненты: MSVC v143 — VS 2022 C++ x64/x86 build tools, Windows 10/11 SDK, CMake tools.
CUDA Toolkit 12.4 — строго эта версия (совместима с torch 2.6.0+cu124).
Python 3.12 — та же мажорная/минорная версия, что и в текущем .venv.
Ninja (опционально, но ускоряет сборку): pip install ninja.
Шаг 2. Создание и активация окружения
powershell
python -m venv D:\ComfyTesla124\.venv
D:\ComfyTesla124\.venv\Scripts\Activate.ps1
Шаг 3. Установка зависимостей
powershell
pip install --upgrade pip setuptools wheel
pip install -r D:\путь_к_архиву\requirements_flash_attn.txt
Важно: в requirements должен быть torch==2.6.0+cu124 (или совместимый под CUDA 12.4). Если ставишь новый torch — потом придётся пересобрать flash-attn.

Шаг 4. Распаковка и подготовка исходников
Распакуй flash-attn-v100-source.zip в D:\tmp\flash-attn-v100.
Проверь правку в include/mat_mul.h:
powershell
(Get-Content D:\tmp\flash-attn-v100\include\mat_mul.h) -replace '__tanhf', 'tanhf' | Set-Content D:\tmp\flash-attn-v100\include\mat_mul.h
В build_v100.bat установи ограничение параллелизма:
bat
set MAX_JOBS=4
Шаг 5. Сборка и установка
powershell
cd D:\tmp\flash-attn-v100
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
.\build_v100.bat > build.log 2>&1
Проверь build.log: не должно быть ошибок компиляции/линковки. Успех — это наличие flash_attn_v100_cuda.cp312-win_amd64.pyd в папке сборки и копирование его в site-packages.

Шаг 6. Проверка импорта
powershell
python -c "import flash_attn_v100; print('OK:', flash_attn_v100.__file__)"
Путь должен вести в D:\ComfyTesla124\.venv\Lib\site-packages\flash_attn_v100\__init__.py.

Шаг 7. Smoke-тест (forward + backward)
powershell
python D:\путь_к\smoke_test.py
Ожидаемый вывод:

text
forward OK: torch.Size([2, 256, 8, 64]) torch.float16 | lse: torch.Size(...)
backward OK: loss = ... | dq: (2, 256, 8, 64) dk: ... dv: ...
Если видишь эти строки — модуль полностью рабочий.

Шаг 8. Проверка в ComfyUI
Убедись, что ComfyUI запускается из этого .venv (D:\ComfyTesla124\.venv).
Если используешь кастомные ноды (H3 и т.п.) — они не включат flash_attn_v100 автоматически. Для ускорения нужно явно вызывать flash_attn_func в коде ноды.
Если есть совместимые бэкенды (comfy-kitchen и аналоги) — проверь логи запуска ComfyUI на строки вроде Flash Attention backend: flash_attn_v100.
Частые проблемы и быстрые решения
Проблема	Решение
Ошибка __tanhf / tanhf	Перепроверь замену в include/mat_mul.h.
Линковка падает, много параллельных задач	Установи set MAX_JOBS=4 в build_v100.bat.
ModuleNotFoundError: No module named 'flash_attn_v100'	Проверь, что запускаешь из активированного .venv и путь к site-packages верный.
CUDA kernel not found	Проверь torch.cuda.is_available() и compute capability: python -c "import torch; print(torch.cuda.get_device_capability())" (должно быть (7, 0) для V100).
После обновления torch модуль не работает	Пересобери flash-attn-v100 заново — он линкуется к конкретной torch.lib.
Важные примечания
Не копируй site-packages целиком между системами — это почти всегда ломается. Сохраняй только исходники + инструкцию.
Comfy Desktop / кастомные сборки: если ComfyUI использует своё окружение, убедись, что flash-attn-v100 установлен именно туда.
Minimax H3 ноды: flash-attn-v100 — это низкоуровневый модуль. Ноды вроде H3VSAAttention используют свои схемы внимания и не подхватят его автоматически.
Этот файл можно положить рядом с архивом и при необходимости быстро восстановить рабочее окружение. Если хочешь, могу ещё сделать короткий вариант на 1 страницу (только команды без пояснений) — чтобы просто копировать и вставлять. Что ближе? 😊


 «после обновления ComfyUI повторить патч comfy_kitchen (fix_kitchen.py + fix_kitchen2.py лежат в D:\tmp)» — сэкономит будущему тебе добрый час.