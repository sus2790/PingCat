import os
import arc
import hikari
import miru
import requests

bot = hikari.GatewayBot(os.environ["TOKEN"])
arc_client = arc.GatewayClient(bot)
client = miru.Client.from_arc(arc_client)

@arc_client.include
@arc.slash_command("ping", "Ping test!")
async def ping_command(
    ctx: arc.GatewayContext,
    ip: arc.Option[str, arc.StrParams("Which IP do you want to ping?")],
    host: arc.Option[str, arc.StrParams("Which host do you want to ping from?", choices=["Taipei, Taiwan - AS149791 StarVerse Network Ltd.", "Taichung, Taiwan - AS17809 VEE TIME CORP."])],
    ipversion: arc.Option[str, arc.StrParams("Your are using ipv4 or ipv6?", choices=["ipv4", "ipv6"])]
) -> None:
    if host == "Taipei, Taiwan - AS149791 StarVerse Network Ltd.":
        url = os.environ["IP1"]
        data = {
            "api_key": os.environ["APIKEY1"],
            "target_ip": ip,
            "ip_version": ipversion
        }
        response = requests.post(url, data=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")
        
        try:
            json_response = response.json()
            formatted_response = f"```\n{json_response.get("output")}\n```"
            await ctx.respond(formatted_response)
        except requests.JSONDecodeError:
            await ctx.respond(f"Error: Unable to parse JSON response. Raw response:\n```\n{response.text}\n```")
    else:
        await ctx.respond("Host not supported yet")