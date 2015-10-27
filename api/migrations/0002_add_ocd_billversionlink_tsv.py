from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL([
        "ALTER TABLE opencivicdata_billversionlink add column tsv tsvector;",
        "CREATE INDEX ocd_billversionlink_tsv_idx ON opencivicdata_billversionlink USING gin(tsv);",
        "UPDATE opencivicdata_billversionlink SET tsv = to_tsvector('english', text);",
        ("CREATE TRIGGER opencivicdata_billversionlink_tsv_update BEFORE INSERT OR UPDATE"
            " ON opencivicdata_billversionlink FOR EACH ROW EXECUTE PROCEDURE"
            " tsvector_update_trigger(tsv, 'pg_catalog.english', text);"),
    ])
    ]
