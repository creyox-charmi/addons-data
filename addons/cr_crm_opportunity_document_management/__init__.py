# -*- coding: utf-8 -*-
from . import models

import logging
from odoo import api

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """
    Post-installation hook to create/update document folders for existing CRM leads/opportunities
    Handles both:
    1. Opportunities without folders - creates new folder structure
    2. Opportunities with old folder structure - migrates to new structure
    """
    _logger.info("Starting post-install hook for CRM Document Management...")

    try:
        # Ensure the base folder structure exists
        _ensure_base_folder_structure(env)

        # Get all existing leads/opportunities
        all_leads = env['crm.lead'].search([])
        _logger.info(f"Found {len(all_leads)} total opportunities to process")

        if not all_leads:
            _logger.info("No opportunities found")
            return

        # Separate leads into different categories
        leads_without_folders = []
        leads_with_old_structure = []
        leads_with_new_structure = []

        for lead in all_leads:
            if not lead.document_folder_id:
                leads_without_folders.append(lead)
            else:
                # Check if it's using the new structure
                if _is_new_folder_structure(lead):
                    leads_with_new_structure.append(lead)
                else:
                    leads_with_old_structure.append(lead)

        _logger.info(f"Classification: {len(leads_without_folders)} without folders, "
                     f"{len(leads_with_old_structure)} with old structure, "
                     f"{len(leads_with_new_structure)} already with new structure")

        total_processed = 0
        total_success = 0

        # Process leads without folders first
        if leads_without_folders:
            _logger.info("Processing opportunities without folders...")
            success_count = _process_leads_without_folders(env, leads_without_folders)
            total_processed += len(leads_without_folders)
            total_success += success_count

        # Process leads with old structure
        if leads_with_old_structure:
            _logger.info("Processing opportunities with old folder structure...")
            success_count = _process_leads_with_old_structure(env, leads_with_old_structure)
            total_processed += len(leads_with_old_structure)
            total_success += success_count

        # Final commit
        env.cr.commit()
        _logger.info(f"Post-install hook completed. Successfully processed {total_success}/{total_processed} opportunities")

    except Exception as e:
        _logger.error(f"Error in post-install hook: {str(e)}")
        env.cr.rollback()
        raise

def _ensure_base_folder_structure(env):
    """Ensure the base Marketing/Opportunities folder structure exists"""
    try:
        marketing_folder = env['documents.document'].search([
            ('name', '=', 'Marketing'),
            ('type', '=', 'folder'),
            ('folder_id', '=', False)
        ], limit=1)

        if not marketing_folder:
            _logger.warning("Marketing folder not found, creating it...")
            marketing_folder = env['documents.document'].create({
                'name': 'Marketing',
                'type': 'folder',
                'folder_id': False,
                'company_id': env.company.id,
                'is_master_folder': True,
            })
            _logger.info("Created Marketing folder")

        opportunities_folder = env['documents.document'].search([
            ('name', '=', 'Opportunities'),
            ('type', '=', 'folder'),
            ('folder_id', '=', marketing_folder.id)
        ], limit=1)

        if not opportunities_folder:
            _logger.warning("Opportunities folder not found, creating it...")
            opportunities_folder = env['documents.document'].create({
                'name': 'Opportunities',
                'type': 'folder',
                'folder_id': marketing_folder.id,
                'company_id': env.company.id,
                'is_master_folder': True,
            })
            _logger.info("Created Opportunities folder")

        _logger.info("Base folder structure verified successfully")

    except Exception as e:
        _logger.error(f"Error ensuring base folder structure: {str(e)}")
        raise

def _is_new_folder_structure(lead):
    """
    Check if the lead's folder follows the new structure:
    Marketing/Opportunities/PartnerName/OpportunityNumber-OpportunityName/
    """
    if not lead.document_folder_id:
        return False

    try:
        opportunity_folder = lead.document_folder_id
        partner_folder = opportunity_folder.folder_id
        opportunities_folder = partner_folder.folder_id if partner_folder else None
        marketing_folder = opportunities_folder.folder_id if opportunities_folder else None

        # Check the hierarchy: Marketing -> Opportunities -> Partner -> Opportunity
        return (marketing_folder and marketing_folder.name == 'Marketing' and
                opportunities_folder and opportunities_folder.name == 'Opportunities' and
                partner_folder and opportunity_folder)
    except Exception:
        return False

def _process_leads_without_folders(env, leads):
    """Process opportunities that don't have any document folders"""
    success_count = 0

    for i, lead in enumerate(leads):
        try:
            lead._create_document_folder()
            success_count += 1
            _logger.debug(f"Created folder structure for opportunity: {lead.name}")

        except Exception as e:
            _logger.error(f"Failed to create folder for opportunity {lead.name} (ID: {lead.id}): {str(e)}")

        # Commit every 50 records
        if (i + 1) % 50 == 0:
            env.cr.commit()
            _logger.info(f"Processed {i + 1}/{len(leads)} opportunities without folders")

    return success_count

def _process_leads_with_old_structure(env, leads):
    """Process opportunities that have old folder structure and migrate them"""
    success_count = 0

    for i, lead in enumerate(leads):
        try:
            if _migrate_old_folder_structure(env, lead):
                success_count += 1
                _logger.debug(f"Migrated folder structure for opportunity: {lead.name}")

        except Exception as e:
            _logger.error(f"Failed to migrate folder for opportunity {lead.name} (ID: {lead.id}): {str(e)}")

        # Commit every 50 records
        if (i + 1) % 50 == 0:
            env.cr.commit()
            _logger.info(f"Processed {i + 1}/{len(leads)} opportunities with old structure")

    return success_count

def _migrate_old_folder_structure(env, lead):
    """
    Migrate an opportunity from old folder structure to new structure
    Returns True if successful, False otherwise
    """
    try:
        old_folder = lead.document_folder_id
        if not old_folder:
            return False

        _logger.info(f"Migrating folder structure for opportunity: {lead.name}")

        # Get all existing documents and subfolders from old structure
        existing_documents = env['documents.document'].search([
            ('folder_id', 'child_of', old_folder.id),
            ('type', '=', 'binary')
        ])

        existing_subfolders = env['documents.document'].search([
            ('folder_id', '=', old_folder.id),
            ('type', '=', 'folder')
        ])

        _logger.debug(f"Found {len(existing_documents)} documents and {len(existing_subfolders)} subfolders to migrate")

        # Store reference to old folder and its parent
        old_folder_parent = old_folder.folder_id

        # Create new folder structure using existing method
        lead._create_document_folder()
        new_folder = lead.document_folder_id

        if not new_folder or new_folder.id == old_folder.id:
            _logger.warning(f"New folder creation failed or returned same folder for {lead.name}")
            return False

        # Move existing documents and subfolders to new structure
        if existing_documents or existing_subfolders:
            _move_documents_to_new_structure(env, lead, existing_documents, existing_subfolders,
                                            old_folder, new_folder)

        # Clean up old folder structure
        _cleanup_old_folder_after_migration(env, old_folder, old_folder_parent)

        _logger.info(f"Successfully migrated folder structure for opportunity: {lead.name}")
        return True

    except Exception as e:
        _logger.error(f"Error migrating folder structure for {lead.name}: {str(e)}")
        return False

def _move_documents_to_new_structure(env, lead, existing_documents, existing_subfolders, old_folder, new_folder):
    """Move documents and subfolders from old structure to new structure"""
    try:
        # Get the new subfolders created by _create_document_folder
        new_subfolders = env['documents.document'].search([
            ('folder_id', '=', new_folder.id),
            ('type', '=', 'folder')
        ])

        # Create mapping of old subfolder names to new subfolders
        subfolder_mapping = {}
        for old_subfolder in existing_subfolders:
            # Find corresponding new subfolder by name
            new_subfolder = new_subfolders.filtered(lambda f: f.name == old_subfolder.name)
            if new_subfolder:
                subfolder_mapping[old_subfolder.id] = new_subfolder[0].id
            else:
                # If subfolder doesn't exist in new structure, create it
                new_subfolder = env['documents.document'].create({
                    'name': old_subfolder.name,
                    'type': 'folder',
                    'folder_id': new_folder.id,
                    'company_id': lead.company_id.id or env.company.id,
                    'is_master_folder': True,
                })
                subfolder_mapping[old_subfolder.id] = new_subfolder.id
                _logger.debug(f"Created missing subfolder: {old_subfolder.name}")

        # Move documents to appropriate folders
        for document in existing_documents:
            try:
                if document.folder_id.id == old_folder.id:
                    # Document is in root old folder - move to root new folder
                    new_folder_id = new_folder.id
                elif document.folder_id.id in subfolder_mapping:
                    # Document is in a subfolder - move to corresponding new subfolder
                    new_folder_id = subfolder_mapping[document.folder_id.id]
                else:
                    # Fallback - move to root new folder
                    new_folder_id = new_folder.id

                document.with_context(bypass_master_folder_check=True).write({
                    'folder_id': new_folder_id
                })

            except Exception as e:
                _logger.error(f"Failed to move document {document.name}: {str(e)}")

        _logger.debug(f"Moved {len(existing_documents)} documents to new structure")

    except Exception as e:
        _logger.error(f"Error moving documents to new structure: {str(e)}")
        raise

def _cleanup_old_folder_after_migration(env, old_folder, old_folder_parent):
    """Clean up old folder structure after successful migration"""
    try:
        # Check if old folder has any remaining documents
        remaining_docs = env['documents.document'].search_count([
            ('folder_id', 'child_of', old_folder.id),
            ('type', '=', 'binary')
        ])

        if remaining_docs > 0:
            _logger.warning(f"Old folder {old_folder.name} still has {remaining_docs} documents, not cleaning up")
            return

        # Delete old subfolders first
        old_subfolders = env['documents.document'].search([
            ('folder_id', '=', old_folder.id),
            ('type', '=', 'folder')
        ])
        if old_subfolders:
            old_subfolders.unlink()
            _logger.debug(f"Deleted {len(old_subfolders)} old subfolders")

        # Delete old opportunity folder
        old_folder.unlink()
        _logger.debug(f"Deleted old opportunity folder: {old_folder.name}")

        # Check if old parent folder is now empty and can be cleaned up
        if old_folder_parent:
            remaining_folders = env['documents.document'].search_count([
                ('folder_id', '=', old_folder_parent.id),
                ('type', '=', 'folder')
            ])

            remaining_docs = env['documents.document'].search_count([
                ('folder_id', '=', old_folder_parent.id),
                ('type', '=', 'binary')
            ])

            # Only delete if it's not a system folder and it's empty
            if (remaining_folders == 0 and remaining_docs == 0 and
                old_folder_parent.name not in ['Marketing', 'Opportunities', 'Anonymous Partner']):
                old_folder_parent.unlink()
                _logger.debug(f"Deleted empty old parent folder: {old_folder_parent.name}")

    except Exception as e:
        _logger.error(f"Error cleaning up old folder structure: {str(e)}")