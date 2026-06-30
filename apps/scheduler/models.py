from django.db import models

# Create your models here.
class DayTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class BellEvent(models.Model):
    day = models.ForeignKey(
        DayTemplate,
        on_delete=models.CASCADE,
        related_name="events",
    )

    order = models.PositiveIntegerField()

    label = models.CharField(max_length=100)

    time = models.TimeField()

    duration = models.PositiveIntegerField(default=0)

    source = models.CharField(
        max_length=100,
        default="custom",
    )


class WeekTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)

    monday = models.ForeignKey(
        DayTemplate,
        on_delete=models.PROTECT,
        related_name="+",
    )

    tuesday = models.ForeignKey(
        DayTemplate,
        on_delete=models.PROTECT,
        related_name="+",
    )

    wednesday = models.ForeignKey(
        DayTemplate,
        on_delete=models.PROTECT,
        related_name="+",
    )

    thursday = models.ForeignKey(
        DayTemplate,
        on_delete=models.PROTECT,
        related_name="+",
    )

    friday = models.ForeignKey(
        DayTemplate,
        on_delete=models.PROTECT,
        related_name="+",
    )

    saturday = models.ForeignKey(
        DayTemplate,
        on_delete=models.PROTECT,
        related_name="+",
    )


class MonthTemplate(models.Model):
    name = models.CharField(max_length=100)

    year = models.PositiveIntegerField()

    month = models.PositiveSmallIntegerField()


class MonthAssignment(models.Model):

    month = models.ForeignKey(
        MonthTemplate,
        on_delete=models.CASCADE,
    )

    week = models.ForeignKey(
        WeekTemplate,
        on_delete=models.PROTECT,
    )

    week_number = models.PositiveSmallIntegerField()
