# -*- coding: utf-8 -*-

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'config.settings.local')
django.setup()


if __name__ == '__main__':
    from x_factor_be.init_schedule import initialize_schedule_send_notion_calendar

    for initializer in (
        initialize_schedule_send_notion_calendar,
    ):
        try:
            initializer()
        except Exception as e:
            print(f'run {initializer=} get exception {e}')
