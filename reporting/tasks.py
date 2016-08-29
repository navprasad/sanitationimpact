from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from administration.views import send_sms
from reporting.models import Ticket
from django.utils import timezone
import datetime
logger = get_task_logger(__name__)


@periodic_task(
    run_every=(crontab(hour=10, minute=00)),
    name="Ticket_escalation",
    ignore_result=True
)
def Ticket_escalation():
    tickets = Ticket.objects.all()
    for ticket in tickets:
    	diff_time = timezone.localtime(timezone.now())-ticket.timestamp
    	if diff_time.days >= 3 and ticket.status == 0:
		message = 'Dear Provider the problem with ticket id:'+ticket.id+" has been escalated. Please contact your manager to resolve the issue."
    		send_sms(phone_number=ticket.provider.user_profile.phone_number,message=message)
		message = 'Dear Manager the problem with ticket id:'+ticket.id+" has been escalated. Please contact your provider:"+ticket.provider.user_profile.user.first_name+" "+ticket.provider.user_profile.user.last_name+" to resolve the issue."
		send_sms(phone_number=ticket.provider.manager.user_profile.phone_number,message=message)
    		ticket.status=3
    		ticket.save()

    
