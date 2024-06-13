import asyncio

from storage import external_links
from settings import START_URLS

crawler_processes = {}


def on_startup():
    for link in START_URLS:
        external_links.append(link)


async def named_counter(name: str):
    i = 0
    for i in range(5):
        await asyncio.sleep(1)
        print(f"{name} count: {i}")
        i += 1
    print(f"{name} finished")
    crawler_processes.pop(name)


async def main_loop():
    task_num = 1
    on_startup()
    async with asyncio.TaskGroup() as tg:
        while True:
            await asyncio.sleep(0.1)
            if len(crawler_processes) < 2:
                print(len(crawler_processes))
                # crawler_processes.add(
                # tg.create_task(named_counter(name=f"Task {task_num}"))
                # )
                task_name = f"Task {task_num}"
                crawler_processes[task_name] = tg.create_task(
                    named_counter(name=task_name)
                )
                task_num += 1


asyncio.run(main_loop())
