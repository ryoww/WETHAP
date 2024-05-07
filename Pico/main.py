import asyncio
import gc
import json

from machine import ADC, I2C, Pin, reset

import env
from sender import Config, Sender


async def init():
    async with master.lock:
        master.display.add_text("WETHAP", new=True).line()
        if master.display.status:
            master.display.display.rect(5, 20, 118, 35, 1)
        master.display.add_text("Hello World!", 3).show()
        await asyncio.sleep(1)
        master.led.off()
        master.display.add_text("booting...", new=True).line().show(False)
        master.init_sensor()
        master.display.add_text("wifi connecting").show(False)
        await master.wifi_connect()
        await master.update_time()
        print("initialize complete")
        master.led.on()


async def send_info_loop():
    while await master.ws.open():
        data = await master.ws.recv()
        if data is None:
            continue
        data = json.loads(data)
        if data.get("message") == "change labID":
            if data.get("new labID"):
                master.labID = data.get("new labID")
                print(f"change labID to {master.labID}")
        elif data.get("message") == "request info":
            info = {"labID": master.labID}
            info.update(master.get_info())
            if data.get("numGen") is not None:
                info["numGen"] = data.get("numGen")
            else:
                info["time"] = master.now_time()
            message = {"status": "send info", "info": info}
            await master.ws.send(json.dumps(message))
            print(f"Sent from Client: {message}")

            async with master.lock:
                now = master.now()
                if info.get("numGen") is None:
                    master.display.add_text("manual request", new=True)
                    master.display.add_text("info posted").line()
                else:
                    master.display.add_text("info posted", new=True).line()
                master.display.add_text(f"date:{now[0]}-{now[1]:02d}-{now[2]:02d}")
                if info.get("numGen") is not None:
                    master.display.add_text(f'numGen:{info["numGen"]}')
                master.display.add_text(f'Temp:{info["temperature"]}C')
                master.display.add_text(f'Hmd.:{info["humidity"]}%')
                master.display.add_text(f'Pres.:{info["pressure"]}hPa').show()
                await asyncio.sleep_ms(1000)


async def keep_connection_loop(interval=60):
    while await master.ws.open():
        await master.ws.send(json.dumps({"message": "keep-alive"}))
        await asyncio.sleep(interval)


async def wifi_connection_loop():
    while True:
        if not master.wifi.isconnected():
            with master.lock():
                master.led.off()
                await master.wifi_connect()
                if not master.wifi.isconnected():
                    await asyncio.sleep_ms(config.wifi_delay)
                else:
                    master.led.on()
        await asyncio.sleep(1)


async def update_time_loop():
    while True:
        now = master.now()
        wait_time = (60 - now[5]) * 60 + (60 - now[6])
        await asyncio.sleep(wait_time)
        while not master.wifi.isconnected():
            await asyncio.sleep_ms(config.wifi_delay)
        async with master.lock:
            await master.update_time()


async def display_info_loop():
    while True:
        async with master.lock:
            # master.display.clear()
            envs = master.get_info()
            now = master.now()
            master.display.multi_text(
                f"{now[0]}-{now[1]:02d}-{now[2]:02d}",
                f"{now[4]:02d}:{now[5]:02d}:{now[6]:02d}",
                f'Temp:{envs["temperature"]:.3f}C',
                f'Hmd.:{envs["humidity"]:.3f}%',
                f'Pres.:{envs["pressure"]:.2f}hPa',
                lines=[2],
            )
        await asyncio.sleep_ms(900)


async def main_loop():
    while True:
        gc.collect()
        try:
            async with master.lock:
                master.led.off()
                master.display.add_text("server connecting...", row=3, new=True)
                print("Handshaking...")
                if not await master.ws.handshake(config.api_server):
                    raise Exception("Handshake error.")
                print("Handshake complete.")

                await master.ws.send(
                    json.dumps({"uuid": master.machine_id, "labID": master.labID})
                )
                print(
                    f'send: {json.dumps({"uuid": master.machine_id, "labID": master.labID})}'
                )
                init_info = await master.ws.recv()
                master.labID = json.loads(init_info)["labID"]
                print(f"my labID: {master.labID}, received info: {init_info}")
                master.display.add_text("server connected")
                master.led.on()
            await asyncio.gather(
                keep_connection_loop(master.config.keep_alive_interval),
                send_info_loop(),
            )

        except Exception as error:
            print(f"Exception: {error}")
            await master.ws.close()
            await asyncio.sleep(1)


async def main():
    try:
        tasks = [main_loop(), wifi_connection_loop()]
        await init()
        if master.display.status:
            tasks += [update_time_loop(), display_info_loop()]
        await asyncio.gather(*tasks)
    except Exception:
        await master.ws.close()
        reset()


led = Pin("LED", Pin.OUT, value=True)
i2c = I2C(0, sda=Pin(16, pull=Pin.PULL_UP), scl=Pin(17, pull=Pin.PULL_UP))
temp_adj = ADC(0)
humid_adj = ADC(1)
config = Config()
config.load_env(env)
master = Sender(config=config, led=led, i2c=i2c, temp_adj=temp_adj, humid_adj=humid_adj)
asyncio.run(main())
