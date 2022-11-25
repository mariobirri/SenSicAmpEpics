import subprocess

path = "/home/pi/SenSicAmpEpics/"
tasks = ['SenSicAmp_data.py', 'SenSicAmp_epics.py', 'SenSicAmp_Socket.py']

task_processes = [
    subprocess.Popen(r'python %s\%s' % (path, task), shell=True)
    for task
    in tasks
]
for task in task_processes:
    task.wait()
