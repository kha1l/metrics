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

    async def get_partner_data(self, partner, **kwargs):
        if kwargs:
            units = ','.join(f"'{unit}'" for unit in kwargs['units'])
            sql = f'''
                SELECT t.access, r.name, r.uuid, r.short_id, r.properties, r.tax, r.timezone, t.partner_id 
                FROM tokens t 
                JOIN stationary r ON t.partner_id = r.partner_id
                WHERE t.partner_id = $1 AND r.uuid IN ({units});
            '''
            params = (partner,)
        else:
            sql = '''
                SELECT t.access, r.name, r.uuid, r.short_id, r.properties, r.tax, r.timezone, t.partner_id 
                FROM tokens t 
                JOIN stationary r ON t.partner_id = r.partner_id 
                WHERE t.partner_id = $1;
            '''
            params = (partner,)
        return await self.execute(sql, parameters=params, fetchall=True)
