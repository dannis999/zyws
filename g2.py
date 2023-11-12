import asyncio,aiohttp,random,sys,ssl,datetime,time,re,json,collections
from faker import Faker
import urllib.parse as parse

faker = Faker('zh-cn')

ssl._create_default_https_context = ssl._create_unverified_context
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def get_ts():
    return datetime.datetime.now().isoformat(' ')

def get_ua():
    return faker.user_agent()

def get_id():
    return str(random.randint(1,8))

def get_phone():
    return str(faker.phone_number())

def get_area():
    return faker.province() + faker.city()

def get_mobile_code():
    return ''.join(map(str,(random.randrange(10) for _ in range(6))))

def rand_bool():
    return random.random() < 0.5

def get_password():
    return faker.password(
        length = random.randint(8,16),
        special_chars = rand_bool(),
        digits = rand_bool(),
        upper_case = rand_bool(),
        lower_case = rand_bool(),
    )

def get_headers():
    return {
        'User-Agent': faker.user_agent(),
    }

def auto_json(res):
    try:
        return json.loads(res)
    except Exception:
        return res

class worker:
    def __init__(self):
        self.logd = {}
        self.tasks = []
    
    def set_alive(self):
        self.alive = time.time()
    
    def is_alive(self):
        return time.time() - self.alive < 60
    
    def add_task(self,co):
        self.tasks.append(asyncio.Task(co))

    async def post(self,*a,**k):
        session = self.session
        async with session.post(*a,**k,ssl=ssl_context) as response:
            res = await response.text()
        return auto_json(res)

    async def get(self,*a,**k):
        session = self.session
        async with session.get(*a,**k,ssl=ssl_context) as response:
            res = await response.text()
        return auto_json(res)
    
    async def query_qq_api(self,t):
        entry = 'https://apis.map.qq.com/'
        key = 'PTMBZ-GCQLW-SC2RG-R2FNI-HWPNQ-4PBQM'
        city = parse.quote(faker.city())
        kw = parse.quote(faker.word())
        x = random.uniform(0,90)
        y = random.uniform(0,180)
        x2 = random.uniform(0,90)
        y2 = random.uniform(0,180)
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
        headers = get_headers()
        r = await self.get(url,headers=headers)
        try:
            m = r['message']
        except Exception:
            m = str(r)
        if '每日调用量已达到上限' in m:
            return 'limit_day'
        if '已达到上限' in m:
            return 'limit'
        return 'ok'
    
    async def task_qq_api(self,t):
        sd = self.qq_states[t]
        while True:
            try:
                m = await self.query_qq_api(t)
            except Exception as e:
                print('qq_api',t,repr(e))
                m = 'err'
            sd[m] += 1
            if sd['limit_day'] > 10:return
            if m == 'ok':
                self.set_alive()
    
    async def start_qq_api(self,tn=10):
        self.qq_states = [collections.defaultdict(int) for _ in range(tn)]
        for _ in range(10):
            for t in range(tn):
                self.add_task(self.task_qq_api(t))
                await asyncio.sleep(0.1)
    
    async def query_toupiao(self,host):
        headers = get_headers()
        html = await self.get(host,headers=headers)
        t = re.escape(host)
        t2 = re.escape('onclick="window.alert(&#39;为了防止刷票，请填使用手机验证&#39;)"')
        pt = rf'a href\=\"({t}[a-z/]+/login\?id=\d+)\"\s+{t2}'
        nexts = re.findall(pt,html)
        if not nexts:
            print(host)
            print(html)
            return 'err'
        url = random.choice(nexts)
        html = await self.get(url,headers=headers)
        pt = rf"url\:\s*\'({t}[a-z/]+/login)\'"
        nexts = re.findall(pt,html)
        if not nexts:
            print(host)
            print(html)
            return 'err'
        url = nexts[0]
        if 'mobile' in url:
            name = get_phone()
            data = {
                'id':get_id(),
                'username':name,
                'area':get_area(),
            }
            r = await self.post(url,json=data,headers=headers)
            if r['code'] != 200:
                print('toupiao','mobile',r)
                return 'err'
            print('toupiao','mobile',data)
            url = f"{host}mobile/code?name={name}"
            html = await self.get(url,headers=headers)
            # 错误的手机号跳转到首页
            # 未提交的手机号等待提交
            # 已提交的手机号跳转到 codeverify
            url = f'{host}/mobile/submitcode'
            data = {
                'name':name,
                'code':get_mobile_code(),
            }
            r = await self.post(url,json=data,headers=headers)
            if r['code'] != 200:
                print('toupiao','mobile',r)
                return 'err'
            print('toupiao','mobile submitcode',data)
            # 提交后跳转
            url = f'{host}/mobile/codeverify?name={name}'
            html = await self.get(url,headers=headers)
            url = f'{host}/mobile/codeverify'
            data = {
                'name':name,
            }
            r = await self.post(url,json=data,headers=headers)
            print('toupiao','mobile codeverify',r)
        elif 'qq' in url:
            name = str(random.randrange(1000000000))
            data = {
                'id':get_id(),
                'username':name,
                'password':get_password(),
                'area':get_area(),
            }
            r = await self.post(url,json=data,headers=headers)
            if r['code'] != 200:
                print('toupiao','qq',r)
                return 'err'
            print('toupiao','qq',data)
            # 提交后跳转
            url = f"{host}qq/verify?name={name}"
            html = await self.get(url,headers=headers)
            url = f'{host}/qq/verify'
            data = {
                'name':name,
            }
            r = await self.post(url,json=data,headers=headers)
            print('toupiao','qq codeverify',r)
        else:
            print('toupiao','???',url)
        return 'ok'
    
    async def task_toupiao(self,suf):
        sd = self.tp_state[suf]
        host = f'https://guanfangtoupiaol.{suf}/'
        while True:
            try:
                m = await self.query_toupiao(host)
            except Exception as e:
                print('toupiao',repr(e))
                m = 'err'
            sd[m] += 1
            if m == 'ok':
                self.set_alive()

    async def start_toupiao(self):
        sufs = ['top','cloud','monster','site','cyou','buzz']
        random.shuffle(sufs)
        self.tp_state = {suf:collections.defaultdict(int) for suf in sufs}
        for _ in range(100):
            for suf in sufs:
                self.add_task(self.task_toupiao(suf))
                await asyncio.sleep(0.1)

    def checkpoint(self):
        self.tasks = [t for t in self.tasks if not t.done()]
        n = len(self.tasks)
        dt = time.time()
        t_run = dt - self.t_begin
        t_idle = dt - self.alive
        print(f'任务数量 {n}, 运行时间 {t_run / 60} min, 空闲时间 {t_idle} s')
        for i,c in enumerate(self.qq_states):
            print('qq api',i,dict(c))
        for suf,c in self.tp_state.items():
            print('toupiao',suf,dict(c))
    
    async def run(self):
        self.set_alive()
        async with aiohttp.ClientSession() as session:
            self.session = session
            self.t_begin = time.time()
            self.add_task(self.start_toupiao())
            self.add_task(self.start_qq_api())
            while True:
                await asyncio.sleep(5)
                self.checkpoint()
                if not self.tasks:break
                if not self.is_alive():break
        exit()

async def main():
    w = worker()
    await w.run()

if __name__ == '__main__':
    asyncio.run(main())
