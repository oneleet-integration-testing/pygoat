"""Rehash the one legacy CSRF lab account with a published password.

An MD5 digest cannot generally be converted into a password hash because the
original password is unavailable. The CSRF lab publishes credentials for only
one account, so this migration changes that account only when its stored value
matches the digest created by the prior implementation.
"""

from django.contrib.auth.hashers import make_password
from django.db import migrations


LEGACY_USERNAME = "susUser2878"
PUBLISHED_PASSWORD = "SUsUserpAsswOrd"
# This identifies data written by the former implementation; it is not used to
# protect a password. It keeps the migration restricted to the published account.
LEGACY_PASSWORD_DIGEST = "a0f6ce4bb84f841dc214cc083387c1eb"


def rehash_published_legacy_password(apps, schema_editor):
    CSRFUser = apps.get_model("introduction", "CSRF_user_tbl")
    CSRFUser.objects.filter(
        username=LEGACY_USERNAME,
        password=LEGACY_PASSWORD_DIGEST,
    ).update(password=make_password(PUBLISHED_PASSWORD))


class Migration(migrations.Migration):
    dependencies = [
        ("introduction", "0021_csrf_user_tbl"),
    ]

    operations = [
        migrations.RunPython(rehash_published_legacy_password, migrations.RunPython.noop),
    ]
