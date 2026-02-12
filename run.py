#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform
import shlex

REQUIRED_PYTHON = (3, 11)
VENV_DIR = 'venv'
REQUIREMENTS = 'requirements.txt'
ENV_EXAMPLE = '.env.example'
ENV_FILE = '.env'


def is_python_compatible(python_exe):
    try:
        out = subprocess.check_output([python_exe, '--version'], stderr=subprocess.STDOUT, text=True)
        version_str = out.strip().split()[1]
        major, minor, *_ = version_str.split('.')
        return (int(major), int(minor)) == REQUIRED_PYTHON
    except Exception:
        return False


def find_python_311():
    # 1. Hozirgi Python yetarlimi
    if sys.version_info[:2] == REQUIRED_PYTHON:
        return None

    # 2. Windows registry
    if os.name == 'nt':
        try:
            import winreg
            for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                with winreg.OpenKey(root, r"SOFTWARE\Python\PythonCore") as pythoncore:
                    for i in range(winreg.QueryInfoKey(pythoncore)[0]):
                        version = winreg.EnumKey(pythoncore, i)
                        if version.startswith(f"{REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}"):
                            with winreg.OpenKey(pythoncore, version + r"\InstallPath") as installpath:
                                path, _ = winreg.QueryValueEx(installpath, None)
                                exe = os.path.join(path, 'python.exe')
                                if os.path.exists(exe):
                                    return exe
        except Exception:
            pass
        # Py launcher fallback
        # First, check if 'py -3.11' works
        try:
            out = subprocess.check_output(['py', '-3.11', '--version'], stderr=subprocess.STDOUT, text=True)
            version_str = out.strip().split()[1]
            major, minor, *_ = version_str.split('.')
            if (int(major), int(minor)) == REQUIRED_PYTHON:
                return 'py -3.11'
        except Exception:
            pass
        candidates = ['python3.11', 'python']
    else:
        # Linux/Mac
        candidates = ['python3.11', 'python3', 'python']

    # 3. Tekshirish
    for cmd in candidates:
        try:
            # Agar bo‘sh joyli buyruq bo‘lsa, shlex.split ishlatamiz
            cmd_list = shlex.split(cmd)
            out = subprocess.check_output(cmd_list + ['--version'], stderr=subprocess.STDOUT, text=True)
            version_str = out.strip().split()[1]
            major, minor, *_ = version_str.split('.')
            if (int(major), int(minor)) == REQUIRED_PYTHON:
                return cmd_list[0]  # Faqat exe yo‘lini qaytaramiz
        except Exception:
            continue

    return None


def create_venv(python_exec):
    if not Path(VENV_DIR).exists():
        print(f"[INFO] Virtual muhit yaratilmoqda... ({python_exec})")
        subprocess.check_call([python_exec, '-m', 'venv', VENV_DIR])
    else:
        print("[INFO] Virtual muhit allaqachon mavjud.")


def install_requirements():
    python_path = Path(VENV_DIR) / ('Scripts' if os.name == 'nt' else 'bin') / ('python.exe' if os.name == 'nt' else 'python')
    print("[INFO] Kutubxonalar o'rnatilmoqda...")
    try:
        subprocess.check_call([str(python_path), '-m', 'pip', 'install', '--upgrade', 'pip'])
        subprocess.check_call([str(python_path), '-m', 'pip', 'install', '-r', REQUIREMENTS])
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Kutubxonalarni o'rnatishda xato: {e}")
        sys.exit(1)


def create_env_file():
    if not Path(ENV_FILE).exists() and Path(ENV_EXAMPLE).exists():
        shutil.copy(ENV_EXAMPLE, ENV_FILE)
        print(f"[INFO] {ENV_FILE} fayli {ENV_EXAMPLE} asosida yaratildi.")
    elif Path(ENV_FILE).exists():
        print(f"[INFO] {ENV_FILE} allaqachon mavjud.")
    else:
        print(f"[WARNING] {ENV_EXAMPLE} topilmadi, {ENV_FILE} yaratilmaydi.")


def main():
    # Avval hozirgi python versiyasini tekshiramiz
    print(f"[DEBUG] sys.executable: {sys.executable}, sys.version_info: {sys.version_info}")
    if sys.version_info[:2] == REQUIRED_PYTHON:
        print(f"[INFO] Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]} detected. Running main logic.")
        create_venv(sys.executable)
        install_requirements()
        create_env_file()

        print("\n[OK] Hammasi tayyor! Loyihani ishga tushirish uchun venv aktivlashtiring:")
        if os.name == 'nt':
            print(f"  Windows:   {VENV_DIR}\\Scripts\\activate")
        else:
            print(f"  Linux/Mac: source {VENV_DIR}/bin/activate")

        # Loyihani avtomatik ishga tushirish
        print("[INFO] Bot avtomatik ishga tushmoqda...")
        bot_main = Path('bot') / 'main.py'
        if bot_main.exists():
            if os.name == 'nt':
                venv_python = Path(VENV_DIR) / 'Scripts' / 'python.exe'
            else:
                venv_python = Path(VENV_DIR) / 'bin' / 'python'
            subprocess.check_call([str(venv_python), '-m', 'bot.main'], cwd=os.getcwd())
        else:
            print("[WARNING] bot/main.py topilmadi, bot avtomatik ishga tushmadi.")
    else:
        python_exec = find_python_311()
        print(f"[DEBUG] python_exec: {python_exec}")
        if python_exec is None:
            print(f"[ERROR] Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]} topilmadi.")
            print(f"O'rnatilgan versiya: {sys.version.split()[0]}")
            sys.exit(1)
        print(f"[INFO] Skript Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]} bilan qayta ishga tushirilmoqda...")
        import shlex
        if python_exec.endswith('python.exe') and os.path.exists(python_exec):
            os.execv(python_exec, [python_exec] + sys.argv)
        elif python_exec == 'py -3.11':
            subprocess.check_call(['py', '-3.11'] + sys.argv)
        else:
            subprocess.check_call(shlex.split(python_exec) + sys.argv)
        sys.exit(0)


if __name__ == "__main__":
    main()
