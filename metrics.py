"""
    Вызов главной функции с передачей ей:
    1. partner: tuple() - (id партнера, [список групп метрик])
    2. date_start, date_end - даты начала и окончания периода
    3. units - [список uuid ресторанов]
"""
from database.db import Database
from configuration.conf import Settings
from functions.delivery import Delivery
from functions.staffmeal import StaffMeal
from functions.refusal import Refusal
from functions.handover import Handover
from functions.salary import Salary
from functions.shifts import Shifts
from functions.couriersorders import CouriersOrders


async def work_metrics(partner, date_start, date_end, **kwargs):
    db = Database()
    partner_id = partner[0]
    partner_groups = partner[1]
    units_metrics = {}
    if kwargs:
        units = kwargs["units"]
        data_units = await db.get_partner_data(partner_id, units=units)
    else:
        data_units = await db.get_partner_data(partner_id)
    for data in data_units:
        stg = Settings()
        objects_dict = {}
        for group in partner_groups:
            metrics_group = stg.groups[group]
            if isinstance(metrics_group, Delivery):
                orders_delivery = objects_dict[1].orders_delivery
                await metrics_group.app(orders_delivery, data, date_start, date_end)
            elif isinstance(metrics_group, StaffMeal) or isinstance(metrics_group, Refusal):
                revenue = objects_dict[1].revenue
                await metrics_group.app(revenue, data, date_start, date_end)
            elif isinstance(metrics_group, Handover):
                orders_stationary = objects_dict[1].orders_stationary
                await metrics_group.app(orders_stationary, data, date_start, date_end)
            elif isinstance(metrics_group, Salary):
                orders_delivery = objects_dict[1].orders_delivery
                revenue = objects_dict[1].revenue
                revenue_delivery = objects_dict[1].revenue_delivery
                await metrics_group.app(revenue, revenue_delivery, orders_delivery, data, date_start, date_end)
            elif isinstance(metrics_group, Shifts):
                hours = objects_dict[2].schedule_work_hours
                await metrics_group.app(hours, data, date_start, date_end)
            elif isinstance(metrics_group, CouriersOrders):
                orders_delivery = objects_dict[1].orders_delivery
                orders_stationary = objects_dict[1].orders_stationary
                await metrics_group.app(orders_delivery, orders_stationary, data, date_start, date_end)
            else:
                await metrics_group.app(data, date_start, date_end)
            objects_dict[group] = metrics_group
            await metrics_group.reset()
        units_metrics[data['uuid']] = objects_dict
    return units_metrics
