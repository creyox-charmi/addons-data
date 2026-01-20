# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    document_folder_id = fields.Many2one('documents.document', string="Document Folder", readonly=True,
                                         domain=[('type', '=', 'folder')])
    document_count = fields.Integer(compute='_compute_document_count', string="Document Count")

    @api.model_create_multi
    def create(self, vals):
        lead = super(CrmLead, self).create(vals)
        lead._create_document_folder()
        return lead

    def write(self, vals):
        res = super(CrmLead, self).write(vals)

        # Handle partner changes
        if 'partner_id' in vals:
            for lead in self:
                if lead.document_folder_id:
                    # Store old folder structure before changes
                    old_opportunity_folder = lead.document_folder_id
                    old_partner_folder = old_opportunity_folder.folder_id

                    # Get all existing documents and subfolders
                    existing_documents = self.env['documents.document'].search([
                        ('folder_id', 'child_of', old_opportunity_folder.id),
                        ('type', '=', 'binary')
                    ])

                    existing_subfolders = self.env['documents.document'].search([
                        ('folder_id', '=', old_opportunity_folder.id),
                        ('type', '=', 'folder')
                    ])

                    # Create new folder structure in new partner location
                    lead._create_document_folder()
                    new_opportunity_folder = lead.document_folder_id

                    if old_opportunity_folder.id != new_opportunity_folder.id:
                        # Move existing documents to new location
                        lead._move_existing_documents_to_new_folder(
                            existing_documents,
                            existing_subfolders,
                            old_opportunity_folder,
                            new_opportunity_folder
                        )

                        # Clean up old folder structure if empty
                        lead._cleanup_old_folder_structure(old_opportunity_folder, old_partner_folder)

        # Handle name changes
        if 'name' in vals:
            for lead in self:
                if lead.document_folder_id:
                    # Update the opportunity folder name
                    folder_name_with_number = f"{lead.custom_number.lstrip('OPPORTUNITY/')}-{lead.name}"
                    lead.document_folder_id.with_context(bypass_master_folder_check=True).write({
                        'name': folder_name_with_number
                    })

        return res

    def _get_or_create_partner_folder(self):
        """Get or create partner folder under Marketing/Opportunities"""
        # Get the Opportunities folder under Marketing
        opportunities_folder = self.env['documents.document'].search([
            ('name', '=', 'Opportunities'),
            ('type', '=', 'folder'),
            ('folder_id.name', '=', 'Marketing')
        ], limit=1)

        if not opportunities_folder:
            _logger.error("Opportunities folder not found under Marketing!")
            return False

        # Determine partner folder name
        if self.partner_id:
            partner_folder_name = self.partner_id.name or f"Partner_{self.partner_id.id}"
        else:
            partner_folder_name = "Anonymous Partner"

        # Check if partner folder already exists
        partner_folder = self.env['documents.document'].search([
            ('name', '=', partner_folder_name),
            ('type', '=', 'folder'),
            ('folder_id', '=', opportunities_folder.id)
        ], limit=1)

        if not partner_folder:
            # Create partner folder
            partner_folder = self.env['documents.document'].create({
                'name': partner_folder_name,
                'type': 'folder',
                'folder_id': opportunities_folder.id,
                'company_id': self.company_id.id,
                'is_master_folder': True,
            })

        return partner_folder

    def _create_document_folder(self):
        """Create document folder structure for the opportunity"""
        # Get or create partner folder
        partner_folder = self._get_or_create_partner_folder()
        if not partner_folder:
            return

        # Create opportunity folder name with number and name
        folder_name_with_number = f"{self.custom_number.lstrip('OPPORTUNITY/')}-{self.name}"

        # Check if opportunity folder already exists (in case of updates)
        existing_folder = self.env['documents.document'].search([
            ('name', '=', folder_name_with_number),
            ('type', '=', 'folder'),
            ('folder_id', '=', partner_folder.id)
        ], limit=1)

        if existing_folder:
            self.document_folder_id = existing_folder
            return

        # Create opportunity folder
        opportunity_folder = self.env['documents.document'].create({
            'name': folder_name_with_number,
            'type': 'folder',
            'folder_id': partner_folder.id,
            'company_id': self.company_id.id,
            'is_master_folder': True,
        })

        # Create static subfolders
        subfolders = ['Technical Data', 'Vendor Quotations', 'Costing', 'Quotation', 'Sales Order']
        for subfolder_name in subfolders:
            self.env['documents.document'].create({
                'name': subfolder_name,
                'type': 'folder',
                'folder_id': opportunity_folder.id,
                'company_id': self.company_id.id,
                'is_master_folder': True,
            })

        self.document_folder_id = opportunity_folder

    def _compute_document_count(self):
        for lead in self:
            if lead.document_folder_id:
                lead.document_count = self.env['documents.document'].search_count([
                    ('folder_id', 'child_of', lead.document_folder_id.id),
                    ('type', '=', 'binary')
                ])
            else:
                lead.document_count = 0

    def action_open_documents(self):
        self.ensure_one()
        if not self.document_folder_id:
            self._create_document_folder()

        # Get the standard documents action and modify it
        action = self.env['ir.actions.act_window']._for_xml_id('documents.document_action')

        # Customize the action for our specific folder - show files and folders
        action.update({
            'name': f"Documents - {self.name}",
            'domain': [
                ('folder_id', 'child_of', self.document_folder_id.id),
                '|',
                ('type', '=', 'binary'),  # Show files
                ('folder_id', '=', self.document_folder_id.id)  # Show immediate subfolders
            ],
            'context': {
                'default_folder_id': self.document_folder_id.id,
                'searchpanel_default_folder_id': self.document_folder_id.id,
            },
            'target': 'current',
        })

        return action

    def action_view_partner_opportunities(self):
        """Action to view all opportunities for the same partner"""
        self.ensure_one()

        # Handle both partner and anonymous cases
        if self.partner_id:
            domain = [('partner_id', '=', self.partner_id.id)]
            name = f"Opportunities - {self.partner_id.name}"
            context = {'default_partner_id': self.partner_id.id}
        else:
            domain = [('partner_id', '=', False)]
            name = "Opportunities - Anonymous Partner"
            context = {}

        action = self.env['ir.actions.act_window']._for_xml_id('crm.crm_lead_opportunities')
        action.update({
            'name': name,
            'domain': domain,
            'context': context,
        })
        return action

    def _move_existing_documents_to_new_folder(self, existing_documents, existing_subfolders, old_opportunity_folder,
                                               new_opportunity_folder):
        """Move existing documents and recreate folder structure in new location"""

        # Create a mapping of old subfolder names to new subfolders
        new_subfolders = self.env['documents.document'].search([
            ('folder_id', '=', new_opportunity_folder.id),
            ('type', '=', 'folder')
        ])

        # Create mapping dictionary for subfolder relocation
        subfolder_mapping = {}
        for old_subfolder in existing_subfolders:
            # Find corresponding new subfolder by name
            new_subfolder = new_subfolders.filtered(lambda f: f.name == old_subfolder.name)
            if new_subfolder:
                subfolder_mapping[old_subfolder.id] = new_subfolder[0].id
            else:
                # If subfolder doesn't exist in new structure, create it
                new_subfolder = self.env['documents.document'].create({
                    'name': old_subfolder.name,
                    'type': 'folder',
                    'folder_id': new_opportunity_folder.id,
                    'company_id': self.company_id.id,
                    'is_master_folder': True,
                })
                subfolder_mapping[old_subfolder.id] = new_subfolder.id

        # Move documents to appropriate folders
        for document in existing_documents:
            try:
                # Determine new folder location
                if document.folder_id.id == old_opportunity_folder.id:
                    # Document is in root opportunity folder
                    new_folder_id = new_opportunity_folder.id
                elif document.folder_id.id in subfolder_mapping:
                    # Document is in a subfolder
                    new_folder_id = subfolder_mapping[document.folder_id.id]
                else:
                    # Fallback to root opportunity folder
                    new_folder_id = new_opportunity_folder.id

                # Move the document
                document.with_context(bypass_master_folder_check=True).write({
                    'folder_id': new_folder_id
                })

            except Exception as e:
                _logger.error(f"Failed to move document {document.name}: {str(e)}")

        return True

    def _cleanup_old_folder_structure(self, old_opportunity_folder, old_partner_folder):
        """Clean up old folder structure if it's empty"""
        try:
            # Check if old opportunity folder has any remaining documents
            remaining_docs = self.env['documents.document'].search_count([
                ('folder_id', 'child_of', old_opportunity_folder.id),
                ('type', '=', 'binary')
            ])

            if remaining_docs == 0:
                # Delete old subfolders first
                old_subfolders = self.env['documents.document'].search([
                    ('folder_id', '=', old_opportunity_folder.id),
                    ('type', '=', 'folder')
                ])
                if old_subfolders:
                    old_subfolders.unlink()

                # Delete old opportunity folder
                old_opportunity_folder.unlink()

                # Check if old partner folder is now empty (except for Anonymous Partner)
                if old_partner_folder.name != "Anonymous Partner":
                    remaining_opportunities = self.env['documents.document'].search_count([
                        ('folder_id', '=', old_partner_folder.id),
                        ('type', '=', 'folder')
                    ])

                    if remaining_opportunities == 0:
                        old_partner_folder.unlink()

        except Exception as e:
            _logger.error(f"Error during folder cleanup: {str(e)}")