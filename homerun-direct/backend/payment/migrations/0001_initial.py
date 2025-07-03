
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StripeCustomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_customer_id', models.CharField(max_length=255)),
                ('stripe_subscription_id', models.CharField(blank=True, max_length=255, null=True)),
                ('stripe_payment_method_id', models.CharField(blank=True, max_length=255, null=True)),
                ('stripe_price_id', models.CharField(blank=True, max_length=255, null=True)),
                ('latest_invoice_url', models.URLField(blank=True, null=True)),
                ('subscription_status', models.CharField(choices=[('active', 'Active'), ('past_due', 'Past Due'), ('canceled', 'Canceled'), ('incomplete', 'Incomplete'), ('trialing', 'Trialing')], default='incomplete', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='stripe_data', to='organization.organization')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
