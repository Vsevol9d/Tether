"""from bleak import BleakScanner, BleakClient
import asyncio
import socket

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
async def dev():
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"{device.name} - {device.address}")

async def main():
    device_name = "LAPTOP-8F7UIIKQ"
    IP_CHAR_UUID = "b963e6f0-2d8c-4926-9db4-ebb916172f22"
    device = await BleakScanner.find_device_by_name(device_name)

    if not device:
        print("No devices found")
        return

    async with BleakClient(device) as client:
        print("Connected")
        ip_bytes = local_ip.encode("utf-8")
        await client.write_gatt_char(IP_CHAR_UUID, ip_bytes)

        try:
            response = await client.read_gatt_char(IP_CHAR_UUID)
            print(response)
        except:
            print("Connection error")


asyncio.run(dev())
asyncio.run(main())"""