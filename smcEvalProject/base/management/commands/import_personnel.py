import re
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from base.models import PersonnelInfo  

class Command(BaseCommand):
    help = "Import users from personnel_info.sql into Django"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help="Path to the personnel_info.sql file",
            required=True,
        )

    def handle(self, *args, **options):
        sql_file = options["file"]
        with open(sql_file, "r", encoding="utf-8") as f:
            content = f.read()

        insert_matches = re.findall(
            r"INSERT INTO `personnel_info` .*? VALUES\s*(.*?);", content, re.DOTALL
        )

        total_imported = 0

        for match in insert_matches:
            rows = re.findall(r"\([^\)]*?\)", match, re.DOTALL)
            for row in rows:
                row = row.strip()[1:-1]
                values = re.findall(r"'(.*?)'|NULL", row)

                if len(values) < 5:
                    continue
                position = values[0] if values[0] != "NULL" else ""
                first_name = values[1] if values[1] != "NULL" else ""
                last_name = values[2] if values[2] != "NULL" else ""
                username = values[3] if values[3] != "NULL" else ""
                password = values[4] if values[4] != "NULL" else ""

                user, created = User.objects.get_or_create(username=username)
                user.first_name = first_name
                user.last_name = last_name
                user.password = password  
                user.save()

                PersonnelInfo.objects.update_or_create(
                    user=user,
                    defaults={"position": position},
                )

                total_imported += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {total_imported} users successfully!"))
