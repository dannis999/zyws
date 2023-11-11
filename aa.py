import asyncio,aiohttp,random,sys,ssl,datetime,time,re,json
from faker import Faker
import urllib.parse as parse

faker = Faker('zh-cn')

ssl._create_default_https_context = ssl._create_unverified_context
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class worker:
    def __init__(self,mode=1):
        self.mode = mode

    def log_res(self,res,log_limit=50):
        ts = datetime.datetime.now().isoformat(' ')
        res = re.sub(r'\s+',' ',res)
        try:
            res = str(json.loads(res))
        except Exception:
            pass
        no = '已达到上限' in res
        if len(res) > log_limit:
            res = res[:log_limit]
        sys.stdout.write(f'{ts} {res}\n')
        if no:return
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
            'id':random.randint(1,8),
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
            'id':random.randint(1,8),
            'username':name,
            'password':faker.password(),
            'area':faker.province() + faker.city(),
        }
        await self.post(url,data)

    async def worker3(self,suf):
        entry = 'https://apis.map.qq.com/'
        key = 'PTMBZ-GCQLW-SC2RG-R2FNI-HWPNQ-4PBQM'
        city = parse.quote(faker.city())
        kw = parse.quote(faker.word())
        x = random.uniform(0,90)
        y = random.uniform(0,180)
        x2 = random.uniform(0,90)
        y2 = random.uniform(0,180)
        t = random.randrange(10)
        if t == 0: # https://apis.map.qq.com/ws/location/v1/ip?key=PTMBZ-GCQLW-SC2RG-R2FNI-HWPNQ-4PBQM
            url = f'{entry}ws/location/v1/ip?key={key}'
        elif t == 1:
            url = f'{entry}ws/geocoder/v1/?address={city}&key={key}'
        elif t == 2:
            url = f'{entry}ws/place/v1/search?boundary=nearby({x},{y},1000)&keyword={kw}&page_size=10&page_index=1&key={key}'
        elif t == 3:
            url = f'{entry}ws/place/v1/suggestion/?region={city}&keyword={kw}&key={key}'
        elif t == 4:
            url = f'{entry}ws/geocoder/v1/?location={x},{y}&key={key}&get_poi=1'
        elif t == 5:
            url = f'{entry}ws/direction/v1/bicycling/?from={x},{y}&to={x2},{y2}&key={key}'
        elif t == 6:
            url = f'{entry}ws/direction/v1/ebicycling/?from={x},{y}&to={x2},{y2}&key={key}'
        elif t == 7:
            url = f'{entry}ws/direction/v1/transit/?from={x},{y}&to={x2},{y2}&key={key}'
        elif t == 8:
            url = f'{entry}ws/direction/v1/driving/?from={x},{y}&to={x2},{y2}&key={key}'
        elif t == 9:
            url = f'{entry}ws/direction/v1/walking/?from={x},{y}&to={x2},{y2}&key={key}'
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
            n_max = 100
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
