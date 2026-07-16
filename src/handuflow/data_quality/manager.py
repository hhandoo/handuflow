# manager.py

from typing import List


class DataQualityManager:

    def __init__(self):
        self.checks = []

    def add_check(self, check):
        self.checks.append(check)

    def run(self, context):

        results = []

        for check in self.checks:
            results.append(check.validate(context))

        return results