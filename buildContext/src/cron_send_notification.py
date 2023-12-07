import time
from apscheduler.schedulers.blocking import BlockingScheduler
from blueprints.notifier.job_notifier import Process_Notifier


if __name__=="__main__":

    notifier = Process_Notifier()
    notifier.process_notification()
   
    # scheduler = BlockingScheduler({'apscheduler.job_defaults.max_instances': 2})
    # scheduler.add_job(notifier.process_notification, 'interval', minutes=10)
    # scheduler.start()
