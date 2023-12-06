import time
from apscheduler.schedulers.blocking import BlockingScheduler
from blueprints.notifier.util import Util


if __name__=="__main__":

    util = Util()
    util.setup_notifications()
   
    # scheduler = BlockingScheduler({'apscheduler.job_defaults.max_instances': 2})
    # scheduler.add_job(util.setup_notifications, 'interval', minutes=5)
    # scheduler.start()
