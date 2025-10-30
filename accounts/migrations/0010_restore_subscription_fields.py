# Generated manually to restore fields removed by 0008
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_merge_20251030_0926'),
    ]

    operations = [
        # Restore removed fields
        migrations.AddField(
            model_name='subscription',
            name='api_credit_balance',
            field=models.DecimalField(decimal_places=2, default=0.50, max_digits=10),
        ),
        migrations.AddField(
            model_name='subscription',
            name='expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subscription',
            name='last_credit_refill',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subscription',
            name='stripe_subscription_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        # Restore original plan_type choices
        migrations.AlterField(
            model_name='subscription',
            name='plan_type',
            field=models.CharField(
                choices=[
                    ('free', 'Free'),
                    ('pay_per_doc', 'Pay Per Document'),
                    ('unlimited', 'Unlimited')
                ],
                default='free',
                max_length=20
            ),
        ),
        # Restore original payment_type choices
        migrations.AlterField(
            model_name='payment',
            name='payment_type',
            field=models.CharField(
                choices=[
                    ('pay_per_doc', 'Pay Per Document'),
                    ('unlimited', 'Unlimited Plan'),
                    ('api_credit', 'API Credit Top-Up')
                ],
                max_length=20
            ),
        ),
    ]
