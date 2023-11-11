import asyncio,aiohttp,random,sys,ssl,datetime,time
from faker import Faker

faker = Faker('zh-cn')

ssl._create_default_https_context = ssl._create_unverified_context
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class worker:
    def __init__(self,mode=1):
        self.mode = mode

    def log_res(self,res):
        ts = datetime.datetime.now().isoformat(' ')
        sys.stdout.write(f'{ts} {res}\n')
        if '已达到上限' in res:return
        if res:
            self.alive = time.time()

    async def post(self,url,data):
        session = self.session
        headers = {
            'User-Agent': faker.user_agent(),
        }
        async with session.post(url, headers=headers, json=data, ssl=ssl_context) as response:
            res = await response.text()
        self.log_res(res)

    async def get(self,url):
        session = self.session
        headers = {
            'User-Agent': faker.user_agent(),
        }
        async with session.get(url, headers=headers, ssl=ssl_context) as response:
            res = await response.text()
        self.log_res(res)

    async def worker1(self,suf):
        name = faker.phone_number()
        url = f'https://guanfangtoupiaol.{suf}/mobile/login'
        data = {
            'id':random.randrange(10),
            'username':name,
            'area':faker.province() + faker.city(),
        }
        await self.post(url,data)

        url = f'https://guanfangtoupiaol.{suf}/mobile/submitcode'
        data = {
            'name':name,
            'code':''.join(map(str,(random.randrange(10) for _ in range(6)))),
        }
        await self.post(url,data)

    async def worker2(self,suf):
        name = str(random.randrange(1000000000))
        url = f'https://guanfangtoupiaol.{suf}/qq/login'
        data = {
            'id':random.randrange(10),
            'username':name,
            'password':faker.password(),
            'area':faker.province() + faker.city(),
        }
        await self.post(url,data)

    async def worker3(self,suf):
        url = 'https://apis.map.qq.com/ws/location/v1/ip?key=PTMBZ-GCQLW-SC2RG-R2FNI-HWPNQ-4PBQM'
        await self.get(url)
    
    async def worker(self):
        suf = None
        while True:
            if self.mode == 1:
                suf = random.choice(['top','cloud','monster','site','cyou','buzz'])
                func = random.choice([self.worker1,self.worker2])
            elif self.mode == 2:
                func = self.worker3
            try:
                await func(suf)
            except Exception as e:
                print(suf,repr(e))

    async def run(self,tlimit=120):
        tasks = []
        self.alive = time.time()
        if self.mode == 2:
            n_max = 10
        else:
            n_max = 100000000
        async with aiohttp.ClientSession() as session:
            self.session = session
            for _ in range(tlimit):
                for _ in range(10):
                    if len(tasks) >= n_max:break
                    tasks.append(asyncio.Task(self.worker()))
                await asyncio.sleep(1)
                if time.time() - self.alive > 60:break
            del tasks
            exit()

async def main_gh():
    w = worker()
    await w.run(3600)

async def main_gh2():
    w = worker(mode=2)
    await w.run(3600)

async def main_my():
    w = worker(mode=2)
    await w.run(86400)

if __name__ == '__main__':
    asyncio.run(main_gh())
