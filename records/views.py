""" This file contains all functions corresponding to their urls"""
import urllib

from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from yellowant import YellowAnt
import json
import uuid
from yellowant.messageformat import MessageClass, \
    MessageAttachmentsClass, MessageButtonsClass, AttachmentFieldsClass
import traceback
from django.views.decorators.csrf import csrf_exempt
from .models import YellowUserToken, YellowAntRedirectState, \
     MailGunUserToken
from .commandcentre import CommandCentre
from django.contrib.auth.models import User
import hashlib, hmac


def redirectToYellowAntAuthenticationPage(request):

    '''Initiate the creation of a new user integration on YA
       YA uses oauth2 as its authorization framework.
       This method requests for an oauth2 code from YA to start creating a
       new user integration for this application on YA.
    '''

    # Generate a unique ID to identify the user when YA returns an oauth2 code
    user = User.objects.get(id=request.user.id)
    state = str(uuid.uuid4())

    # Save the relation between user and state so that we can identify the user
    # when YA returns the oauth2 code
    YellowAntRedirectState.objects.create(user=user.id, state=state)

    # Redirect the application user to the YA authentication page.
    # Note that we are passing state, this app's client id,
    # oauth response type as code, and the url to return the oauth2 code at.
    return HttpResponseRedirect("{}?state={}&client_id={}&response_type=code&redirect_url={}".format
                                (settings.YELLOWANT_OAUTH_URL, state, settings.YELLOWANT_CLIENT_ID,
                                 settings.YELLOWANT_REDIRECT_URL))


def yellowantRedirecturl(request):

    ''' Receive the oauth2 code from YA to generate a new user integration
        This method calls utilizes the YA Python SDK to create a new user integration on YA.
        This method only provides the code for creating a new user integration on YA.
        Beyond that, you might need to authenticate the user on
        the actual application (whose APIs this application will be calling) and store a relation
        between these user auth details and the YA user integration.
    '''

    # Oauth2 code from YA, passed as GET params in the url
    code = request.GET.get('code')

    # The unique string to identify the user for which we will create an integration
    state = request.GET.get("state")

    # Fetch user with help of state from database
    yellowant_redirect_state = YellowAntRedirectState.objects.get(state=state)
    user = yellowant_redirect_state.user

    # Initialize the YA SDK client with your application credentials
    y = YellowAnt(app_key=settings.YELLOWANT_CLIENT_ID,
                  app_secret=settings.YELLOWANT_CLIENT_SECRET,
                  access_token=None, redirect_uri=settings.YELLOWANT_REDIRECT_URL)
    print(settings.YELLOWANT_REDIRECT_URL)
    # Getting the acccess token
    access_token_dict = y.get_access_token(code)
    access_token = access_token_dict['access_token']

    # Getting YA user details
    yellowant_user = YellowAnt(access_token=access_token)
    profile = yellowant_user.get_user_profile()

    # Creating a new user integration for the application
    user_integration = yellowant_user.create_user_integration()
    hash_str = str(uuid.uuid4()).replace("-", "")[:25]
    ut = YellowUserToken.objects.create(user=user, yellowant_token=access_token,
                                        yellowant_id=profile['id'],
                                        yellowant_integration_invoke_name=user_integration\
                                            ["user_invoke_name"],
                                        yellowant_integration_id=user_integration\
                                            ['user_application'],
                                        webhook_id=hash_str)

    ## Initially the mailgun object contians no access token so kept empty
    ## On submiting API key it is updated

    mail_gun_token = ""
    mail_object = MailGunUserToken.objects.create(user_integration=ut, accessToken=mail_gun_token, webhook_id=hash_str)

    url = settings.BASE_URL + "/webhook/" + ut.webhook_id + "/"
    print(url)

    return HttpResponseRedirect("/")


@csrf_exempt
def webhook(request,hash_str=""):

    print("In webhook")

    api_key = (MailGunUserToken.objects.get(webhook_id=hash_str).accessToken)
    urllib.parse.unquote(request.body.decode("utf-8"))
    params_dict = urllib.parse.parse_qsl(request.body)
    params = dict(params_dict)

    if b'token' not in params:

        if(params[b'token'].decode("utf-8") == 'unsubscribed'):
            webhook_unsubscribed(request,hash_str)
        else :
            webhook_delivered(request,hash_str)
    else:
        token = params[b'token'].decode('utf-8')
        timestamp = params[b'timestamp'].decode('utf-8')
        signature = params[b'signature'].decode('utf-8')

        hmac_digest = hmac.new(key=api_key.encode('utf-8'),
                               msg='{}{}'.format(timestamp, token).encode('utf-8'),
                               digestmod=hashlib.sha256).hexdigest()

        val = hmac.compare_digest(signature, hmac_digest)

        check = str(params[b'event'].decode("utf-8"))

        if (check == 'unsubscribed'):
            webhook_unsubscribed(request, hash_str)
        else:
            webhook_delivered(request, hash_str)

    return HttpResponse("OK",status=200)


def webhook_unsubscribed(request,webhook_id):
    print("In webhook_unsubscribed")
    """
    Webhook function to notify user about update in unsbscribes
    """

    urllib.parse.unquote(request.body.decode("utf-8"))
    params_dict = urllib.parse.parse_qsl(request.body)
    params = dict(params_dict)

    ## Extracting necessary data

    device_type = params[b'device-type'].decode("utf-8")
    name = params[b'client-name'].decode("utf-8")
    domain = params[b'domain'].decode("utf-8")
    city = params[b'city'].decode('utf-8')
    country = params[b'country'].decode('utf-8')
    recipient = params[b'recipient'].decode('utf-8')

    try:

        # Fetching yellowant object
        yellow_obj = YellowUserToken.objects.get(webhook_id=webhook_id)
        print(yellow_obj)
        access_token = yellow_obj.yellowant_token
        print(access_token)
        integration_id = yellow_obj.yellowant_integration_id
        service_application = str(integration_id)
        print(service_application)

        # Creating message object for webhook message

        webhook_message = MessageClass()
        webhook_message.message_text = "Unsubscribe details"

        attachment_message = MessageAttachmentsClass()


        field2 = AttachmentFieldsClass()
        field2.title = "Email Id :"
        field2.value = recipient
        attachment_message.attach_field(field2)

        field1 = AttachmentFieldsClass()
        field1.title = "Browser :"
        field1.value = name
        attachment_message.attach_field(field1)

        field3 = AttachmentFieldsClass()
        field3.title = "Domain"
        field3.value = domain
        attachment_message.attach_field(field3)

        field4 = AttachmentFieldsClass()
        field4.title = "Device type"
        field4.value = device_type
        attachment_message.attach_field(field4)

        field5 = AttachmentFieldsClass()
        field5.title = "City"
        field5.value = city
        attachment_message.attach_field(field5)

        field6 = AttachmentFieldsClass()
        field6.title = "Country"
        field6.value = country
        attachment_message.attach_field(field6)

        webhook_message.attach(attachment_message)


        attachment = MessageAttachmentsClass()
        attachment.title = "Unsubscribe operations"

        button_get_incidents = MessageButtonsClass()
        button_get_incidents.name = "1"
        button_get_incidents.value = "1"
        button_get_incidents.text = "Get unsubscribe details"
        button_get_incidents.command = {
            "service_application": service_application,
            "function_name": 'get_unsubscribes',
            "data": {}
            }

        attachment.attach_button(button_get_incidents)
        webhook_message.data = {
                "recipient_email_id" : recipient,
                "domain" : domain,
                "device_type" : device_type,
                "city" : city,
                "country" : country,
                "name": name,
                     }
        webhook_message.attach(attachment)
        #print(integration_id)

        # Creating yellowant object
        yellowant_user_integration_object = YellowAnt(access_token=access_token)

        # Sending webhook message to user
        send_message = yellowant_user_integration_object.create_webhook_message(
        requester_application=integration_id,
        webhook_name="notify_unsubscribe", **webhook_message.get_dict())
        return HttpResponse("OK", status=200)

    except YellowUserToken.DoesNotExist:
        return HttpResponse("Not Authorized", status=403)


def webhook_delivered(request,webhook_id):

    print("In webhook_delivered")

    """
    Webhook function to notify user about update in component
    """

    urllib.parse.unquote(request.body.decode("utf-8"))
    params_dict = urllib.parse.parse_qsl(request.body)
    params = dict(params_dict)


    #Extracting necessary data
    recipient = params[b'recipient'].decode('utf-8')


        # Fetching yellowant object
    try:
        yellow_obj = YellowUserToken.objects.get(webhook_id=webhook_id)
        print(yellow_obj)
        access_token = yellow_obj.yellowant_token
        print(access_token)
        integration_id = yellow_obj.yellowant_integration_id
        service_application = str(integration_id)
        print(service_application)


        # Creating message object for webhook message
        webhook_message = MessageClass()
        webhook_message.message_text = "Mail delivered to " + str(recipient)

        attachment = MessageAttachmentsClass()
        attachment.title = "Mail Stats upto last 1 month"

        button_get_components = MessageButtonsClass()
        button_get_components.name = "1"
        button_get_components.value = "1"
        button_get_components.text = "Get all stats"
        button_get_components.command = {
            "service_application": service_application,
            "function_name": 'get_stats',
            "data": {}
            }

        attachment.attach_button(button_get_components)
        webhook_message.data = {"recipient_email_id" : recipient}
        webhook_message.attach(attachment)
        #print(integration_id)

        # Creating yellowant object
        yellowant_user_integration_object = YellowAnt(access_token=access_token)

        # Sending webhook message to user
        send_message = yellowant_user_integration_object.create_webhook_message(
        requester_application=integration_id,
        webhook_name="notify_delivered", **webhook_message.get_dict())

        return HttpResponse("OK", status=200)

    except YellowUserToken.DoesNotExist:
        return HttpResponse("Not Authorized", status=403)

@csrf_exempt
def yellowantapi(request):
    try:
        """
        Recieve user commands from YA
        """
        # Extracting the necessary data
        print("In yellowant api")
        data = json.loads(request.POST['data'])
        args = data["args"]
        service_application = data["application"]
        verification_token = data['verification_token']
        function_name = data['function_name']
        # print(data)

        # Verifying whether the request is actually from YA using verification token
        if verification_token == settings.YELLOWANT_VERIFICATION_TOKEN:
            print("--------")
            print(data)
            print("--------")


        # Processing command in some class Command and sending a Message Object
            message = CommandCentre(data["user"], service_application, function_name, args).parse()

        # Returning message response
            return HttpResponse(message)
        else:
            # Handling incorrect verification token
            error_message = {"message_text": "Incorrect Verification token"}
            return HttpResponse(json.dumps(error_message), content_type="application/json")

    except Exception as e:
        # Handling exception
        print(str(e))
        traceback.print_exc()
        return HttpResponse("Something went wrong !")

