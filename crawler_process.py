import asyncio
from typing import Awaitable


from settings import MAX_PROCESS
from utils import logger


class ProcessHandler(asyncio.TaskGroup):
    max_process = MAX_PROCESS
    awailable_numbers = [f"Task {i}" for i in range(1, MAX_PROCESS + 1)]
    process_dict: dict[int, asyncio.Task] = {}
    lock = asyncio.Lock()

    async def get_awailable_name(self):
        async with self.lock:
            return self.awailable_numbers.pop()

    async def add_awailable_name(self, name: str):
        async with self.lock:
            return self.awailable_numbers.append(name)

    async def wrap_process(self, func: Awaitable, task_name: str, **kwargs):
        await func(**kwargs)
        try:
            self.process_dict.pop(task_name)
            await self.add_awailable_name(task_name)
        except Exception as e:
            raise

    async def create_task(self, func: Awaitable, **kwargs):
        if len(self.process_dict.keys()) < self.max_process:
            task_name = await self.get_awailable_name()
            task = super().create_task(
                self.wrap_process(func, task_name=task_name, **kwargs), name=task_name
            )
            self.process_dict[task_name] = task


if __name__ == "__main__":

    async def main_loop():
        # on_startup()
        # async with asyncio.TaskGroup() as tg:
        #     while True:
        #         await asyncio.sleep(0.1)
        #         # await process_manager(tg, named_counter)
        #         if len(tg._tasks) < MAX_PROCESS:
        #             task = tg.create_task(named_counter(name="task"))
        #             crawler_processes[task.get_name()] = task
        #             awailable_numbers.add(task.get_name())
        # print(awailable_numbers)
        async with ProcessHandler() as ph:
            while True:
                await asyncio.sleep(0.1)
                # ph.create_task(named_counter, name="test")

    asyncio.run(main_loop())
