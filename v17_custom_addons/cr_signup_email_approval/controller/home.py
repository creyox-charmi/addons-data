# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
import time
from datetime import datetime, timedelta

import psycopg2
import random
import odoo
from odoo.addons.web.controllers.home import Home
import odoo.modules.registry
from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request , Response
from odoo.service import security
from odoo.tools import ustr
from odoo.tools.translate import _
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url, is_user_internal


_logger = logging.getLogger(__name__)

# Shared parameters for all login/signup flows
SIGN_UP_REQUEST_PARAMS = {'db', 'login', 'debug', 'token', 'message', 'error', 'scope', 'mode',
                          'redirect', 'redirect_hostname', 'email', 'name', 'partner_id',
                          'password', 'confirm_password', 'city', 'country_id', 'lang', 'signup_email'}
LOGIN_SUCCESSFUL_PARAMS = set()


class SubHome(Home):

    def _login_redirect(self, uid, redirect=None):
        print("childddddddd")
        request_path = request.httprequest.path
        print(f"request_path - {request_path}")
        if '/web/login' in request_path:
            # Logic for /web/login
            print("Redirecting from /web/login page")
        elif '/web/signup' in request_path:
            # Logic for /web/signup
            self.verify_code()
        else:
            # Default logic
            print("Redirecting from another page")

        response = super(SubHome, self)._login_redirect(uid, redirect=None)
        return response


    def verify_code(self):
        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        print(f"values {values}")
        try:
            print("in try")
            values['databases'] = http.db_list()
            print(f"values['databases'] - {values['databases']}")
        except odoo.exceptions.AccessDenied:
            print("in catch")
            values['databases'] = None
            print(f"values['databases'] - {values['databases']}")

        if request.httprequest.method == 'POST':
            try:
                print("in try-------------------")
                uid = request.session.authenticate(request.db, request.params['login'], request.params['password'])
                print(f"uid - {uid}")

                self.send_mail(uid)
                return self.verification_page()
            except odoo.exceptions.AccessDenied as e:
                values['error'] = e.args[0]

    @http.route(['/web/verify_code'], type='http', auth='public', website='True')
    def verification_page(self, **post):
        print("verification_page is call")
        print(f'request.render("cr_signup_email_approval.verification_code") - {request.render("cr_signup_email_approval.verification_code")}')
        return request.render("cr_signup_email_approval.verification_code")




    # @http.route('/web/login', type='http', auth="none")
    # def web_login(self, redirect=None, **kw):
    #     print("for login-----------------------------")
    #     ensure_db()
    #
    #     print("11")
    #
    #
    #     values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
    #     print(f"values {values}")
    #     try:
    #         print("in try")
    #         values['databases'] = http.db_list()
    #         print(f"values['databases'] - {values['databases']}")
    #     except odoo.exceptions.AccessDenied:
    #         print("in catch")
    #         values['databases'] = None
    #         print(f"values['databases'] - {values['databases']}")
    #
    #     if request.httprequest.method == 'POST':
    #         try:
    #             print("in try-------------------")
    #             uid = request.session.authenticate(request.db, request.params['login'], request.params['password'])
    #             print(f"uid - {uid}")
    #
    #             self.send_mail(uid)
    #             print(
    #                 f'request.render("cr_signup_email_approval.verification_code") - {request.render("cr_signup_email_approval.verification_code")}')
    #             return request.render("cr_signup_email_approval.verification_code")
    #         except odoo.exceptions.AccessDenied as e:
    #             values['error'] = e.args[0]
    #     else:
    #         print("22")
    #         response = super(SubHome, self).web_login(redirect=None, **kw)
    #         return response





    def generate_random_number(self):
        num = list(range(1000, 10001))  # range is exclusive, so we use 10001 to include 10000

        # Pick a random number from this range
        code = random.choice(num)

        print(f"in method code - {code}")
        return code


    def send_mail(self, supervisor_emails):
        try:
            print("call")
            code = self.generate_random_number()
            print(f"code - {code}")
            request.session['verification_code'] = code
            request.session['supervisor_emails'] = supervisor_emails
            request.session['verification_time'] = time.time()  # Store the current time when OTP is generated
            print(f"Verification code stored in session: {request.session['verification_code']}")

            subject = "Your Company Verification Email"

            # Corrected: Use an f-string for body_html to properly interpolate the code variable
            body_html = f"<p>Hello Supervisor,</p><p>Your verification code is {code}</p>"

            print(f"subject - {subject}")
            print(f"body_html - {body_html}")
            admin_email = request.env['res.company'].sudo().search([('id', '=', 1)]).email
            print(f"admin_email - {admin_email}")
            User = request.env['res.users'].sudo().search(
                [
                    ('id', '=', supervisor_emails)
                ]
            )
            user_email = User.email
            # Create and send the mail
            mail = request.env["mail.mail"].sudo().create(
                {
                    "subject": subject,
                    "body_html": body_html,
                    "email_to": user_email,
                    "email_from": admin_email
                }
            )
            print(f"mail - {mail}")

            # Send the email
            mail.send()

        except Exception as e:
            # Catch any exceptions and log them
            _logger.error(f"Error sending verification email: {str(e)}")
            print(f"Error sending email: {str(e)}")

        return request.render("cr_signup_email_approval.verification_code")


    @http.route(['/user/form/submit'], csrf=False, type='http', auth='public', website=True)
    def user_form_submit(self, redirect=None, **post):
        print("enter")
        verify_code = post.get('code')
        print(f"verify_code - {verify_code}")

        session_code = request.session.get('verification_code')
        print(f"session_code - {session_code}")

        session_time = request.session.get('verification_time')  # Retrieve the OTP generation time
        print(f"session_time - {session_time}")

        uid = request.session.get('supervisor_emails')
        print(f"uid - {uid}")

        if session_code and session_time:
            current_time = time.time()  # Get the current time
            time_diff = current_time - session_time  # Calculate the time difference

            # Check if the OTP has expired (more than 60 seconds)
            if time_diff > 60:
                error_message = "The verification code has expired. Please request a new one."
                return request.render("cr_signup_email_approval.verification_code",
                                      {"error_message": error_message, "expired": True})

            if str(verify_code) == str(session_code):
                print("yessssssssssssssssssssssssssssssssssssssssssssssssssssss")
                uid = request.session.get('supervisor_emails')
                return _get_login_redirect_url(uid, redirect)

        return request.redirect('/user/invalid_code')


    @http.route(['/user/invalid_code'], csrf=False, type='http', auth='public', website=True)
    def invalid_code(self, **post):
        session_time = request.session.get('verification_time')  # This is in milliseconds
        print(f"session_time (milliseconds) - {session_time}")

        # Ensure session_time is present and valid
        if not session_time:
            error_message = "Session expired or invalid OTP. Please try again."
            return request.render("cr_signup_email_approval.verification_code", {"error_message": error_message})

        current_time = time.time()
        print(f"current_time (milliseconds) - {current_time}")

        # Calculate the time difference (time passed since OTP was sent)
        time_diff = current_time - session_time
        print(f"time_diff (milliseconds) - {time_diff}")

        # OTP expiration time is 60000 milliseconds (60 seconds)
        otp_expiration_time = 60000  # 60 seconds in milliseconds

        # Calculate the remaining time
        remaining_time = otp_expiration_time - time_diff
        print(f"remaining_time (milliseconds) - {remaining_time}")


        remaining_time_seconds = remaining_time / 1000
        print(f"remaining_time (seconds) - {remaining_time_seconds}")

        error_message = "Incorrect Code, try again.."

        # Render the template with error message and remaining time
        return request.render("cr_signup_email_approval.verification_code",
                              {"error_message": error_message, "remaining_time": int(remaining_time_seconds)})

    @http.route('/web/regenerate_otp', type='http', auth='public', website=True)
    def regenerate_otp_page(self, **kw):
        print("enter in regenrate otp")
        """
        Handle OTP regeneration when user clicks the "Regenerate OTP" button.
        """
        # Get the supervisor email from the session and send a new OTP
        supervisor_emails = request.session.get('supervisor_emails')
        print(f"supervisor_emails - {supervisor_emails}")
        if supervisor_emails:
            print('if supervisor_emails: -->true')
            print("before send mail")
            self.send_mail(supervisor_emails)  # Send the email with new OTP
            print("after send mail")
            success_message = "A new OTP has been sent to your email."
            print(f"success_message - {success_message}")
            return request.render("cr_signup_email_approval.verification_code", {"success_message": success_message})

        return request.render("cr_signup_email_approval.verification_code",
                              {"error_message": "Failed to regenerate OTP."})