import asyncio
import json

import asyncgateway


async def main():
    cfg = {
        "host": "gateway.privateip.dev",
    }

    asyncgateway.logger.set_level(10)

    async with asyncgateway.client(**cfg) as client:
        res = await client.playbooks.get_all()

    print(json.dumps(res, indent=4))


if __name__ == "__main__":
    asyncio.run(main())
