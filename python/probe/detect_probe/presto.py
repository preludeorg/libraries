import asyncio
import platform
import re
import stat
import subprocess
import tempfile
import os.path
from urllib import request
from urllib.parse import urlparse

DOS = f'{platform.system()}-{platform.machine()}'.lower()
UUID = re.compile('[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}')


class Probe:

    def __init__(self):
        self.alive = True

    @staticmethod
    def service(dat=''):
        api = os.environ.get('PRELUDE_API', 'https://detect.prelude.org')
        headers = dict(token=os.environ.get('PRELUDE_TOKEN'), dos=DOS, dat=dat)
        with request.urlopen(request.Request(api, headers=headers)) as rs:
            authority = urlparse(rs.url).netloc
            if os.environ.get('PRELUDE_CA', authority) == authority:
                test = UUID.search(rs.url)
                if test:
                    yield test.group(0), rs.read()

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
            asyncio.create_task(self.run(next(self.service(_measure()), None)))

    async def loop(self):
        while self.alive:
            try:
                asyncio.create_task(self.run(next(self.service(), None)))
            except Exception as e:
                print('[-] %s' % e)
            await asyncio.sleep(43200)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(Probe().loop())
