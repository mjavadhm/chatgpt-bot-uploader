import asyncio
import telegram


async def main():
    bot = telegram.Bot("6821047694:AAHpK7nIUrQW-53ifVtPwBaQikGaHM4s_dg")
    async with bot:
        await bot.send_message(text='hi', chat_id=5368372729)

if __name__ == '__main__':
    asyncio.run(main())
