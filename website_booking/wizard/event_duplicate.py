# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime


class EventWizard(models.TransientModel):

    _name = 'event.duplicate.wizard'

    date_start = fields.Date('Start Date', default=datetime.datetime.today().date(), required=True)
    date_end = fields.Date('End Date', default=datetime.datetime.today().date(), required=True)
    days_0=fields.Boolean(string='Monday')
    days_1=fields.Boolean(string='Tuesday')
    days_2=fields.Boolean(string='Wednesday')
    days_3=fields.Boolean(string='Thursday')
    days_4=fields.Boolean(string='Friday')
    days_5=fields.Boolean(string='Saturday')
    days_6=fields.Boolean(string='Sunday')

    def duplicate(self):
        DATETIME_FORMAT = "%Y-%m-%d"
        id=self.env.context.get("active_ids",[])
        if len(id) > 1:
            raise ValidationError(_("You can not selection many events for duplication !"))

        event=self.env["event.event"].browse(id)
        date_begin_old = datetime.datetime.strptime(event.date_begin[0:10], DATETIME_FORMAT)
        date_end_old = datetime.datetime.strptime(event.date_end[0:10], DATETIME_FORMAT)
        numdays_event = date_end_old - date_begin_old
        time_begin=event.date_begin[11:len(event.date_begin)]
        time_end=event.date_end[11:len(event.date_end)]
        from_dt = datetime.datetime.strptime(self.date_start, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(self.date_end, DATETIME_FORMAT)
        numdays = to_dt - from_dt
        for x in range (0, numdays.days):
            newdate=from_dt + datetime.timedelta(days = x)

            ok=False
            if newdate.weekday()==0 and self.days_0:
                ok=True
            if newdate.weekday()==1 and self.days_1:
                ok=True
            if newdate.weekday()==2 and self.days_2:
                ok=True
            if newdate.weekday()==3 and self.days_3:
                ok=True
            if newdate.weekday()==4 and self.days_4:
                ok=True
            if newdate.weekday()==5 and self.days_5:
                ok=True
            if newdate.weekday()==6 and self.days_6:
                ok=True

            date_begin=str(newdate)[0:10]
            date_end=str(newdate+datetime.timedelta(days =numdays_event.days))[0:10]

            if ok :
                default={
                      'name': event.name,
                      'date_begin':('%s %s')%(date_begin,time_begin),
                      'date_end':('%s %s')%(date_end,time_end),
                     }
                new_event = event.copy(default)
                new_event.write(default)
        return True
