# Generated by Django 2.2 on 2019-04-06 12:20

import django.db.models.deletion
import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('barcode_listener', '0004_auto_20190406_0904'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaggedProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaggedStock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='log',
            options={'ordering': ['pk'], 'verbose_name_plural': 'Log'},
        ),
        migrations.AlterField(
            model_name='product',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.',
                                                  through='barcode_listener.TaggedProduct', to='taggit.Tag',
                                                  verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='stock',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.',
                                                  through='barcode_listener.TaggedStock', to='taggit.Tag',
                                                  verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='taggedstock',
            name='content_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='barcode_listener.Stock'),
        ),
        migrations.AddField(
            model_name='taggedstock',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='barcode_listener_taggedstock_items', to='taggit.Tag'),
        ),
        migrations.AddField(
            model_name='taggedproduct',
            name='content_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='barcode_listener.Product'),
        ),
        migrations.AddField(
            model_name='taggedproduct',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='barcode_listener_taggedproduct_items', to='taggit.Tag'),
        ),
    ]
