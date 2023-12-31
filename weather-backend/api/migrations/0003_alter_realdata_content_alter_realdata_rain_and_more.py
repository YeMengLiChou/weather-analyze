# Generated by Django 5.0 on 2024-01-02 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_rename_historyweatheritem_historydata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realdata',
            name='content',
            field=models.CharField(max_length=1500),
        ),
        migrations.AlterField(
            model_name='realdata',
            name='rain',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='realdata',
            name='rain24h',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='realdata',
            name='w_level',
            field=models.IntegerField(max_length=10),
        ),
    ]
