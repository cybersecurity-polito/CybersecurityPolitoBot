import json
import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder


def lambda_handler(event, context):
    return asyncio.get_event_loop().run_until_complete(main(event, context))

async def main(event, context):
    token = os.environ.get("TG_TOKEN")
    application = ApplicationBuilder().token(token).build()
    
    try:    
        await application.initialize()
        await application.process_update(
            Update.de_json(json.loads(event["body"]), application.bot)
        )
    
        return {
            'statusCode': 200,
            'body': 'Success'
        }

    except Exception as exc:
        return {
            'statusCode': 500,
            'body': 'Failure'
        }