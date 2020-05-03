import subprocess

from debug import get_logger
log = get_logger("default")

def run_shell_command_as_user(command, user='arkserver', shell=True, flatten_command=True):
    if flatten_command and isinstance(command, list):
        command = " ".join(command)
    log.debug(f"Running shell command: {command}; as user {user}")
    if user != 'root':
        cmd = f"""su - {user} -c '{command}'"""
    else:
        cmd = command
    try:
        cmd_out = subprocess.call(cmd, shell=True)#.decode("utf-8") #os.system(cmd)
    except subprocess.CalledProcessError as e:
        log.warning(f"Shell command '{cmd}' ran with errors.", exc_info=True)
        cmd_out = str(e.message)
    #cmd_out = check_output(cmd)
    log.debug(f"Shell command '{cmd}' exit code: {cmd_out}; code type {type(cmd_out)}; command ran without errors - {cmd_out == 0}")
    return cmd_out