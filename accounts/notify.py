from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.template import Context
from listings.models import Transaction
import config
from urllib import parse


class EmailManager:
    COMMIT_NOTIFICATION = 'Committed'
    COMPLETE_NOTIFICATION = 'Completed'

    def notify_transactees(self, notif_type, trans_id):
        if notif_type == self.COMMIT_NOTIFICATION:
            transaction_obj = Transaction.objects.get(pk=trans_id)
            listing_owner_obj = transaction_obj.ticket.seller
            trans_creator_obj = transaction_obj.buyer
            listing_name = transaction_obj.ticket.title
            self.send_commit_email(listing_owner_obj, trans_creator_obj, listing_name)
            self.send_commit_email(trans_creator_obj, listing_owner_obj, listing_name)
            return True

        elif notif_type == self.COMPLETE_NOTIFICATION:
            transaction_obj = Transaction.objects.get(pk=trans_id)
            listing_owner_obj = transaction_obj.ticket.seller
            trans_creator_obj = transaction_obj.buyer
            listing_name = transaction_obj.ticket.title
            self.send_commit_email(listing_owner_obj, trans_creator_obj, listing_name)
            self.send_commit_email(trans_creator_obj, listing_owner_obj, listing_name)
            return True
        else: 
            #Nothing was done
            return False

    def send_commit_email(self, user, contact_obj, listing_name):
        subject = 'Listing Sloth: This ticket exchange is ready to happen!'
        plaintext = get_template("email/commit.txt")
        htmly = get_template("email/commit.html")
        d = Context({ 
            'recipient': user.username,
            'member_name': contact_obj.username,
            'contact_email':contact_obj.email,
            'contact_phone':contact_obj.phone,
            'listing_name':listing_name
            })
        to = [user.email]
        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        from_email = config.DEFAULT_FROM_EMAIL
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def send_commit_email(self, user, contact_obj, listing_name):
        subject = 'Listing Sloth: Please review your contact.'
        review_link = parse.urljoin(config.SITE_URL, reverse("review_view", args=[contact_obj.id]))
        plaintext = get_template("email/complete.txt")
        htmly = get_template("email/complete.html")
        d = Context({ 
            'recipient': user.username,
            'member_name': contact_obj.username,
            'listing_name':listing_name,
            'review_link':review_link
            })
        to = [user.email]
        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        from_email = config.DEFAULT_FROM_EMAIL
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

