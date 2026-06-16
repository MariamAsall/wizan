from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0004_user_is_approved"),
    ]

    operations = [
        migrations.CreateModel(
            name="VoiceLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("transcribed_text", models.TextField(help_text="The text output from Samy's STT function. Never store audio here.")),
                ("agent_response", models.TextField(blank=True, help_text="The daily plan text returned by the Planning Agent.")),
                ("action_type", models.CharField(
                    choices=[
                        ("plan_request", "Plan Request"),
                        ("task_add", "Task Add"),
                        ("query", "Query"),
                    ],
                    default="plan_request",
                    max_length=20,
                )),
                ("status", models.CharField(
                    choices=[
                        ("success", "Success"),
                        ("failed", "Failed"),
                        ("partial", "Partial"),
                    ],
                    default="success",
                    max_length=10,
                )),
                ("session_id", models.CharField(blank=True, max_length=255)),
                ("error_message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="voice_logs",
                    to="users.user",
                )),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
