# Generated by Django 5.0 on 2024-01-02 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_historydata_city_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realdata',
            name='d_temp',
            field=models.DecimalField(decimal_places=1, max_digits=5),
        ),
        migrations.AlterField(
            model_name='realdata',
            name='n_temp',
            field=models.DecimalField(decimal_places=1, max_digits=5),
        ),
        migrations.AlterField(
            model_name='realdata',
            name='rain',
            field=models.DecimalField(decimal_places=1, max_digits=5),
        ),
        migrations.AlterField(
            model_name='realdata',
            name='rain24h',
            field=models.DecimalField(decimal_places=1, max_digits=5),
        ),
        migrations.AlterField(
            model_name='realdata',
            name='temp',
            field=models.DecimalField(decimal_places=1, max_digits=5),
        ),
    ]