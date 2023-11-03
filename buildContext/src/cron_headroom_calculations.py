import time
from apscheduler.schedulers.blocking import BlockingScheduler
from blueprints.headrooms.headroom_util import Util


if __name__=="__main__":
    headroom_util = Util()
    headroom_util.calculate_headrooms()

    scheduler = BlockingScheduler({'apscheduler.job_defaults.max_instances': 2})
    scheduler.add_job(headroom_util.calculate_headrooms, 'interval', minutes=10)
    scheduler.start()