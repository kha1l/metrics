import asyncpg
from configuration.conf import Config

class Database:
    def __init__(self):
        self.config = Config()
        self.dsn = f"postgresql://{self.config.user}:{self.config.password}@{self.config.host}:5432/{self.config.dbase}"

    async def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False):
        pool = await asyncpg.create_pool(dsn=self.dsn)
        if not parameters:
            parameters = tuple()
        async with pool.acquire() as connection:
            data = None
            async with connection.transaction():
                if fetchone:
                    data = await connection.fetchrow(sql, *parameters)
                elif fetchall:
                    data = await connection.fetch(sql, *parameters)
                else:
                    await connection.execute(sql, *parameters)
        await pool.close()
        return data
