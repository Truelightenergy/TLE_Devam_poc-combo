import time
from apscheduler.schedulers.blocking import BlockingScheduler
from blueprints.notifier.util import Util
from utils.configs import read_config

config = read_config()


if __name__=="__main__":

    util = Util()
    util.setup_notifications()
   
    scheduler = BlockingScheduler({'apscheduler.job_defaults.max_instances':  config['cron_instances']})
    scheduler.add_job(util.setup_notifications, 'interval', minutes= config['cron_time'])
    scheduler.start()
