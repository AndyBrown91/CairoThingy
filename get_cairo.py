from pathlib import Path
import sys
import os
from subprocess import Popen, PIPE, STDOUT


def get_script_dir():
    return Path(sys.path[0])


def is_windows():
    if not os.name == "nt":
        return "cygdrive" in os.getcwd()

    return True


def run_cmd(cmd, exit_on_failure=True, hide_output=False):
    if exit_on_failure:
        if "|" in cmd:
            cmd = cmd + "; test ${PIPESTATUS[0]} -eq 0"
        else:
            cmd = cmd + " || exit 1"

    try:
        lines = []

        with Popen(cmd, stdout=PIPE, stderr=STDOUT, bufsize=1, shell=True) as p:
            for line in p.stdout:
                line = line.decode('utf-8')

                if not hide_output:
                    print(line, end='')
                lines.append(line)

        if not p.returncode == 0 and exit_on_failure:
            print(cmd + " - Returned: " + str(p.returncode))
            exit(1)

        return [p.returncode, lines]
    except:
        print("Error executing cmd: " + cmd)

        if exit_on_failure:
            exit(1)

        return None


def check_application_exists(name):
    """Check whether `name` is on PATH and marked as executable."""
    from shutil import which

    return which(name) is not None


if not check_application_exists("git"):
    raise RuntimeError("Couldn't find git")

vcpkg_path = get_script_dir() / "vcpkg"

if not vcpkg_path.exists():
    print("-- Cloning vcpkg")
    run_cmd(f"git clone https://github.com/microsoft/vcpkg.git")

    for dirpath, dirnames, filenames in os.walk(vcpkg_path):
        os.chmod(dirpath, 0o777)
        for filename in filenames:
            os.chmod(os.path.join(dirpath, filename), 0o777)

extension = ".exe" if is_windows() else ""
vcpkg_exe = vcpkg_path / str("vcpkg" + extension)

if not vcpkg_exe.exists():
    print("-- Building vcpkg")
    bootstrap = "./vcpkg/bootstrap-vcpkg.bat" if is_windows() else "./vcpkg/bootstrap-vcpkg.sh"
    run_cmd(f"{get_script_dir() / bootstrap}")

print("-- Downloading required libraries")
libraries = ["cairo"]
triplet = "x64-windows-static" if is_windows() else "x64-osx"

for library in libraries:
    run_cmd(f"{vcpkg_exe} install {library} --triplet={triplet}")

libs_path = get_script_dir() / "external_libs"

if not libs_path.exists():
    os.symlink(vcpkg_path / "installed" / triplet, libs_path)

library_extension = ".lib" if is_windows() else ".a"
# Projucer doesn't let you specify different library names based on target (Debug/Release) - So rename the downloaded libraries
for f in Path(libs_path / "debug" / "lib").glob("*" + library_extension):
    if f.name.endswith("d" + library_extension):
        f.rename(str(f).replace("d" + library_extension, library_extension))

if is_windows():
    # libexpat doesn't follow the same pattern in that it tags an MD on the end
    libexpat = Path(libs_path / "debug" / "lib" / "libexpatdMD.lib")
    libexpat.rename(str(libexpat).replace("libexpatdMD.lib", "libexpatMD.lib"))
