
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('url_path', models.CharField(max_length=255, unique=True)),
                ('model_path', models.CharField(help_text='e.g. rbac.Organizations', max_length=255)),
                ('meta', models.JSONField(blank=True, default=dict)),
                ('form', models.JSONField(blank=True, default=dict)),
                ('actions', models.JSONField(blank=True, default=dict)),
                ('table', models.JSONField(blank=True, default=dict)),
                ('layout', models.JSONField(blank=True, default=list)),
                ('permissions', models.JSONField(blank=True, default=list)),
                ('POST', models.JSONField(blank=True, default=dict)),
                ('post_heading', models.JSONField(blank=True, default=dict)),
                ('post_description', models.JSONField(blank=True, default=dict)),
                ('extra_field', models.JSONField(blank=True, default=dict)),
                ('extra_parameter', models.JSONField(blank=True, default=dict)),
                ('post_tabs', models.JSONField(blank=True, default=dict)),
                ('post_order', models.JSONField(blank=True, null=True)),
            ],
        ),
    ]
