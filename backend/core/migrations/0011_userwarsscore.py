# Generated manually on 2026-03-04
# Wars 미니게임 점수 기록 모델 추가 (명예의 전당 연동)

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_userbattlerecord_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserWarsScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_id', models.CharField(blank=True, help_text='생성자 ID', max_length=50, null=True)),
                ('update_id', models.CharField(blank=True, help_text='수정자 ID', max_length=50, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, help_text='생성 일시')),
                ('update_date', models.DateTimeField(auto_now=True, help_text='수정 일시')),
                ('use_yn', models.CharField(default='Y', help_text='사용 여부 (Y/N)', max_length=1)),
                ('game_type', models.CharField(help_text='미니게임 종류 (logic_run, code_typing 등)', max_length=30)),
                ('score', models.IntegerField(default=0, help_text='획득 점수 (0-100)')),
                ('submitted_data', models.JSONField(blank=True, help_text='게임 결과 상세 (난이도, 페이즈별 점수, 등급 등)', null=True)),
                ('is_perfect', models.BooleanField(default=False, help_text='만점 여부')),
                ('user', models.ForeignKey(help_text='점수 소유자', on_delete=django.db.models.deletion.CASCADE, related_name='wars_scores', to='core.userprofile')),
            ],
            options={
                'verbose_name': 'Wars 게임 점수',
                'verbose_name_plural': 'Wars 게임 점수 목록',
                'db_table': 'gym_wars_score',
            },
        ),
    ]
