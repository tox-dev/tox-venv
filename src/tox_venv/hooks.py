import os
import subprocess

from tox.config import hookimpl


def real_python3(python):
    """
    use real_prefix to determine if we're running inside a virtualenv,
    and if so, use it as the base path to determine the real python
    executable path.
    """
    args = [str(python), '-c', 'import sys; print(sys.real_prefix)']

    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, _ = process.communicate()
    output = output.decode('UTF-8').strip()
    path = os.path.join(output, 'bin/python3')

    valid = process.returncode == 0 and os.path.isfile(path)
    return path if valid else python


@hookimpl
def tox_testenv_create(venv, action):
    # defautl to tox impl if not python3
    if not venv._ispython3():
        return

    config_interpreter = venv.getsupportedinterpreter()
    real_executable = real_python3(config_interpreter)

    args = [real_executable, '-m', 'venv']
    if venv.envconfig.sitepackages:
        args.append('--system-site-packages')
    if venv.envconfig.alwayscopy:
        args.append('--copies')

    venv.session.make_emptydir(venv.path)
    basepath = venv.path.dirpath()
    basepath.ensure(dir=1)
    args.append(venv.path.basename)
    venv._pcall(args, venv=False, action=action, cwd=basepath)
    # Return non-None to indicate the plugin has completed
    return True