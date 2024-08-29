import logging
import os

import arc
import hikari
import httpx
import miru

bot = hikari.GatewayBot(os.environ["TOKEN"])
arc_client = arc.GatewayClient(bot)
miru_client: miru.Client = miru.Client.from_arc(arc_client)
httpx_client = httpx.AsyncClient()
logger: logging.Logger = logging.getLogger("PingCat")


@arc_client.include
@arc.slash_command("ping", "Ping test!")
async def handle_ping_command(
    ctx: arc.GatewayContext,
    ip: arc.Option[str, arc.StrParams("Which IP do you want to ping?")],
    host: arc.Option[
        str,
        arc.StrParams(
            "Which host do you want to ping from?",
            choices=[
                "Taipei, Taiwan - AS149791 StarVerse Network Ltd.",
                "Taichung, Taiwan - AS17809 VEE TIME CORP.",
            ],
        ),
    ],
    ipversion: arc.Option[
        str,
        arc.StrParams("Your are using ipv4 or ipv6?", choices=["ipv4", "ipv6"]),
    ],
) -> arc.InteractionResponse | None:
    if host == "Taipei, Taiwan - AS149791 StarVerse Network Ltd.":
        url: str = os.environ["IP1"]
        data: dict[str, str] = {
            "api_key": os.environ["APIKEY1"],
            "target_ip": ip,
            "ip_version": ipversion,
        }
        response: httpx.Response = await httpx_client.post(url, json=data)

        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Content: {response.text}")

        try:
            json_response = await response.json()
            formatted_response = f"```json\n{json_response.get("output")}\n```"
            await ctx.respond(formatted_response)
        except Exception as e:
            logger.info(e)
            return await ctx.respond(
                f"Error: Unable to parse JSON response. Raw response:\n```\n{response.text}\n```",
            )
    else:
        return await ctx.respond("Host not supported yet")
