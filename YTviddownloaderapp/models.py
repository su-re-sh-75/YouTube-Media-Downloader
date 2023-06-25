from django.db import models

class History(models.Model):
    # History table in ORM(object-Relational Mapping)
    down_link = models.URLField()
    down_time = models.DateTimeField(auto_now_add=True)
    down_type = models.CharField(max_length=10)
    class Meta:
        db_table = 'Download_history'
    def __str__(self):
        return self.down_link