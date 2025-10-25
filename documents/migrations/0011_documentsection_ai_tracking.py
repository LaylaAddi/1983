# Generated migration for AI enhancement tracking

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0010_purchaseddocument'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentsection',
            name='ai_enhanced',
            field=models.BooleanField(default=False, help_text='Whether this section was enhanced using AI'),
        ),
        migrations.AddField(
            model_name='documentsection',
            name='ai_cost',
            field=models.DecimalField(decimal_places=4, default=0.0, help_text='Cost of AI enhancement in USD', max_digits=6),
        ),
        migrations.AddField(
            model_name='documentsection',
            name='ai_model',
            field=models.CharField(blank=True, help_text='AI model used (e.g., gpt-4o)', max_length=50),
        ),
    ]
