# coding=utf-8

from django.db import models

from check_constraints import Check
from metaclass import CheckConstraintMetaClass


models.options.DEFAULT_NAMES += ('constraints', )
