import time
from apscheduler.schedulers.blocking import BlockingScheduler
from blueprints.notifier.job_notifier import Process_Notifier
from utils.configs import read_config

config = read_config()

if __name__=="__main__":

    notifier = Process_Notifier()
    notifier.process_notification()
   
    scheduler = BlockingScheduler({'apscheduler.job_defaults.max_instances':  config['cron_instances']})
    scheduler.add_job(notifier.process_notification, 'interval', minutes= config['cron_time'])
    scheduler.start()
