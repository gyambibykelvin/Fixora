from django.db import migrations


def normalize_service_modes(apps, schema_editor):
    Provider = apps.get_model('provider', 'Provider')

    for provider in Provider.objects.all().iterator():
        if provider.service_mode in {'home', 'walk_in'}:
            continue

        provider.service_mode = (
            'home' if provider.delivery_type == 'home_service' else 'walk_in'
        )
        provider.save(update_fields=['service_mode'])


def reverse_normalization(apps, schema_editor):
    Provider = apps.get_model('provider', 'Provider')

    for provider in Provider.objects.all().iterator():
        provider.service_mode = 'home'
        provider.save(update_fields=['service_mode'])


class Migration(migrations.Migration):
    dependencies = [
        ('provider', '0004_provider_service_mode_and_more'),
    ]

    operations = [
        migrations.RunPython(normalize_service_modes, reverse_normalization),
    ]
