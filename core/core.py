import logging
import os
import re
import socket

import arc
import hikari
import httpx
import miru

bot = hikari.GatewayBot(os.environ["TOKEN"])
arc_client = arc.GatewayClient(bot)
miru_client: miru.Client = miru.Client.from_arc(arc_client)
httpx_client = httpx.AsyncClient()
logger: logging.Logger = logging.getLogger("PingCat")

ipv4_regex = re.compile(
    r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$"
)
ipv6_regex = re.compile(
    r"(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"
)
domain_regex = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.(?!-)[A-Za-z0-9-]{1,63}(?<!-)$"
)

def detect_input_type(input_str: str) -> tuple[str, str]:
    if ipv4_regex.match(input_str):
        return "ipv4", input_str
    elif ipv6_regex.match(input_str):
        return "ipv6", input_str
    elif domain_regex.match(input_str):
        return "domain", input_str
    else:
        return "invalid", input_str

def resolve_domain_to_ip(domain: str) -> tuple[str, str]:
    try:
        ip_address = socket.gethostbyname(domain)
        if ipv4_regex.match(ip_address):
            return "ipv4", ip_address
        elif ipv6_regex.match(ip_address):
            return "ipv6", ip_address
        else:
            return "invalid", ip_address
    except socket.gaierror as e:
        logger.error(f"Failed to resolve domain: {e}")
        return "invalid", domain

async def ping_host(
    ctx: arc.GatewayContext,
    url: str,
    api_key: str,
    target: str,
    ip_version: str,
    host: str,
):
    data: dict[str, str] = {
        "api_key": api_key,
        "target_ip": target,
        "ip_version": ip_version,
    }
    response: httpx.Response = await httpx_client.post(url, json=data)

    logger.info(f"Status Code: {response.status_code}")
    logger.info(f"Response Content: {response.text}")

    try:
        json_response = response.json()
        formatted_response = f"Ping result from {host}\n```\n{json_response.get('output')}\n```"
        await ctx.respond(formatted_response)
    except Exception as e:
        logger.error(f"Failed to parse JSON: {e}")
        await ctx.respond(
            f"Error: Unable to parse JSON response. Raw response:\n```\n{response.text}\n```",
        )

@arc_client.include
@arc.slash_command("ping", "Ping test!")
async def handle_ping_command(
    ctx: arc.GatewayContext,
    target: arc.Option[str, arc.StrParams("Which IP or domain do you want to ping?")],
    host: arc.Option[
        str,
        arc.StrParams(
            "Which host do you want to ping from?",
            choices=[
                "Taipei, Taiwan - AS149791 StarVerse Network Ltd.",
                "Taichung, Taiwan - AS17809 VEE TIME CORP.",
                "Taoyuan, Taiwan - AS131596 TBC"
            ],
        ),
    ],
) -> arc.InteractionResponse | None:
    ip_version, detected_target = detect_input_type(target)

    if ip_version == "domain":
        ip_version, detected_target = resolve_domain_to_ip(detected_target)

    if ip_version == "invalid":
        await ctx.respond("Invalid IP address or domain name.")
        return
    
    if host == "Taipei, Taiwan - AS149791 StarVerse Network Ltd.":
        url = os.environ["IP1"]
        api_key = os.environ["APIKEY1"]
    elif host == "Taichung, Taiwan - AS17809 VEE TIME CORP.":
        url = "https://api.cowgl.xyz/ping"
        api_key = ""
    elif host == "Taoyuan, Taiwan - AS131596 TBC":
        url = "https://pingapi.milkteamc.org/ping"
        api_key = ""
    else:
        await ctx.respond("Host not supported yet")
        return

    await ping_host(ctx, url, api_key, detected_target, ip_version, host)
