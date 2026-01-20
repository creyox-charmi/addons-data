# -*- coding: utf-8 -*-
# Extiende el modelo de entradas de blog para añadir campos de contenido multimedia.

from odoo import fields, models


# 1. Creamos un nuevo modelo para el contenido multimedia.
class BlogPostMultimedia(models.Model):
    _name = 'blog.post.multimedia'
    _description = 'Contenido Multimedia para Entradas de Blog'

    # Campos para el tipo de contenido y el valor (archivo o URL)
    content_type = fields.Selection([
        ('none', 'Ninguno'),
        ('image', 'Imagen'),
        ('file', 'Archivo'),
        ('videoMp4', 'Video'),
        ('video', 'Video (URL)')
    ], string='Tipo de Contenido', default='none', required=True)
    content_file = fields.Binary(string="Archivo", attachment=True)
    content_url = fields.Char(string="Enlace URL")
    # Campos para el nombre y el tipo de archivo (se llenan automáticamente)
    content_file_filename = fields.Char(string='Nombre del Archivo')
    content_file_mimetype = fields.Char(string='Tipo de Archivo')

    # Campo para la relación con la entrada de blog.
    blog_post_id = fields.Many2one('blog.post', string='Entrada de Blog', ondelete='cascade')
