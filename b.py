import requests,random,sys
from faker import Faker
import json,datetime
import threading

faker = Faker('zh-cn')

def worker():
    while True:
        name = str(random.randrange(1000000000))
        url = 'https://guanfangtoupiaol.monster/qq/login'
        data = {
            'id':random.randrange(10),
            'username':name,
            'password':faker.password(),
            'area':faker.province() + faker.city(),
            }
        response = requests.post(url, json=data)
        ts = datetime.datetime.now().isoformat(' ')
        sys.stdout.write(f'{ts} {response.json()}\n')

def main():
    ts = []
    for _ in range(100):
        t = threading.Thread(target=worker)
        t.start()
        ts.append(t)
    for t in ts:
        t.join()

if __name__ == '__main__':
    main()
