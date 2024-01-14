from schedule import Scheduler
import threading
import time

from .models import Contest
from .api import YandexContestAPI, CodeforcesAPI


def process_all_contests():
    """
    Iterate through all contests in DB and process submits for each one.
    """
    contests = Contest.objects.all()
    for contest in contests:
        if contest.test_system == Contest.TestSystem.YANDEX_CONTEST:
            api = YandexContestAPI(contest)
        elif contest.test_system == Contest.TestSystem.CODEFORCES:
            api = CodeforcesAPI(contest)
        else:
            raise NotImplementedError
        api.process_all_submits()


def run_continuously(self, interval=1):
    """
    A new special function for Sheduler class to run in separate thread.
    """

    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.daemon = True
    continuous_thread.start()

    return cease_continuous_run


Scheduler.run_continuously = run_continuously


def start_scheduler():
    """
    Prepare scheduler with contest-processing job and start it.
    """
    scheduler = Scheduler()
    scheduler.every().minute.do(process_all_contests)
    scheduler.run_continuously()
