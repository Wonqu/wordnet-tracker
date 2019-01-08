# based on https://gist.github.com/chenjianjx/53d8c2317f6023dc2fa0
import os
import time

import psutil
import subprocess

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


code_directory = '/app'
celery_working_dir = '/app'
celery_command = 'celery --app={project_name}.celery.celery worker --concurrency={num_workers} --loglevel={loglevel}'.format(
    project_name='tracker',
    num_workers=os.environ.get("CELERY_WORKERS_NUMBER", 1),
    loglevel=os.environ.get("CELERY_LOGLEVEL", 'debug')
).split(' ')


class TrackerHandler(PatternMatchingEventHandler):
    is_paused = False

    def __init__(self, *args, **kwargs):
        self.celery_command = kwargs.pop('celery_command', '')
        super().__init__(*args, **kwargs)

    def on_any_event(self, event):
        observer.pause()
        for proc in psutil.process_iter():
            proc_cmdline = self._get_proc_cmdline(proc)
            if proc_cmdline or len(proc_cmdline) < len(self.celery_command):
                continue

            is_celery_worker = all([
                'python' in proc_cmdline[0].lower(),
                self.celery_command[0] in proc_cmdline[0],
                self.celery_command[1] in proc_cmdline[1],
            ])

            if not is_celery_worker:
                continue

            proc.kill()
            # logger.info("Restarting Celery ...")

        run_worker()
        observer.resume()

    def _get_proc_cmdline(self, proc):
        try:
            return proc.cmdline()
        except Exception as e:
            return []


class PausingObserver(Observer):
    def dispatch_events(self, event_queue, timeout):
        if not getattr(self, '_is_paused', False):
            super().dispatch_events(event_queue, timeout)

    def pause(self):
        self._is_paused = True

    def resume(self):
        self.event_queue.queue.clear()
        self._is_paused = False


def run_worker():
    # logger.info("Starting Celery...")
    os.chdir(celery_working_dir)
    subprocess.Popen(celery_command)


if __name__ == "__main__":
    run_worker()

    event_handler = TrackerHandler(patterns=['*'], celery_command=celery_command)
    observer = PausingObserver()
    observer.schedule(event_handler, code_directory, recursive=True)
    observer.start()
    # logger.info("Watchdog Supervisor started.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
