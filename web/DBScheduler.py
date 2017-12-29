# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


from django_celery_beat.schedulers import DatabaseScheduler
from celery.five import values
import heapq
import time

from collections import namedtuple
event_t = namedtuple('event_t', ('time', 'priority', 'entry'))



class Scheduler(DatabaseScheduler):

    @property
    def my_schedule(self):
        self.sync()
        ret = self.all_as_schedule()
        #print("Current schedule:\n%s", "\n".join(
        #    repr(entry) for entry in values(ret)
        #))
        return ret
        

    def tick(self, event_t=event_t, min=min,
             heappop=heapq.heappop, heappush=heapq.heappush,
             heapify=heapq.heapify, mktime=time.mktime):
        """Run a tick - one iteration of the scheduler.

        Executes one due task per call.

        Returns:
            float: preferred delay in seconds for next call.
        """
        def _when(entry, next_time_to_run):
            return (mktime(entry.schedule.now().timetuple()) +
                    (adjust(next_time_to_run) or 0))

        adjust = self.adjust
        max_interval = self.max_interval
        H = self._heap
        if H is None:
            H = self._heap = [event_t(_when(e, e.is_due()[1]) or 0, 5, e)
                              for e in values(self.schedule)]
            heapify(H)

        elif self.schedule_changed():       # if database changed, update the heap. some task would be droped
            print "[INFO]: database changed, update H now!!"
            H = self._heap = [event_t(_when(e, e.is_due()[1]) or 0, 5, e)
                              for e in values(self.my_schedule)]
            print("length of H is [%d]" % len(H) )
            heapify(H)

        if not H:
            return max_interval

        event = H[0]
        entry = event[2]
        is_due, next_time_to_run = self.is_due(entry)
        if is_due:
            verify = heappop(H)
            if verify is event:
                next_entry = self.reserve(entry)
                self.apply_entry(entry, producer=self.producer)
                heappush(H, event_t(_when(next_entry, next_time_to_run),
                                    event[1], next_entry))
                return 0
            else:
                heappush(H, verify)
                return min(verify[0], max_interval)
        return min(adjust(next_time_to_run) or max_interval, max_interval)