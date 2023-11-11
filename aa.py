import asyncio,aiohttp,random,sys,ssl,datetime
from faker import Faker

faker = Faker('zh-cn')

ssl._create_default_https_context = ssl._create_unverified_context
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class worker:
    async def post(self,url,data):
        session = self.session
        async with session.post(url, json=data, ssl=ssl_context) as response:
            res = await response.json()
        ts = datetime.datetime.now().isoformat(' ')
        sys.stdout.write(f'{ts} {res}\n')

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
    
    async def worker(self):
        while True:
            suf = random.choice(['top','cloud','monster','site','cyou','buzz'])
            func = random.choice([self.worker1,self.worker2])
            try:
                await func(suf)
            except Exception as e:
                print(suf,repr(e))

    async def run(self,tlimit=120):
        tasks = []
        async with aiohttp.ClientSession() as session:
            self.session = session
            for _ in range(tlimit):
                for _ in range(10):
                    tasks.append(asyncio.Task(self.worker()))
                await asyncio.sleep(1)
            del tasks
            exit()

async def main_gh():
    w = worker()
    await w.run(600)

async def main_my():
    w = worker()
    await w.run(86400)

if __name__ == '__main__':
    asyncio.run(main_gh())
