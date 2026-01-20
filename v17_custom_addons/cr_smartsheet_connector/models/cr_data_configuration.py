from odoo import models, fields, api,_
import requests
import base64
from odoo.exceptions import UserError

class SmartsheetConfig(models.Model):
    _name = 'cr.data.config'
    _description = 'Data Configuration'

    def import_contacts(self,id):
        config=self.env['cr.smartsheet.config'].sudo().search([('id','=',id)])
        access_token=config.cr_access_token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        url = "https://api.smartsheet.eu/2.0/contacts" if config.cr_europe_region else "https://api.smartsheet.com/2.0/contacts"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Error fetching contacts: {response.text}")

        contacts_data = response.json().get("data", [])
        if config.cr_import_image :

            contact_ids = [contact.get("id") for contact in contacts_data]
            for contact_id in contact_ids:
                contact_url = f"{url}/{contact_id}?include=profileImage"
                contact_response = requests.get(contact_url, headers=headers)

                if contact_response.status_code != 200:
                    continue

                contact_details = contact_response.json()
                smartsheet_id = contact_details.get("id")
                name = contact_details.get("name")
                email = contact_details.get("email")
                profile_image_url = contact_details.get("profileImage", {}).get("imageId")

                if not name:
                    name = email


                partner = self.env['res.partner'].sudo().search([
                    ('cr_smart_sheet_id', '=', smartsheet_id)
                ], limit=1)

                if partner:
                    partner.write({
                        'name': name or partner.name,
                        'email': email,
                        'cr_smart_sheet_id': smartsheet_id,
                        'image_1920': self._fetch_image(profile_image_url[2:]) if profile_image_url else False,
                    })
                else:
                    self.env['res.partner'].sudo().create({
                        'name': name,
                        'email': email,
                        'cr_smart_sheet_id': smartsheet_id,
                        'image_1920': self._fetch_image(profile_image_url[2:]) if profile_image_url else False,
                    })
        else:
            for contact in contacts_data:
                smartsheet_id = contact.get("id")
                name = contact.get("name")
                email = contact.get("email")
                if name:
                    name = name
                else:
                    name = email

                partner = self.env['res.partner'].sudo().search([
                    ('cr_smart_sheet_id', '=', smartsheet_id)
                ], limit=1)
                if partner:
                    partner.write({
                        'name': name or partner.name,
                        'email': email,
                        'cr_smart_sheet_id': smartsheet_id,
                    })
                else:
                    self.env['res.partner'].sudo().create({
                        'name': name,
                        'email': email,
                        'cr_smart_sheet_id': smartsheet_id,
                    })
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Successful"),
                "message": _(
                    "Contacts have been imported successfully."
                ),
                "type": "success",
                "sticky": False,
            },
        }


    def _fetch_image(self, image_url):
        """
        Fetch an image from a URL and return it as a base64-encoded string.
        """
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                content = base64.b64encode(response.content)
                return content
            else:
                return False
        except Exception as e:
            return False

    def import_user(self,id):
        config=self.env['cr.smartsheet.config'].sudo().search([('id','=',id)])
        access_token=config.cr_access_token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        base_url = "https://api.smartsheet.eu/2.0" if config.cr_europe_region else "https://api.smartsheet.com/2.0"
        url = "https://api.smartsheet.eu/2.0/users" if config.cr_europe_region else "https://api.smartsheet.com/2.0/users"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Error fetching contacts: {response.text}")

        users_data = response.json().get("data", [])
        if not users_data:
            raise UserError("No users found in the response.")

        # Extract user IDs
        user_ids = [user.get("id") for user in users_data if user.get("id")]

        # Process each user ID
        for user_id in user_ids:
            try:
                # Fetch detailed user information for each user ID
                user_detail_url = f"{base_url}/users/{user_id}"
                user_detail_response = requests.get(user_detail_url, headers=headers)

                if user_detail_response.status_code != 200:
                    raise UserError(f"Error fetching user details for ID {user_id}: {user_detail_response.text}")
                user_detail = user_detail_response.json()
                print(user_detail)
                user_id= user_detail.get('id')
                user_email = user_detail.get("email")
                user_first_name = user_detail.get("firstName")
                user_last_name = user_detail.get("lastName")
                lastLogin = user_detail.get("lastLogin")
                user_name = f"{user_first_name} {user_last_name}" if user_first_name and user_last_name else user_email
                user_partner=user_detail.get("account")
                if not user_email:
                    continue


                existing_user = self.env['res.users'].search([('login', '=', user_email)], limit=1)


                user_vals = {
                    'name': user_name,
                    'login': user_email,
                    'email': user_email,
                    'cr_smartsheet_user_id':user_id,
                    'login_date':lastLogin,
                }

                partner_vals = {
                    'name': user_name,
                    'email': user_email,
                    'phone': user_detail.get("workPhone"),
                    'mobile': user_detail.get("mobilePhone"),
                    'company_name': user_detail.get("company"),
                    'function': user_detail.get("title"),
                    'tz': user_detail.get("timeZone"),
                    'comment': user_detail.get("role"),
                    'cr_smart_sheet_id':user_partner.get("id"),
                }

                if existing_user:

                    existing_user.write(user_vals)
                    odoo_user = existing_user


                    partner = odoo_user.partner_id
                    partner.write(partner_vals)
                else:

                    odoo_user = self.env['res.users'].create(user_vals)


                    partner = odoo_user.partner_id
                    partner.write(partner_vals)


                if config.cr_import_user_image:
                    try:

                        image_id = user_detail.get("imageId")
                        if image_id:
                            image_url = f"{base_url}/users/{user_id}/image"
                            image_response = requests.get(image_url, headers=headers)

                            if image_response.status_code == 200:

                                image_base64 = base64.b64encode(image_response.content).decode('utf-8')
                                partner.write({'image_1920': image_base64})

                    except Exception as e:

                        return {
                            "type": "ir.actions.client",
                            "tag": "display_notification",
                            "params": {
                                "title": _("Image Import Error"),
                                "message": _(
                                    f"Error importing image for user {user_email}: {str(e)}."
                                ),
                                "type": "danger",
                                "sticky": False,
                            },
                        }

            except Exception as e:

                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("User Import Error"),
                        "message": _(
                            f"Error importing user with ID {user_id}: {str(e)}."
                        ),
                        "type": "danger",
                        "sticky": False,
                    },
                }

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Import Users"),
                "message": _(
                    "Users imported successfully."
                ),
                "type": "success",
                "sticky": False,
            },
        }