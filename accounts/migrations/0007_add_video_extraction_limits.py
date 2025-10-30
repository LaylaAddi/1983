# Generated manually for Phase 1.4
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_userprofile_referred_by_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='monthly_extractions_count',
            field=models.IntegerField(default=0, help_text='Number of video extractions this month'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='extractions_reset_date',
            field=models.DateField(blank=True, help_text='Date when monthly extraction counter resets', null=True),
        ),
    ]
