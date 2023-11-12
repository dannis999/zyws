from g2 import *

def url_iter():
    sufs = ['top','cloud','monster','site','cyou','buzz']
    for suf in sufs:
        host = f'https://guanfangtoupiaol.{suf}/'
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
        async with self.session.post(url,headers=headers,json=data) as response:
            r = await response.text()
        return r

    @property
    def wait(self):
        return random.uniform(10,20)

    async def save(self,url):
        '返回name,msg'
        print(url)
        try:
            r = await self.save_req(url)
        except Exception as e:
            print(repr(e))
        else:
            if r.status_code != 200:
                print(r.text)

    async def run(self):
        urls = list(url_iter())
        random.shuffle(urls)
        async with aiohttp.ClientSession() as session:
            self.session = session
            for url in urls:
                await asyncio.gather(
                    self.save(url),
                    asyncio.sleep(self.wait),
                )

async def main():
    w = wbSaver()
    await w.run()

if __name__ == '__main__':
    asyncio.run(main())