from odoo import api, models, fields
from odoo.addons.http_routing.models.ir_http import unslug


class BlogPostExtension(models.Model):
    _inherit = 'blog.post'

    # Campo One2many que relaciona esta entrada de blog con el nuevo modelo de multimedia.
    # El primer argumento es el nombre del modelo con el que se relaciona.
    # El segundo es el nombre del campo en ese otro modelo que hace la relación (blog_post_id).
    multimedia_ids = fields.One2many('blog.post.multimedia', 'blog_post_id', string='Elementos Multimedia')

    only_text_content = fields.Html('Contenido Principal')
    main_image = fields.Binary('Imagen Principal', attachment=True)
    blog_entry_html = fields.Binary(string='HTML Entry Image', help="Image for the blog entry's title.")

    # Extiende el modelo para asegurar que el campo 'author_id' es accesible
    author_id = fields.Many2one(
        'res.partner',
        string='Autor',
        help="El autor de la publicación del blog."
    )

    @api.model
    def _search_get_detail(self, website, order, options):
        with_description = options['displayDescription']
        with_date = options['displayDetail']
        blog = options.get('blog')
        tags = options.get('tag')
        date_begin = options.get('date_begin')
        date_end = options.get('date_end')
        state = options.get('state')
        domain = [website.website_domain()]
        if blog:
            domain.append([('blog_id', '=', unslug(blog)[1])])
        if tags:
            active_tag_ids = [unslug(tag)[1] for tag in tags.split(',')] or []
            if active_tag_ids:
                domain.append([('tag_ids', 'in', active_tag_ids)])
        if date_begin and date_end:
            domain.append([("post_date", ">=", date_begin), ("post_date", "<=", date_end)])
        if self.env.user.has_group('website.group_website_designer'):
            if state == "published":
                domain.append([("website_published", "=", True), ("post_date", "<=", fields.Datetime.now())])
            elif state == "unpublished":
                domain.append(['|', ("website_published", "=", False), ("post_date", ">", fields.Datetime.now())])
        else:
            domain.append([("post_date", "<=", fields.Datetime.now())])
        search_fields = ['name', 'author_name']

        def search_in_tags(env, search_term):
            tags_like_search = env['blog.tag'].search([('name', 'ilike', search_term)])
            print(tags_like_search)
            return [('tag_ids', 'in', tags_like_search.ids)]

        fetch_fields = ['name', 'website_url']
        mapping = {
            'name': {'name': 'name', 'type': 'text', 'match': True},
            'website_url': {'name': 'website_url', 'type': 'text', 'truncate': False},
        }
        if with_description:
            search_fields.append('content')
            fetch_fields.append('content')
            mapping['description'] = {'name': 'content', 'type': 'text', 'html': True, 'match': True}

            search_fields.append('author_id.country_id.name')  # 🚨 AÑADIDO
            search_fields.append('author_id.state_id.name')  # 🚨 AÑADIDO

        if with_date:
            fetch_fields.append('published_date')
            mapping['detail'] = {'name': 'published_date', 'type': 'date'}
        return {
            'model': 'blog.post',
            'base_domain': domain,
            'search_fields': search_fields,
            'search_extra': search_in_tags,
            'fetch_fields': fetch_fields,
            'mapping': mapping,
            'icon': 'fa-rss',
            # 'requires_sudo': True,
        }
