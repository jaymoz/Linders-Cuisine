# Generated by Django 3.1.7 on 2021-04-13 09:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_remove_services_title_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryFee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_fee', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('delivery_method', models.CharField(choices=[('self pickup', 'Self Pickup'), ('delivery', 'Delivery')], max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Delivery Fee',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_fee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='app.deliveryfee'),
        ),
    ]
