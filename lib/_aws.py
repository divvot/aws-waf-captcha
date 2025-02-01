import base64
import random

from ._ai import get_solutions
from ._models import TokenTask, Proxy

from curl_cffi.requests import Session

class InvalidCaptchaError(Exception):
    pass

class InvalidProxyError(Exception):
    pass

class AwsTokenProcessor:
    def __init__(self, task: TokenTask) -> None:
        proxy_auth = None
        proxy = None

        if task.proxy and isinstance(task.proxy, Proxy):
            if task.proxy.username and task.proxy.password:
                proxy_auth = (task.proxy.username,  task.proxy.password)

            proxy = f'http://{task.proxy.host}:{task.proxy.port}'
        
        if task.proxy and isinstance(task.proxy, str):
            parts = task.proxy.split(':')
            if len(parts) != 2 and len(parts) != 4:
                raise InvalidProxyError()
            
            proxy = f'http://{parts[0]}:{parts[1]}'

            if len(parts) == 4:
                proxy_auth = (parts[2], parts[3])

        self.token_url = f"{task.token_url}/voucher"
        self.captcha_url = f"{task.captcha_url}/verify"
        self.problem_url = f"{task.captcha_url}/problem?kind=visual&domain={task.site_host}&locale=en-gb"
        self.session = Session(proxy=proxy, proxy_auth=proxy_auth, verify=False)

        self.goku_props = eval(base64.b64decode(task.goku_props).decode())

        self.__get_challenge()

    def __get_challenge(self):
        challenge = self.session.get(self.problem_url, impersonate='chrome124').json()

        self.payload = challenge['state']['payload']
        self.iv = challenge['state']['iv']
        self.hmac_tag = challenge['hmac_tag']
        self.key = challenge['key']
        self.images = eval(challenge['assets']['images'])
        self.target = eval(challenge['assets']['target'])[0]
    
    def get_token(self):
        solutions = get_solutions(self.images, self.target)
        data = {
            "state":{
                "iv":self.iv,
                "payload":self.payload
            },
            "key":self.key,
            "hmac_tag":self.hmac_tag,
            "client_solution": solutions,
            "metrics":{"solve_time_millis":random.randint(5000, 9000)},
            "goku_props":self.goku_props,
            "locale":"en-gb"
        }

        response = self.session.post(self.captcha_url, json=data, impersonate='chrome124').json()
        if not response['success']:
                raise InvalidCaptchaError()

        data = {
            "captcha_voucher": response['captcha_voucher'],
            "existing_token": None
        }

        response = self.session.post(self.token_url, json=data, impersonate='chrome124').json()

        return response['token']
