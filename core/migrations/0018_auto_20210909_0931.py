# Generated by Django 3.2.6 on 2021-09-09 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_refund'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='address_type',
            field=models.CharField(choices=[('B', 'Billing'), ('S', 'Shipping')], default='B', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='address',
            name='default',
            field=models.BooleanField(default=False),
        ),
    ]
