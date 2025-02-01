import uvicorn
import threading
import ctypes

from lib._models import TokenTask, CaptchaTask
from lib._ai import get_solutions
from lib._aws import AwsTokenProcessor, InvalidCaptchaError, InvalidProxyError

from fastapi import FastAPI

lock = threading.Lock()

token_solves = 0
captcha_solves = 0

app = FastAPI()

@app.post('/solveCaptcha')
def solve_captcha(task: CaptchaTask):
    global captcha_solves

    images = task.images
    target = task.target

    try:
        solutions = get_solutions(images, target)
    except Exception as ex:
        return {"error":str(ex)}
    
    with lock:
        captcha_solves += 1
        ctypes.windll.kernel32.SetConsoleTitleW(f"Token solves: {token_solves} | Captcha solves: {captcha_solves}")
    
    return {"solutions":solutions}

@app.post('/getToken')
def getToken(task: TokenTask):
    global token_solves

    try:
        aws = AwsTokenProcessor(task)
        token = aws.get_token()
    except InvalidCaptchaError:
        return {"status":"failed to solve captcha"}
    except InvalidProxyError:
        return {"status":"invalid proxy"}
    except Exception as ex:
        return {"exception":str(ex)}

    with lock:
        token_solves += 1
        ctypes.windll.kernel32.SetConsoleTitleW(f"Token solves: {token_solves} | Captcha solves: {captcha_solves}")

    return {"token":token, "status":"success"}

if __name__ == '__main__':
    ctypes.windll.kernel32.SetConsoleTitleW(f"Token solves: {token_solves} | Captcha solves: {captcha_solves}")
    uvicorn.run(app, host="0.0.0.0", port=5000, workers=1, reload=False)
