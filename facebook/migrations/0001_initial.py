# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActionsFacebook',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('post_id', models.BigIntegerField()),
                ('facebook_user_id', models.BigIntegerField()),
                ('action', models.CharField(choices=[('shared', 'Shared'), ('comment', 'Comment'), ('like', 'Like'), ('retweet', 'Retweet'), ('tweet', 'Tweet')], max_length=10)),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='date published')),
            ],
        ),
        migrations.CreateModel(
            name='PostsTrace',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('facebook_id', models.BigIntegerField(unique=True)),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='date published')),
            ],
        ),
        migrations.CreateModel(
            name='TokenPage',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('token', models.CharField(unique=True, max_length=400)),
                ('provider', models.CharField(choices=[('facebook', 'Facebook'), ('ahorrando', 'Ahorrando'), ('twitter', 'Twitter')], max_length=10, verbose_name='provider')),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='date published')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='actionsfacebook',
            unique_together=set([('post_id', 'facebook_user_id', 'action')]),
        ),
    ]
