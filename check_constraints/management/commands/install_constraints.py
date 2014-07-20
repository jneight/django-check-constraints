# coding=utf-8

"""Code based in the django_check_constraints.diff patch from original project

https://github.com/theju/django-check-constraints/blob/master/django_check_constraints.diff

"""
from django.db import connection
from django.core.management.base import BaseCommand
from django.db import models
from django.core.management.color import color_style as style


class Command(BaseCommand):
    help = u'Installs or updates all the constraints'

    def handle(self, *args, **kwargs):
        """Will search in all installed models to find which ones define
        a constraint. No constraint is modified until all are valid.

        In case a constrait name is already used, will raise and
            exception
        """
        cursor = connection.cursor()
        for model in models.get_models(include_auto_created=True):
            if getattr(model._meta, 'constraints', []):
                check_names = []
                sql_for_constraints = []
                for check in model._meta.constraints:
                    check_name, check_obj = check
                    if not check_name in check_names:
                        check_names.append(check_name)
                        check_obj.check_name = check_name
                        alter_sql = u'ALTER TABLE {0}'.format(model._meta.db_table)
                        drop_sql = u'{0} DROP CONSTRAINT IF EXISTS {1}'.format(
                            alter_sql, check_name)
                        cursor.execute(drop_sql)
                        add_sql = u'{0} ADD {1}'.format(
                            alter_sql, check_obj.generate_sql(connection, style()))
                        self.stdout.write('\033[01;32mAdding constraint: \033[m{0}'.format(
                            add_sql))
                        sql_for_constraints.append(';'.join([
                            drop_sql, u'{0} ADD {1}'.format(
                                alter_sql, check_obj.generate_sql(connection, style))]))
                    else:
                        raise Exception(
                            u'\033[01;31m{0} already defined in {1}'.format(
                            check_name, model.__class__))
                    cursor.execute(';'.join(sql_for_constraints))

        self.stdout.write('\n\033[01;32mConstraints installed!')
