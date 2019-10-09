from django.contrib import admin
from .models import Listing, Transaction, Review



def buyer_link(obj):
    buyer_id = str(obj.buyer_id)
    if buyer_id != 'None':
        return "<a href='/admin/events/member/" + buyer_id + "/' >"+obj.buyer.name+"</a>"
    else:
        return "N/A"

buyer_link.short_description = 'Buyer'



def ticket_link(obj):
    ticket_id = str(obj.ticket_id)
    if ticket_id != 'None':
        return "<a href='/admin/events/ticket/" + ticket_id + "/' >"+obj.ticket.title+"</a>"
    else:
        return "N/A"

def event_link(obj):
    event_id = str(obj.event_id)
    if event_id != 'None':
        return "<a href='/admin/events/event/" + event_id + "/' >"+obj.event.name+"</a>"
    else:
        return "N/A"

event_link.short_description = 'Event'
event_link.allow_tags = True


ticket_link.short_description = 'Listing'
ticket_link.allow_tags = True


class TicketAdmin(admin.ModelAdmin):
    list_display = ["title", "ticket_total", "ticket_sold", "ticket_committed", "price", event_link, "create_date"]


class TransactionAdmin(admin.ModelAdmin):
    list_display = ["status", buyer_link, ticket_link, "quantity", "create_date"]


admin.site.register(Listing, TicketAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Review)