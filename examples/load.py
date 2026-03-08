import asyncio
import json

import asyncgateway
from asyncgateway.services import Operation


async def main():
    cfg = {
        "host": "gateway.privateip.dev",
    }

    with open("examples/sample_devices.json", "r") as f:
        content = f.read()

    data = json.loads(content)

    asyncgateway.logger.set_level(10)

    async with asyncgateway.client(**cfg) as client:
        res = await client.devices.load(data, Operation.REPLACE)

    print(json.dumps(res, indent=4))


if __name__ == "__main__":
    asyncio.run(main())
