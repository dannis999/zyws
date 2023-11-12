from g2 import *

hosts = []
def url_iter():
    sufs = ['top','cloud','monster','site','cyou','buzz']
    for suf in sufs:
        host = f'https://guanfangtoupiaol.{suf}/'
        hosts.append(host)
        for i in range(1,9):
            yield f'{host}mobile/login?id={i}'
            yield f'{host}qq/login?id={i}'
        for _ in range(10):
            name = get_phone()
            yield f"{host}mobile/code?name={name}"
            yield f'{host}/mobile/codeverify?name={name}'
        for _ in range(10):
            name = get_qq()
            yield f"{host}qq/verify?name={name}"
        yield f'{host}/mobile/submitcode'
        yield f'{host}/mobile/codeverify'
        yield f'{host}/qq/verify'

class wbSaver:
    url='http://web.archive.org/save'

    @classmethod
    def get_headers(cls):
        return {
            'Referer':cls.url,
            'User-Agent':faker.chrome(),
            }

    async def save_req(self,url):
        self.cur_url = url
        data = {
            'url':url,
        }
        headers = self.get_headers()
        url = self.url + '/' + url
        async with self.session.post(url,headers=headers,data=data) as response:
            r = await response.text()
            if response.status == 200:
                print('ok')
            else:
                print(r)

    @property
    def wait(self):
        return random.uniform(5,10)

    async def save(self,url):
        '返回name,msg'
        print(url)
        try:
            await self.save_req(url)
        except Exception as e:
            print(repr(e))
    
    async def task_exit(self,t):
        await asyncio.sleep(t)
        exit()

    async def run(self,t):
        t = asyncio.Task(self.task_exit(t))
        urls = list(url_iter())
        random.shuffle(urls)
        random.shuffle(hosts)
        async with aiohttp.ClientSession() as session:
            self.session = session
            for url in hosts + urls:
                await asyncio.gather(
                    self.save(url),
                    asyncio.sleep(self.wait),
                )

async def main():
    w = wbSaver()
    await w.run(60)

if __name__ == '__main__':
    asyncio.run(main())
