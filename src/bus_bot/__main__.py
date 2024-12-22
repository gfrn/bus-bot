import os
import aiohttp
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from datetime import datetime

from bus_bot.models.responses import Call, StopUpdate

from .utils.events import Periodic

from .crud.alert import delete_alert, get_alerts, insert_alert, update_alert
import asyncio
from .models.database import async_main

TOKEN = os.environ.get("SLACK_BOT_TOKEN")

app = AsyncApp(token=TOKEN)


@app.command("/list")
async def list_alerts(ack, respond, command):
    await ack()
    alerts = await get_alerts(user=command["channel_id"])

    msg = "\n".join(
        [
            f"*{alert.id}*: *{alert.line}* at *{alert.stop.name}* at *{alert.alertTime}*"
            for alert in alerts
        ]
    )

    if msg == "":
        await respond("No alerts found")
        return

    await respond(msg)


# TODO: replace this with button press event
@app.command("/delete")
async def remove_alert(ack, respond, command):
    await ack()
    if command["text"] is None:
        await respond("No alert ID provided")
        return

    try:
        await delete_alert(int(command["text"]))
        await respond(f"Alert *{command["text"]}* successfully deleted!")
    except ValueError:
        await respond("Alert does not exist")


@app.command("/register")
async def subscribe_to_stop(ack, respond, command):
    await ack()
    args = command["text"].split(" ")

    if len(args) != 3:
        await respond("Unknown arguments provided")

    naptan, line, time_str = args
    try:
        time = datetime.strptime(time_str, "%H:%M").time()
        await insert_alert(command["channel_id"], naptan, time, line)
    except ValueError:
        await respond("Invalid time provided. Time must be formatted as HH:MM")
        return

    await respond(f"Successfully registered alert for *{naptan}* at *{time_str}*")


async def send_alerts():
    time = datetime.now().time()

    # Get alerts within 10 minutes of the user-specified alert time
    alerts = await get_alerts(time)
    last_atco: str | None = None
    last_update: StopUpdate | None = None
    last_call: Call | None = None

    async with aiohttp.ClientSession() as http_session:
        for alert in alerts:
            # Iterate through ATCO groups, to avoid making redundant requests
            if alert.atco != last_atco:
                async with http_session.get(
                    f"https://oxontime.com/pwi/departureBoard/{alert.atco}"
                ) as resp:
                    resp_json = await resp.json(content_type="text/html")
                    last_update = StopUpdate.model_validate(resp_json[alert.atco])

            if last_update is not None and (
                last_call is None or alert.line != last_call.route_code
            ):
                try:
                    last_call = next(
                        call
                        for call in last_update.calls
                        if call.route_code == alert.line
                    )
                except StopIteration:
                    last_call = None

            if last_call:
                await app.client.chat_postMessage(
                    channel=alert.user,
                    token=TOKEN,
                    markdown=True,
                    text=f"*{alert.line}* arriving in *{last_call.time_to_arrival} min* at {alert.stop.name}",
                )

            await update_alert(alert_id=alert.id)


async def main():
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    alert_loop = Periodic(send_alerts, 60)
    await alert_loop.start()

    await async_main()
    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(main())
