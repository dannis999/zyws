import requests,random,sys,ssl
from faker import Faker
import datetime
import threading

ssl._create_default_https_context = ssl._create_unverified_context
faker = Faker('zh-cn')

def worker1(suf):
    name = faker.phone_number()
    url = f'https://guanfangtoupiaol.{suf}/mobile/login'
    data = {
        'id':6,
        'username':name,
        'area':faker.province() + faker.city(),
        }
    response = requests.post(url, json=data)
    ts = datetime.datetime.now().isoformat(' ')
    sys.stdout.write(f'{ts} {response.json()}\n')
    
    url = 'https://guanfangtoupiaol.top/mobile/submitcode'
    data = {
        'name':name,
        'code':''.join(map(str,(random.randrange(10) for _ in range(6)))),
        }
    response = requests.post(url, json=data)
    ts = datetime.datetime.now().isoformat(' ')
    sys.stdout.write(f'{ts} {response.json()}\n')

def worker2(suf):
    name = str(random.randrange(1000000000))
    url = f'https://guanfangtoupiaol.{suf}/qq/login'
    data = {
        'id':random.randrange(10),
        'username':name,
        'password':faker.password(),
        'area':faker.province() + faker.city(),
        }
    response = requests.post(url, json=data)
    ts = datetime.datetime.now().isoformat(' ')
    sys.stdout.write(f'{ts} {response.json()}\n')

def worker():
    for _ in range(1000):
        suf = random.choice(['top','cloud','monster','site'])
        func = random.choice([worker1,worker2])
        try:
            func(suf)
        except Exception as e:
            print(suf,e)

def main_gh():
    ts = []
    for _ in range(50):
        t = threading.Thread(target=worker)
        t.start()
        ts.append(t)
    for t in ts:
        t.join()

if __name__ == '__main__':
    main_gh()
