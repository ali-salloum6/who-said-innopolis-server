import asyncio
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
from datetime import datetime, timedelta
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import InputMessagesFilterEmpty
from flask import Flask, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
session = os.getenv('TELEGRAM_SESSION')
filename = './data/channels.txt'
with open(filename) as input_data:
    channels = list(item.rstrip() for item in input_data.readlines())

tokenizer = RegexTokenizer()
model = FastTextSocialNetworkModel(tokenizer=tokenizer)

def get_sentiment(text):
    results = model.predict([text], k=2)
    sentiment = next(iter(results[0]))
    return sentiment

async def get_channel_messages():
    # Create a TelegramClient instance
    client = TelegramClient(StringSession(session), api_id, api_hash)
    await client.start()

    try:
        todays_messages = []
        todays_forwarded_messages = []
        for index, channel in enumerate(channels):
            print("@", channel, sep='')
            print(index, "/", len(channels))
            # Get the entity (channel) using its username
            try:
                entity = await client.get_entity(channel)
            except:
                continue

            messages = client.iter_messages(
                entity, filter=InputMessagesFilterEmpty())

            # Get today's date
            today = datetime.now().date() - timedelta(days=1)

            async for message in messages:
                # Extract only the date portion of the message date
                message_date = message.date.date()

                # Compare the message date with today's date
                if message_date < today:
                    break

                if message and message.message:
                    if 'иннополис' in message.message.lower() or 'innopolis' in message.message.lower():
                        if message.fwd_from:
                            todays_forwarded_messages.append(
                                (channel, message))
                        else:
                            todays_messages.append((channel, message))

        # Generate the report
        report = f"{today.strftime('%d of %B')}:\n"
        if todays_messages:
            report += f"Innopolis was mentioned in the following {len(todays_messages)} sources:\n"
            for (channel, message) in todays_messages:
                report += f"Sentiment: {get_sentiment(message.text)}\n"
                report += f"Link: https://t.me/{channel}/{message.id}\n"
                report += f"Message: {message.message}\n"
                report += f"Date: {message.date}\n\n"
                report += f"##################\n\n"
        if todays_forwarded_messages:
            report += "Innopolis was forwarded in the following sources:\n"
            for (channel, message) in todays_forwarded_messages:
                report += f"Sentiment: {get_sentiment(message.text)}\n"
                report += f"Link: https://t.me/{channel}/{message.id}\n"
                report += f"Message: {message.message}\n"
                report += f"Date: {message.date}\n\n"
        if len(todays_forwarded_messages) == 0 and len(todays_messages) == 0:
            report += "No messages mentioning Innopolis found today.\n"

        return report

    finally:
        await client.disconnect()


@app.route('/')
def messages():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    messages = loop.run_until_complete(get_channel_messages())
    loop.close()
    return messages


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
