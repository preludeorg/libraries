import asyncio
import os
import re
import stat
import subprocess
import tempfile
from urllib import request

DOS = f'{os.uname().sysname}-{os.uname().machine}'.lower()
UUID = re.compile('[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}')


class Probe:

    def __init__(self):
        self.alive = True

    @staticmethod
    def hq(dat):
        api = os.environ.get('PRELUDE_HQ', 'https://detect.prelude.org')
        r = request.Request(f'{api}?link={dat}', headers=dict(token=os.environ['PRELUDE_TOKEN']))
        with request.urlopen(r) as rs:
            if api not in rs.url:
                match = UUID.search(rs.url)
                yield match.group(0), rs.read()

    async def run(self, pack):
        def _measure():
            fp = tempfile.NamedTemporaryFile(dir=os.getcwd())
            fp.write(pack[1])
            os.chmod(fp.name, os.stat(fp.name).st_mode | stat.S_IEXEC)
            test = subprocess.run([fp.name, 'test'])
            clean = subprocess.run([fp.name, 'test'])
            fp.close()
            return f'{DOS}:{pack[0]}:{max(test.returncode, clean.returncode)}'
        if pack:
            asyncio.create_task(self.run(next(self.hq(_measure()), None)))

    async def loop(self):
        while self.alive:
            try:
                asyncio.create_task(self.run(next(self.hq(DOS), None)))
            except Exception as e:
                print('[-] %s' % e)
            await asyncio.sleep(43200)
