import asyncio
import aiohttp
import socket
from aiohttp import ClientSession
import re

pattern = re.compile(r"%SYS-5-CONFIG_I")

# Webhook URL to which the syslog events will be forwarded
WEBHOOK_URL = "https://yourwebhook.url/endpoint"

# The IP address and port on which the script will listen for syslog messages
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 514  # Consider using a non-privileged port (above 1024) if not running as root


# async def send_event(event_data: str, sender_ip: str, session: ClientSession):
#     """Send a single syslog event and the sender's IP address to the webhook."""
#     payload = {
#         "log": event_data,
#         "ip_address": sender_ip
#     }
#     try:
#         async with session.post(WEBHOOK_URL, json=payload) as response:
#             print(f"Log sent from {sender_ip}. Response status: {response.status}")
#     except Exception as e:
#         print(f"Error sending log from {sender_ip}: {e}")


async def listen_for_syslog_messages(loop):
    """Listen for incoming syslog messages and forward them along with the sender's IP address."""
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, LISTEN_PORT))
    sock.setblocking(False)

    async with aiohttp.ClientSession() as session:
        while True:
            data, addr = await loop.sock_recvfrom(sock, 4096)
            syslog_message = data.decode('utf-8').strip()
            if pattern.search(syslog_message):
                sender_ip = addr[0]  # Extract the sender's IP address
                print(syslog_message, f'| Client IP: {sender_ip}')
                # asyncio.create_task(send_event(syslog_message, sender_ip, session))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        print(f"Listening for syslog messages on {LISTEN_IP}:{LISTEN_PORT}")
        loop.run_until_complete(listen_for_syslog_messages(loop))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
