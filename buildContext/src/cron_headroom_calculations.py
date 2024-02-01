import time
from apscheduler.schedulers.blocking import BlockingScheduler
from blueprints.headrooms.headroom_util import Util
from utils.configs import read_config

config = read_config()
if __name__=="__main__":
    headroom_util = Util()
    headroom_util.calculate_headrooms()

    scheduler = BlockingScheduler({'apscheduler.job_defaults.max_instances': config['cron_instances']})
    scheduler.add_job(headroom_util.calculate_headrooms, 'interval', minutes=config['cron_time'])
    scheduler.start()