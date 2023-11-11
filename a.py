import requests,random,sys
from faker import Faker
import json,datetime
import threading

faker = Faker('zh-cn')

def worker():
    while True:
        name = faker.phone_number()
        url = 'https://guanfangtoupiaol.monster/mobile/login'
        data = {
            'id':6,
            'username':name,
            'area':faker.province() + faker.city(),
            }
        response = requests.post(url, json=data)
        ts = datetime.datetime.now().isoformat(' ')
        sys.stdout.write(f'{ts} {response.json()}\n')
        
        url = 'https://guanfangtoupiaol.monster/mobile/submitcode'
        data = {
            'name':name,
            'code':''.join(map(str,(random.randrange(10) for _ in range(6)))),
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
