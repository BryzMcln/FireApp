from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fire', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firefighters',
            name='experience_level',
            field=models.CharField(choices=[('Probationary Firefighter', 'Probationary Firefighter'), ('Firefighter I', 'Firefighter I'), ('Firefighter II', 'Firefighter II'), ('Firefighter III', 'Firefighter III'), ('Driver', 'Driver'), ('Captain', 'Captain'), ('Battalion Chief', 'Battalion Chief')], max_length=45),
        ),
        migrations.AlterField(
            model_name='firefighters',
            name='station',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fire.firestation'),
        ),
    ]