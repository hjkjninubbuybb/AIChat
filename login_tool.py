import requests
import time
import json
import os
from dotenv import load_dotenv

# 加载 .env 配置
load_dotenv()
API_URL = os.getenv("GEWE_API_URL", "http://localhost:2531/v2/api")
CALLBACK_URL = os.getenv("CALLBACK_URL", "http://host.docker.internal:8000/callback")
APP_ID = "wx_bot_v2" # 自定义一个设备ID

def get_token():
    """获取 Token"""
    try:
        resp = requests.post(f"{API_URL}/tools/getTokenId", json={"appId": APP_ID})
        resp_json = resp.json()
        if resp_json['ret'] == 200:
            return resp_json['data']
        print(f"❌ 获取Token失败: {resp_json}")
        return None
    except Exception as e:
        print(f"❌ 连接 GeWeChat 失败，请检查 Docker 是否启动: {e}")
        return None

def get_qr(token):
    """获取登录二维码"""
    resp = requests.post(f"{API_URL}/login/getLoginQrCode", json={"appId": APP_ID, "uuid": token})
    data = resp.json()
    if data['ret'] == 200:
        print(f"\n✅ 请使用微信扫描下面的链接（复制到浏览器打开）：\n")
        print(f"👉 {data['data']['qrData']}\n")
        return True
    return False

def check_login(token):
    """检查是否登录成功"""
    while True:
        resp = requests.post(f"{API_URL}/login/checkLogin", json={"appId": APP_ID, "uuid": token})
        data = resp.json()
        if data['ret'] == 200:
            # data['data']['status']: 0=未扫码, 1=已扫码, 2=已登录
            status = data['data']['status']
            if status == 2:
                print(f"🎉 登录成功！微信号: {data['data']['loginInfo']['wxid']}")
                return True
            elif status == 1:
                print("👀 已扫码，请在手机上确认登录...")
        time.sleep(2)

def set_callback(token):
    """设置回调地址"""
    print(f"⚙️ 正在设置回调地址为: {CALLBACK_URL}")
    resp = requests.post(f"{API_URL}/tools/setCallback", json={
        "token": token,
        "callbackUrl": CALLBACK_URL
    })
    if resp.json()['ret'] == 200:
        print("✅ 回调地址设置成功！全真测试环境已就绪。")
    else:
        print(f"❌ 设置失败: {resp.json()}")

if __name__ == "__main__":
    print("🚀 开始初始化 GeWeChat...")
    token = get_token()
    if token:
        get_qr(token)
        if check_login(token):
            set_callback(token)
            print("\n============ 下一步 ============")
            print("现在，请去 PyCharm 运行 app/main.py")
            print("然后用另外一个手机给这个微信号发消息测试！")