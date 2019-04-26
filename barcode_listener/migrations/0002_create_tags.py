from django.db import migrations


def add_default(apps, schema_editor):
    # We can't import the model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Tag_Model = apps.get_model('taggit', 'Tag')
    for name, slug in [
        ('reset_stack', '9780002001533'),
        ('frozen', '9770262407312'),
        ('delete_stock', '9780001385108'),
        ('one_weeks_life', '9780001385191'),
        ('two_weeks_life', '9780001022096'),
        ('six_months_life', '9781784707095'),
        ('remaining_0', '9780001385597'),
        ('remaining_10', '9780001385764'),
        ('remaining_25', '9780001967335'),
        ('remaining_50', '9780001967489'),
        ('remaining_75', '9780001979383'),
        ('remaining_100', '9780001401396'),
    ]:
        Tag_Model.objects.create(name=name,
                                 slug=slug
                                 )


class Migration(migrations.Migration):
    dependencies = [
        ('barcode_listener', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_default),
    ]
