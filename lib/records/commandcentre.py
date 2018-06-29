""" This is the command centre for all the commands created in the YA developer console
    This file contains the logic to understand a user message request from YA
    and return a response in the format of a YA message object accordingly

"""

import requests
import json
from yellowant.messageformat import MessageClass, MessageAttachmentsClass, AttachmentFieldsClass
from .models import MailGunUserToken, YellowUserToken

from django.conf import settings


API_BASE_URL = "https://api.mailgun.net/v3/domains"


class CommandCentre(object):

    """ Handles user commands

        Args:
            yellowant_integration_id (int): The integration id of a YA user
            function_name (str): Invoke name of the command the user is calling
            args (dict): Any arguments required for the command to run
    """
    def __init__(self, yellowant_user_id, yellowant_integration_id, function_name, args):
        self.yellowant_user_id = yellowant_user_id
        self.yellowant_integration_id = yellowant_integration_id
        self.function_name = function_name
        self.args = args

    def parse(self):
        """
        Matching which function to call
        """

        self.commands = {
            'get_domains'  : self.get_domains,
            'get_domain' : self.get_domain,
            'get_credentials' : self.get_credentials,
            'get_domain_tracking' : self.get_domain_tracking,
            'get_ips' : self.get_ips,
            'get_stats'  : self.get_stats,
            'get_bounces' : self.get_bounces,
            'get_unsubscribes' : self.get_unsubscribes,
            'get_complaints' : self.get_complaints,
            'api_key'   : self.api_key,
            'send_mail' : self.send_mail
        }

        self.user_integration = YellowUserToken.objects.get\
            (yellowant_integration_id=self.yellowant_integration_id)

        self.mailgun_access_token_object = MailGunUserToken.objects.\
            get(user_integration=self.user_integration)

        self.mailgun_access_token = self.mailgun_access_token_object.\
            accessToken

        self.domain_name = self.mailgun_access_token_object.domain_name

        self.API_URL = "https://api.mailgun.net/v3/" + str(self.domain_name)

        return self.commands[self.function_name](self.args)



    def get_domains(self,args):
        """ Get a list of all domains """

        print("In get_domains")

        # API parameteres for getting account information
        param = {"skip": 0, "limit": 3}
        auth = ("api", self.mailgun_access_token)


        # Consuming the API
        r = requests.get(API_BASE_URL, auth=auth, params=param)

        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            print(json.loads(r.content.decode("utf-8")))
            response = json.loads(r.content.decode("utf-8"))
            items = response["items"]

            # Creating message objects to structure the message to be shown
            message = MessageClass()
            message.message_text = "All domain details :"

            attachment = MessageAttachmentsClass()

            for item in range(0,len(items)):
                field1 = AttachmentFieldsClass()
                field1.title = "Domain :"
                field1.value = response["items"][item]["name"]
                attachment.attach_field(field1)

                field2 = AttachmentFieldsClass()
                field2.title = "State :"
                field2.value = response["items"][item]["state"]
                attachment.attach_field(field2)

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()



    def get_domain(self,args):
        """ Get a single domain """

        # API parameteres for getting account information
        auth = ("api", self.mailgun_access_token)

        # Consuming the API
        r = requests.get("https://api.mailgun.net/v3/domains/" + str(self.domain_name), auth=auth)
        print(self.mailgun_access_token)
        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            print(json.loads(r.content.decode("utf-8")))
            response = json.loads(r.content.decode("utf-8"))


            # Creating message objects to structure the message to be shown
            message = MessageClass()
            message.message_text = "Domain details :"

            attachment = MessageAttachmentsClass()

            field1 = AttachmentFieldsClass()
            field1.title = "Domain :"
            field1.value = response['domain']["name"]
            attachment.attach_field(field1)

            field2 = AttachmentFieldsClass()
            field2.title = "State :"
            field2.value = response['domain']["state"]
            attachment.attach_field(field2)

            field3 = AttachmentFieldsClass()
            field3.title = "Created at :"
            field3.value = response['domain']['created_at']
            attachment.attach_field(field3)

            field4 = AttachmentFieldsClass()
            field4.title = "Type :"
            field4.value = response['domain']['type']
            attachment.attach_field(field4)

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()



    def get_credentials(self,args):
        """ Listing all SMTP credentials """

        # API parameteres for getting account information
        auth = ("api", self.mailgun_access_token)

        # Consuming the API
        r = requests.get("https://api.mailgun.net/v3/domains/" + str(self.domain_name) + "/credentials",
                         auth=auth)

        ## Just for reference
        ## NOT USED here

        sample_response = {
            "total_count": 2,
            "items": [
                    {
                      "size_bytes": 0,
                      "created_at": "Tue, 27 Sep 2011 20:24:22 GMT",
                      "mailbox": "user@samples.mailgun.org",
                      "login": "user@samples.mailgun.org",
                    },
                    {
                      "size_bytes": 0,
                      "created_at": "Thu, 06 Oct 2011 10:22:36 GMT",
                      "mailbox": "user@samples.mailgun.org",
                      "login": "user@samples.mailgun.org",
                    }]
                }


        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            print(json.loads(r.content.decode("utf-8")))
            response = json.loads(r.content.decode("utf-8"))

            # Creating message objects to structure the message to be shown
            message = MessageClass()
            message.message_text = "SMTP Credentials :"
            items = response['items']
            attachment = MessageAttachmentsClass()

            for item in range(0,len(items)):

                field1 = AttachmentFieldsClass()
                field1.title = "Mailbox :"
                field1.value = response["items"][item]["mailbox"]
                attachment.attach_field(field1)

                field2 = AttachmentFieldsClass()
                field2.title = "Created at :"
                field2.value = response["items"][item]["created_at"]
                attachment.attach_field(field2)

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()

    def get_domain_tracking(self,args):

        """ Get tracking settings for a domain """


        # API parameteres for getting account information
        auth = ("api", self.mailgun_access_token)

        # Consuming the API
        r = requests.get("https://api.mailgun.net/v3/domains/" + str(self.domain_name) + "/tracking",
                         auth=auth)
        # print(json.loads(r.content.decode("utf-8")))

        ## Just for reference
        ## NOT USED here

        # NOT USED here
        sample_response = {'tracking': {'click': {'active': False}, 'open': {'active': False}, 'unsubscribe': {
            'html_footer': '\n<br>\n<p><a href="%unsubscribe_url%">unsubscribe</a></p>\n', 'active': False,
            'text_footer': '\n\nTo unsubscribe click: <%unsubscribe_url%>\n\n'}}}

        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            print(json.loads(r.content.decode("utf-8")))
            response = json.loads(r.content.decode("utf-8"))

            # Creating message objects to structure the message to be shown
            message = MessageClass()
            message.message_text = "SMTP Credentials :"
            attachment = MessageAttachmentsClass()


            field1 = AttachmentFieldsClass()
            field1.title = "Click :"
            field1.value = response['tracking']['click']['active']
            attachment.attach_field(field1)

            field2 = AttachmentFieldsClass()
            field2.title = "Unsubscribe :"
            field2.value = response['tracking']['unsubscribe']['active']
            attachment.attach_field(field2)

            field3 = AttachmentFieldsClass()
            field3.title = "Open :"
            field3.value = response['tracking']['open']['active']
            attachment.attach_field(field3)



            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()



    def get_ips(self,args):

        """ Get a list of all IPs """


        # API parameteres for getting account information
        auth = ("api", self.mailgun_access_token)

        # Consuming the API
        r = requests.get("https://api.mailgun.net/v3/ips",params={"dedicated": "true"},auth=auth)

        # NOT USED here
        sample_response = {
          "items": ["192.161.0.1", "192.168.0.2"],
          "total_count": 2
        }

        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            print(json.loads(r.content.decode("utf-8")))
            response = json.loads(r.content.decode("utf-8"))

            # Creating message objects to structure the message to be shown
            message = MessageClass()
            message.message_text = "List of IPs :"
            attachment = MessageAttachmentsClass()

            for i in range(0,len(response['items'])):
                field1 = AttachmentFieldsClass()
                field1.title = "Click :"
                field1.value = response['items'][i]
                attachment.attach_field(field1)

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()


    def get_stats(self,args):
        """ Get stats for ‘accepted’, ‘delivered’, and ‘failed’ events for the past month: """
        print("In get_stats")

        # API parameters for getting account information
        auth = ("api", self.mailgun_access_token)

        # Consuming the API
        r = requests.get(
            "https://api.mailgun.net/v3/" + self.domain_name + "/stats/total",
            auth=("api", self.mailgun_access_token),
            params={"event": ["accepted", "delivered", "failed"],
                    "duration": "1m"})

        # NOT USED here
        sample_response = {
              "end": "Fri, 01 Apr 2012 00:00:00 UTC",
              "resolution": "month",
              "start": "Tue, 14 Feb 2012 00:00:00 UTC",
              "stats": [
                {
                  "time": "Tue, 14 Feb 2012 00:00:00 UTC",
                  "accepted": {
                    "outgoing": 10,
                    "incoming": 5,
                    "total": 15
                  },
                  "delivered": {
                      "smtp": 15,
                      "http": 5,
                      "total": 20
                  },
                  "failed": {
                    "permanent": {
                      "bounce": 4,
                      "delayed-bounce": 1,
                      "suppress-bounce": 1,
                      "suppress-unsubscribe": 2,
                      "suppress-complaint": 3,
                      "total": 10
                    },
                    "temporary": {
                      "espblock": 1
                    }
                  },
                }
              ]
            }

        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            print(json.loads(r.text))
            response = json.loads(r.text)

            # Creating message objects to structure the message to be shown
            message = MessageClass()
            message.message_text = " Your statistics :"

            attachment = MessageAttachmentsClass()

            for i in range(0, len(response["stats"])):
                field1 = AttachmentFieldsClass()
                field1.title = "Time :"
                field1.value = response["stats"][i]["time"]
                attachment.attach_field(field1)

                field2 = AttachmentFieldsClass()
                field2.title = "Total accepted :"
                field2.value = response["stats"][i]["accepted"]["total"]
                attachment.attach_field(field2)

                field3 = AttachmentFieldsClass()
                field3.title = "Total delivered :"
                field3.value = response["stats"][i]["delivered"]["total"]
                attachment.attach_field(field3)

                field4 = AttachmentFieldsClass()
                field4.title = "Total failed :"
                field4.value = response["stats"][i]["failed"]['permanent']["total"]
                attachment.attach_field(field4)

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()



    def get_bounces(self,args):
        """ View all bounces """

        # API parameteres for getting account information
        auth = ("api", self.mailgun_access_token)

        # Consuming the API
        r = requests.get("https://api.mailgun.net/v3/" + self.domain_name + "/bounces", auth=auth)

        # NOT USED here

        sample_response = {
                "items":
                    [
                        {
                            "address": "alice@example.com",
                            "code": "550",
                            "error": "No such mailbox",
                            "created_at": "Fri, 21 Oct 2011 11:02:55 GMT"
                        }
                    ]
                }


        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            print(print(json.loads(r.text)))
            response = json.loads(r.text)

            # Creating message objects to structure the message to be shown


            if(len(response['items']) == 0):
                message = MessageClass()
                message.message_text = "You don't have any bounces as of now !"
                return message.to_json()


            message = MessageClass()
            message.message_text = "List bounces :"
            attachment = MessageAttachmentsClass()

            for i in range(0, len(response['items'])):
                field1 = AttachmentFieldsClass()
                field1.title = "Address :"
                field1.value = response['items'][i]["address"]
                attachment.attach_field(field1)

                field2 = AttachmentFieldsClass()
                field2.title = "Created at :"
                field2.value = response['items'][i]["created_at"]
                attachment.attach_field(field2)

                field3 = AttachmentFieldsClass()
                field3.title = "Error :"
                field3.value = response['items'][i]["error"]
                attachment.attach_field(field3)

                field4 = AttachmentFieldsClass()
                field4.title = "Code :"
                field4.value = response['items'][i]["code"]
                attachment.attach_field(field4)

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()




    def get_unsubscribes(self,args):

        print("In get_unsubscribes")
        # API parameteres for getting account information
        auth = ("api", self.mailgun_access_token)

        # Consuming the API
        r = requests.get("https://api.mailgun.net/v3/" + self.domain_name + "/unsubscribes",auth=auth)

        # NOT USED here
        sample_response = {
                      "items":
                        [
                          {
                            "address": "alice@example.com",
                            "tag": "*",
                            "created_at": "Fri, 21 Oct 2011 11:02:55 GMT"
                          }
                        ]
                    }


        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            print(print(json.loads(r.text)))
            response = json.loads(r.text)

            # Creating message objects to structure the message to be shown
            if(len(response['items']) == 0):
                message = MessageClass()
                message.message_text = "You don't have any unsubscribes as of now !"
                return message.to_json()


            message = MessageClass()
            message.message_text = "Unsubscribers details :"
            attachment = MessageAttachmentsClass()

            for i in range(0, len(response['items'])):
                field1 = AttachmentFieldsClass()
                field1.title = "Address :"
                field1.value = response['items'][i]["address"]
                attachment.attach_field(field1)

                field2 = AttachmentFieldsClass()
                field2.title = "Created at :"
                field2.value = response['items'][i]["created_at"]
                attachment.attach_field(field2)

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()



    def get_complaints(self,args):

        print("In get_complaints")

        # API parameteres for getting account information
        auth = ("api", self.mailgun_access_token)

        # Consuming the API
        r = requests.get(
            "https://api.mailgun.net/v3/" + self.domain_name +"/complaints",
            auth=("api", self.mailgun_access_token))


        # NOT USED here
        sample_response = {
            "items":
                [
                    {
                        "address": "alice@example.com",
                        "created_at": "Fri, 21 Oct 2011 11:02:55 GMT"
                    }
                ]
        }

        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            print(print(json.loads(r.text)))
            response = json.loads(r.text)

            # Creating message objects to structure the message to be shown
            if (len(response['items']) == 0):
                message = MessageClass()
                message.message_text = "You don't have any complaints as of now !"
                return message.to_json()

            message = MessageClass()
            message.message_text = "Complaint details :"
            attachment = MessageAttachmentsClass()

            for i in range(0, len(response['items'])):
                field1 = AttachmentFieldsClass()
                field1.title = "Address :"
                field1.value = response['items'][i]["address"]
                attachment.attach_field(field1)

                field2 = AttachmentFieldsClass()
                field2.title = "Created at :"
                field2.value = response['items'][i]["created_at"]
                attachment.attach_field(field2)

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = r.content.decode("utf-8")
            m.message_text = "{0}: {1}".format(r.status_code, r.text)
            return m.to_json()


    def api_key(self,args):
        """
        api_key function updates the user's api key in case it is regenerated by user
        """

        print("In api key")
        api = args['api']

        # Fetching object from database and updating the api_key and flag
        api_new = MailGunUserToken.objects.get \
            (user_integration_id=self.user_integration)

        api_new.accessToken = api
        api_new.apikey_login_update_flag = True
        api_new.save()
        # print(api_new.accessToken)

        m = MessageClass()
        m.message_text = "Your api key is updated !"
        return m.to_json()

    def send_mail(self,args):

        print("In send_mail")

        # Arguments from slack
        to = args['to']
        text = args['text']
        subject = args['subject']

        # API parameteres for getting account information
        auth = ("api", self.mailgun_access_token)

        # sample payload
        data = {"from": "mailgun" + "@" + self.domain_name,
                  "to": [to, "mailgun" + "@" + self.domain_name],
                  "subject": subject,
                  "text": text}

        # Consuming the API
        r = requests.post(
            "https://api.mailgun.net/v3/"+ self.domain_name +"/messages",
            auth=auth,
            data=data)

        # NOT USED here
        sample_response = {
                  "message": "Queued. Thank you.",
                  "id": "<20111114174239.25659.5817@samples.mailgun.org>"
                }

        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            print(print(json.loads(r.text)))
            response = json.loads(r.text)

            # Creating message objects to structure the message to be shown

            message = MessageClass()
            message.message_text = response["message"]
            return message.to_json()


        else:
            m = MessageClass()
            print(r.content.decode("utf-8"))
            d = json.loads(r.content.decode("utf-8"))
            m.message_text = d['message']
            return m.to_json()


