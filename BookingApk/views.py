from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from .models import Theater, Screen, WeeklySchedule, Slot, Unavailability
from .serializers import WeeklyScheduleSerializer, UnavailabilitySerializer, SlotSerializer

class TheaterAvailabilityView(APIView):
    """
    API to configure weekly schedules and weekly unavailability for a theater.
    """

    def post(self, request, id):
        try:
         
            theater = Theater.objects.get(id=id)
            
       
            screen = Screen.objects.filter(theater=theater).first()

          
            if not screen:
                return Response({"error": "No screens available for this theater."}, status=status.HTTP_404_NOT_FOUND)

            data = request.data

            for day, times in data.get("weekly_schedule", {}).items():
               
                open_time = datetime.strptime(times["open"], "%H:%M").time()
                close_time = datetime.strptime(times["close"], "%H:%M").time()

               
                weekly_schedules = WeeklySchedule.objects.filter(screen=screen, day_of_week=day)

                if weekly_schedules.exists():
                    
                    if weekly_schedules.count() > 1:
                        raise ValueError(f"Multiple weekly schedules found for {day}. Please check the data.")
                  
                    weekly_schedule = weekly_schedules.first()
                    weekly_schedule.open_time = open_time
                    weekly_schedule.close_time = close_time
                    weekly_schedule.save()
                else:
                
                    WeeklySchedule.objects.create(
                        screen=screen,
                        day_of_week=day,
                        open_time=open_time,
                        close_time=close_time
                    )

            for day, unavailable_times in data.get("weekly_unavailability", {}).items():
                for time_range in unavailable_times:
                    start_time = datetime.strptime(time_range["start"], "%H:%M").time()
                    end_time = datetime.strptime(time_range["end"], "%H:%M").time()
                    
                    Unavailability.objects.update_or_create(
                        screen=screen,
                        start_time=make_aware(
                            datetime.combine(datetime.now().date(), start_time)
                        ),
                        end_time=make_aware(
                            datetime.combine(datetime.now().date(), end_time)
                        )
                    )

            return Response({"message": "Weekly schedule and unavailability configured successfully."}, status=status.HTTP_201_CREATED)

        except Theater.DoesNotExist:
            return Response({"error": "Theater not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CustomUnavailabilityView(APIView):
    """
    API to mark custom unavailability for a specific screen.
    """

    def post(self, request, id):
        try:
            theater = Theater.objects.get(id=id)
            data = request.data
            screen = Screen.objects.get(id=data["screen_id"], theater=theater)

            for slot in data.get("unavailable_slots", []):
                start_time = datetime.strptime(slot['start'], "%H:%M").time()
                end_time = datetime.strptime(slot['end'], "%H:%M").time()
                Unavailability.objects.create(
                    screen=screen,
                    start_time=make_aware(
                        datetime.strptime(f"{slot['date']} {slot['start']}", "%Y-%m-%d %H:%M")
                    ),
                    end_time=make_aware(
                        datetime.strptime(f"{slot['date']} {slot['end']}", "%Y-%m-%d %H:%M")
                    ),
                    reason="Custom unavailability"
                )

            
            for date in data.get("unavailable_dates", []):
                start_of_day = make_aware(datetime.strptime(date, "%Y-%m-%d"))
                end_of_day = start_of_day + timedelta(hours=23, minutes=59, seconds=59)
                Unavailability.objects.create(
                    screen=screen,
                    start_time=start_of_day,
                    end_time=end_of_day,
                    reason="Full-day unavailability"
                )

            return Response({"message": "Custom unavailability added successfully."}, status=status.HTTP_201_CREATED)

        except Theater.DoesNotExist:
            return Response({"error": "Theater not found."}, status=status.HTTP_404_NOT_FOUND)
        except Screen.DoesNotExist:
            return Response({"error": "Screen not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AvailableSlotsView(APIView):
    """
    API to fetch available slots for a given screen within a date range.
    """

    def get(self, request, id):
        try:
         
            theater = Theater.objects.get(id=id)
            
         
            screen_id = request.GET.get("screen_id")
            start_date_str = request.GET.get("start_date")
            end_date_str = request.GET.get("end_date")

           
            if not screen_id or not start_date_str or not end_date_str:
                return Response(
                    {"error": "screen_id, start_date, and end_date are required parameters."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError as e:
                return Response(
                    {"error": "Invalid date format. Please use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )

           
            screen = Screen.objects.get(id=screen_id, theater=theater)

           
            unavailability = Unavailability.objects.filter(
                screen=screen,
                start_time__date__lte=end_date,  # Include any unavailability that might end after the end date
                end_time__date__gte=start_date  # Include any unavailability that might start before the start date
            )
            
           
            print(f"Unavailability for screen {screen_id}:")
            for unavail in unavailability:
                print(f"Unavailability Slot: {unavail.start_time} to {unavail.end_time}")

           
            slots = Slot.objects.filter(
                screen=screen,
                start_time__gte=make_aware(datetime.combine(start_date, datetime.min.time())),
                end_time__lte=make_aware(datetime.combine(end_date, datetime.max.time()))
            )

          
            print(f"Slots for screen {screen_id} from {start_date} to {end_date}:")
            for slot in slots:
                print(f"Slot: {slot.start_time} to {slot.end_time}")

           
            available_slots = []
            for slot in slots:
               
                print(f"Checking slot: {slot.start_time} - {slot.end_time}")
                is_overlapping = False
                for unavailable in unavailability:
                    print(f"Checking against unavailability: {unavailable.start_time} - {unavailable.end_time}")
                    if (slot.start_time < unavailable.end_time and slot.end_time > unavailable.start_time):
                        print("Slot overlaps with unavailability.")
                        is_overlapping = True
                        break
               
                if not is_overlapping:
                    available_slots.append(slot)

          
            print(f"Available slots: {available_slots}")

           
            serializer = SlotSerializer(available_slots, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Theater.DoesNotExist:
            return Response({"error": "Theater not found."}, status=status.HTTP_404_NOT_FOUND)
        except Screen.DoesNotExist:
            return Response({"error": "Screen not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
