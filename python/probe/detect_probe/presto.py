import asyncio
import os
import resource
from functools import wraps
from urllib import request

DOS = f'{os.uname().sysname}-python.code'.lower()
WORKING_DIR = None


def clock(func):
    @wraps(func)
    def wrapper(*args, **params):
        pre = resource.getrusage(resource.RUSAGE_SELF)
        pre_cycles = getattr(pre, 'ru_utime') + getattr(pre, 'ru_stime')
        i, status = func(*args, **params)
        post = resource.getrusage(resource.RUSAGE_SELF)
        post_cycles = getattr(post, 'ru_utime') + getattr(post, 'ru_stime')
        return DOS, i, status, '%.3f' % float(post_cycles - pre_cycles)
    return wrapper


class Probe:

    def __init__(self):
        self.alive = True

    @staticmethod
    def hq(dat):
        api = os.environ.get('PRELUDE_HQ', 'https://detect.prelude.org')
        r = request.Request(api, str.encode(dat), dict(token=os.environ['PRELUDE_TOKEN']))
        with request.urlopen(r) as rs:
            yield rs.read().decode('utf8')

    @staticmethod
    def code(dat):
        requested_mod = {}
        exec(dat, requested_mod)
        return requested_mod

    async def run(self, test):
        @clock
        def _run():
            i, blob = test[:36], bytes.fromhex(test[36:]).decode('utf-8')
            code = self.code(blob)
            status = code.get('attack')()
            code.get('cleanup')()
            return i, status
        if test:
            dat = '%s:%s:%s:%s' % _run()
            asyncio.create_task(self.run(next(self.hq(dat), None)))

    async def loop(self):
        while self.alive:
            try:
                asyncio.create_task(self.run(next(self.hq(DOS), None)))
            except Exception as e:
                print('[-] %s' % e)
            await asyncio.sleep(43200)
