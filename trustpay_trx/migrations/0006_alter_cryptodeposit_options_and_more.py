# Generated by Django 5.2.3 on 2025-06-21 00:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trustpay_trx', '0005_cryptodeposit_trx_reference_transfer_trx_reference_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cryptodeposit',
            options={},
        ),
        migrations.AlterField(
            model_name='cryptodeposit',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='crypto_trx', to='trustpay_trx.transaction'),
        ),
        migrations.AlterField(
            model_name='cryptodeposit',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_crypto', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterModelTable(
            name='cryptodeposit',
            table=None,
        ),
        migrations.CreateModel(
            name='ChequeDeposit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('cheque_front_img', models.ImageField(blank=True, null=True, upload_to='uploads/cheque/')),
                ('cheque_back_img', models.ImageField(blank=True, null=True, upload_to='uploads/cheque/')),
                ('trx_reference', models.CharField(blank=True, editable=False, max_length=100, null=True, unique=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('transaction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cheque_trx', to='trustpay_trx.transaction')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_cheque', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Cheque Deposit',
                'db_table': 'Cheque Deposit',
            },
        ),
    ]
