from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_add_interview_models'),
        ('core', '0004_alter_common_create_date_alter_common_create_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviewfeedback',
            name='vision_analysis',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
    ]
