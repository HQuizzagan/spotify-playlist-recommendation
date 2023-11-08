# FUNCTION: To send the Spotify Access Token to the user's email address during REQUEST NEW TOKEN events. It uses SendGrid services.
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

def emailSpotifyAccessToken():
    # Create the HTML content of the email
    html_content = f"""
        <h1>Spotify Access Token</h1>
        <p>Here is your new Spotify Access Token:</p>
        <p><strong>{os.getenv('SPOTIFY_ACCESS_TOKEN')}</strong></p>
        <p>Copy the token and paste it in the text box in the app then revalidate it.!</p>
        <p>Thank you!</p>
    """

    message = Mail(
        from_email='hquizzagan.dev@gmail.com',
        # Multiple email addresses can be added to the "to_emails" list
        to_emails=[
            '4578qharlee10@gmail.com',
            'hquizzagan39@gmail.com'
        ],
        subject='Spotify Authenticated Access Token',
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        
        return {
            'success': True,
            'message': f"Email sent to {response.body['personalizations'][0]['to'][0]['email']}"
        }
    except Exception as e:
        return {
            'error': e
        }