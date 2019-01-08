# based on https://gist.github.com/chenjianjx/53d8c2317f6023dc2fa0
import atexit
import os
import time
import subprocess

from celery_start import TrackerHandler, PausingObserver

code_directory = '/app'
celery_working_dir = '/app'
celery_command = 'celery --app={project_name}.celery.celery beat -s {path} --loglevel={loglevel} --max-interval={maxinterval} -S redbeat.RedBeatScheduler'.format(
    project_name='tracker',
    path="/home/celerybeat-schedule",
    loglevel=os.environ.get("CELERY_LOGLEVEL", 'debug'),
    maxinterval=os.environ.get("CELERYBEAT_MAX_LOOP_INTERVAL", 300)  # 300 is library default
).split(' ')


def run_worker():
    # logger.info("Starting Celery...")
    os.chdir(celery_working_dir)
    subprocess.Popen(celery_command)


def remove_pid():
    try:
        os.remove('celerybeat.pid')
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    remove_pid()
    run_worker()

    event_handler = TrackerHandler(patterns=['*'], celery_command=celery_command)
    observer = PausingObserver()
    observer.schedule(event_handler, code_directory, recursive=True)
    observer.start()
    atexit.register(remove_pid)
    # logger.info("Watchdog Supervisor started.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
