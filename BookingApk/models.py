from django.db import models


class Theater(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Screen(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} - {self.theater.name}"


class WeeklySchedule(models.Model):
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10) 
    open_time = models.TimeField()
    close_time = models.TimeField()

    def __str__(self):
        return f"{self.day_of_week}: {self.open_time} - {self.close_time} ({self.screen})"


class Slot(models.Model):
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)
    movie = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.movie} ({self.start_time} - {self.end_time})"



class Unavailability(models.Model):
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='unavailabilities')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    reason = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.screen} unavailable from {self.start_time} to {self.end_time}"
