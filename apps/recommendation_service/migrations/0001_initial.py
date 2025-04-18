# Generated by Django 5.2 on 2025-04-05 14:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProductSentiment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.IntegerField(unique=True)),
                ('overall_sentiment', models.FloatField()),
                ('sentiment_distribution', models.JSONField()),
                ('key_positive_aspects', models.JSONField(default=list)),
                ('key_negative_aspects', models.JSONField(default=list)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'product_sentiments',
            },
        ),
        migrations.CreateModel(
            name='UserPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(unique=True)),
                ('favorite_categories', models.JSONField(default=list)),
                ('preferred_price_range', models.JSONField(default=dict)),
                ('disliked_products', models.JSONField(default=list)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'user_preferences',
            },
        ),
        migrations.CreateModel(
            name='RecommendationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('product_id', models.IntegerField()),
                ('action_type', models.CharField(max_length=50)),
                ('recommendation_type', models.CharField(max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'recommendation_logs',
                'indexes': [models.Index(fields=['user_id'], name='recommendat_user_id_f4c2a4_idx'), models.Index(fields=['product_id'], name='recommendat_product_d07e65_idx'), models.Index(fields=['timestamp'], name='recommendat_timesta_cf0e8e_idx')],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('rating', models.IntegerField()),
                ('title', models.CharField(blank=True, max_length=255)),
                ('comment', models.TextField(blank=True)),
                ('verified_purchase', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('helpful_votes', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'reviews',
                'indexes': [models.Index(fields=['product_id'], name='reviews_product_3516b2_idx'), models.Index(fields=['user_id'], name='reviews_user_id_79db63_idx'), models.Index(fields=['created_at'], name='reviews_created_53b5d6_idx')],
                'unique_together': {('product_id', 'user_id')},
            },
        ),
        migrations.CreateModel(
            name='ReviewImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='recommendation_service.review')),
            ],
            options={
                'db_table': 'review_images',
            },
        ),
        migrations.CreateModel(
            name='ReviewResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vendor_id', models.IntegerField()),
                ('response_text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='recommendation_service.review')),
            ],
            options={
                'db_table': 'review_responses',
            },
        ),
    ]
