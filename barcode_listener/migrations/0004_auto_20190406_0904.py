# Generated by Django 2.2 on 2019-04-06 09:04

import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('barcode_listener', '0003_stock'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upcnumber', models.CharField(blank=True, max_length=32)),
                ('created_at', models.DateTimeField(blank=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='stock',
            options={'ordering': ['-modified_at', '-created_at'], 'verbose_name_plural': 'Stock'},
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.',
                                                  through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='stock',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.',
                                                  through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]