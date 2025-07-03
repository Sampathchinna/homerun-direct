
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_id', models.CharField(max_length=100)),
                ('value', models.CharField(choices=[('corporation', 'Corporation'), ('sole_prop', 'Sole Proprietorship'), ('non_profit', 'Non-Profit'), ('partnership', 'Partnership'), ('llc', 'LLC'), ('other', 'Other')], max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_id', models.CharField(max_length=100)),
                ('value', models.CharField(choices=[('aud', 'AUD'), ('brl', 'BRL'), ('cad', 'CAD'), ('chf', 'CHF'), ('cny', 'CNY'), ('eur', 'EUR'), ('gbp', 'GBP'), ('hkd', 'HKD'), ('inr', 'INR'), ('jpy', 'JPY'), ('krw', 'KRW'), ('mxn', 'MXN'), ('nok', 'NOK'), ('nzd', 'NZD'), ('rub', 'RUB'), ('sek', 'SEK'), ('sgd', 'SGD'), ('try', 'TRY'), ('usd', 'USD'), ('zar', 'ZAR'), ('clp', 'CLP'), ('thb', 'THB')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_id', models.CharField(max_length=100)),
                ('value', models.CharField(choices=[('ar', 'AR'), ('bn', 'BN'), ('cs', 'CS'), ('da', 'DA'), ('nl', 'NL'), ('en', 'EN'), ('et', 'ET'), ('fr', 'FR'), ('de', 'DE'), ('el', 'EL'), ('hi', 'HI'), ('hu', 'HU'), ('id', 'ID'), ('it', 'IT'), ('ja', 'JA'), ('jv', 'JV'), ('ko', 'KO'), ('nb', 'NB'), ('pa', 'PA'), ('pl', 'PL'), ('pt', 'PT'), ('ru', 'RU'), ('es', 'ES'), ('sv', 'SV'), ('th', 'TH'), ('tr', 'TR'), ('vi', 'VI'), ('zh', 'ZH')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='LocationableType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=51, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('old_id', models.CharField(max_length=100)),
                ('value', models.CharField(choices=[('bnb', 'Bnb'), ('hotel', 'Hotel'), ('hostel', 'Hostel'), ('vacation_rental', 'Vacation Rental'), ('rv_fleet', 'RV fleet')], max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PaymentProcessor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=100)),
                ('value', models.CharField(choices=[('stripe', 'Stripe'), ('lynbrook', 'Lynnbrook')], max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PropertyType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('old_id', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('apt_suite', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(max_length=100, null=True)),
                ('state_province', models.CharField(max_length=100, null=True)),
                ('postal_code', models.CharField(max_length=20, null=True)),
                ('country', models.CharField(max_length=100, null=True)),
                ('street_address', models.CharField(max_length=255, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=9, max_digits=12, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=9, max_digits=12, null=True)),
                ('exact', models.BooleanField(blank=True, null=True)),
                ('timezone', models.CharField(blank=True, max_length=53, null=True)),
                ('raw_json', models.JSONField(blank=True, null=True)),
                ('locationable_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.locationabletype')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('interval', models.CharField(choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')], max_length=20)),
                ('price_cents', models.IntegerField()),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master.paymentprocessor')),
            ],
        ),
    ]
