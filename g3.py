from g2 import *
import string

get_name = faker.name

class worker2(worker):
    ss = string.ascii_lowercase + string.ascii_uppercase + string.digits
    def __init__(self):
        super().__init__()
        self.rand_rid = random.random() < 0.5
        self.use_track = random.random() < 0.5
        self.rid = random.choice(['9IpIo8N','TPqlPXb'])
        print(self.rand_rid,self.use_track,self.rid)
    
    async def query_one(self,rid):
        headers = get_headers()
        home = 'https://nju.authserver.cn:80/?rid=' + rid
        if self.use_track:
            track = 'https://nju.authserver.cn:80/track?rid=' + rid
            headers['Referer'] = home
            await self.get(track,headers=headers)
        target = 'https://nju.authserver.cn:80/?rid=' + rid
        name = get_name()
        data = {
            'username':name,
        }
        r = await self.post(target,headers=headers,data=data)
        print(rid,self.use_track,name,r)
        self.set_alive()
    
    async def task_edu(self,dt):
        await asyncio.sleep(dt)
        while True:
            if self.rand_rid:
                rid = ''.join(random.choice(self.ss) for _ in range(7))
            else:
                rid = self.rid
            try:
                await self.query_one(rid)
            except Exception as e:
                print(rid,repr(e))
    
    async def start_edu(self,n_con=48,t_window=50,t_base=0.01):
        k_all = t_window / t_base
        k0 = k_all ** (1.0 / n_con)
        t0 = t_base
        for _ in range(n_con):
            t0 *= k0
            dt = t0 * random.uniform(0,2)
            self.add_task(self.task_edu(dt))

    async def run(self):
        self.set_alive()
        self.add_task(self.task_exit())
        async with aiohttp.ClientSession() as session:
            self.session = session
            self.t_begin = time.time()
            self.add_task(self.start_edu())
            while True:
                await asyncio.sleep(5)
                if not self.tasks:break
                if not self.is_alive():break
            print('exiting...')
        exit()

async def main2():
    w = worker2()
    await w.run()

if __name__ == '__main__':
    asyncio.run(main2())
