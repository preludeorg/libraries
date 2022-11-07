import asyncio
import platform
import re
import stat
import subprocess
import tempfile
import os.path
from urllib import request

DOS = f'{platform.system()}-{platform.machine()}'.lower()
UUID = re.compile('[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}')


class Probe:

    def __init__(self):
        self.alive = True

    @staticmethod
    def hq(dat=''):
        headers = dict(token=os.environ['PRELUDE_TOKEN'], dos=DOS, dat=dat)
        r = request.Request('http://localhost:8080', headers=headers)
        with request.urlopen(r) as rs:
            match = UUID.search(rs.url)
            if match:
                yield match.group(0), rs.read()

    async def run(self, pack):
        def _measure():
            name = ''
            try:
                fd, name = tempfile.mkstemp(dir=os.getcwd())
                os.write(fd, pack[1])
                os.close(fd)
                os.chmod(name, os.stat(name).st_mode | stat.S_IEXEC)
                test = subprocess.run([name], timeout=2)
                clean = subprocess.run([name, 'clean'], timeout=2)
                return f'{pack[0]}:{max(test.returncode, clean.returncode)}'
            except subprocess.TimeoutExpired:
                return f'{pack[0]}:102'
            except Exception:
                return f'{pack[0]}:1'
            finally:
                if os.path.exists(name):
                    os.remove(name)
        if pack:
            asyncio.create_task(self.run(next(self.hq(_measure()), None)))

    async def loop(self):
        while self.alive:
            try:
                asyncio.create_task(self.run(next(self.hq(), None)))
            except Exception as e:
                print('[-] %s' % e)
            await asyncio.sleep(43200)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(Probe().loop())
