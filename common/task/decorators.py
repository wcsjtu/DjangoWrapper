# -*- coding: utf-8 -*-
import logging
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.utils.module_loading import import_string

try:
    _celery_task = getattr(settings, "CELERY_TASK", None)
    task = import_string(_celery_task)
except ImproperlyConfigured:
    logging.warn("settings are not configured!!")


def timer(*args, **kwargs):
    """
    Example	                                            Meaning
    crontab()	                                        Execute every minute.
    
    crontab(minute=0, hour=0)	                        Execute daily at midnight.
    
    crontab(minute=0, hour='*/3')	                    Execute every three hours: midnight, 3am, 6am, 9am, noon, 3pm, 6pm, 9pm.
    crontab(minute=0,
            hour='0,3,6,9,12,15,18,21')                 Same as previous.
    
    crontab(minute='*/15')	                            Execute every 15 minutes.
    
    crontab(day_of_week='sunday')	                    Execute every minute (!) at Sundays.
    
    crontab(minute='*',
            hour='*', day_of_week='sun')                Same as previous.
    
    crontab(minute='*/10',
            hour='3,17,22', day_of_week='thu,fri')      Execute every ten minutes, but only between 3-4 am, 5-6 pm, 
                                                        and 10-11 pm on Thursdays or Fridays.
    
    crontab(minute=0, hour='*/2,*/3')	                Execute every even hour, and every hour divisible by three. 
                                                        This means: at every hour except: 1am, 5am, 7am, 11am, 1pm, 5pm, 7pm, 11pm
    
    crontab(minute=0, hour='*/5')	                    Execute hour divisible by 5. This means that it is triggered at 3pm, 
                                                        not 5pm (since 3pm equals the 24-hour clock value of ��15��, which is divisible by 5).
    
    crontab(minute=0, hour='*/3,8-17')	                Execute every hour divisible by 3, and every hour during office hours (8am-5pm).
    
    crontab(0, 0, day_of_month='2')	                    Execute on the second day of every month.
    
    crontab(0, 0,
            day_of_month='2-30/3')                      Execute on every even numbered day.
    
    crontab(0, 0,
            day_of_month='1-7,15-21')                   Execute on the first and third weeks of the month.
    
    crontab(0, 0, day_of_month='11',
            month_of_year='5')                          Execute on the eleventh of May every year.
    
    crontab(0, 0,
            month_of_year='*/3')                        Execute on the first month of every quarter.
    
    more infos, see http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html
    """
    from celery.beat import crontab
    from celery.task import periodic_task
    all = ["month_of_year", "day_of_month", "hour", "minute", "day_of_week"]
    crontab_args = args
    crontab_kwargs = {}
    left_kwargs = {}
    for kw in kwargs:
        if kw in all: crontab_kwargs[kw] = kwargs[kw]
        else: left_kwargs[kw] = kwargs[kw]
    left_kwargs["run_every"] = (crontab(*crontab_args, **crontab_kwargs))
    return periodic_task(**left_kwargs)

__all__ = ["task", "timer"]