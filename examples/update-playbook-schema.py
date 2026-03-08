import asyncio
import json

import asyncgateway


async def main():
    cfg = {
        "host": "gateway.privateip.dev",
    }

    asyncgateway.logger.set_level(10)

    schema = {
        "schema": {
            "properties": {
                "message": {"description": "INSERT DESCRIPTION HERE", "type": "string"}
            },
            "required": [],
            "title": "echo",
            "type": "object",
        }
    }

    async with asyncgateway.client(**cfg) as client:
        res = await client.playbooks.update_schema("echo", schema)

    print(json.dumps(res, indent=4))


if __name__ == "__main__":
    asyncio.run(main())
