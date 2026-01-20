# -*- coding: utf-8 -*-

import base64, logging
import re
import json
from odoo import exceptions, http
from odoo.http import request
from .portal import CustomerPortalBlogs as portal

_logger = logging.getLogger(__name__)

class CustomerPortalBlogsController(http.Controller):
    _items_per_page = 10

    @http.route(['/blog/tag/<model("blog.tag"):tag>'], type='http', auth="public", website=True)
    def blog_filter_by_tag(self, tag, **kwargs):
        BlogPost = request.env['blog.post'].sudo()
        posts = BlogPost.search([('tag_ids', 'in', tag.ids)])
        values = {
            'tag': tag,
            'posts': posts,
        }
        return request.render("website_blog.blog_post_short", values)

    @http.route(['/my/blogs', '/my/blogs/page/<int:page>'], auth='user', website=True)
    def myBlogsListView(self, page=1, **kw):
        partner = request.env.user.partner_id.id
        blog_blog_id = self._get_community_id()
        blog_posts = request.env['blog.post'].sudo().search(portal._get_blogs_domain(self, partner)).filtered(
            lambda x: x.blog_id.id == blog_blog_id.id)

        pager = request.website.pager(
            url='/my/blogs',
            total=len(blog_posts),
            page=page,
            step=self._items_per_page,
            scope=7
        )

        return request.render("wb_portal_blogs.portal_my_blogs_list_view", {
            'blog_posts': blog_posts[pager['offset']:pager['offset'] + self._items_per_page],
            'pager': pager,
            'page_name': 'my_blogs',
            'breadcrumb': [('/my/home', 'Inicio'), ('/my/blogs', 'Mis Blogs')],
        })

    @http.route('/my/blog/edit/<int:blog_id>', type='http', auth="user", website=True, csrf=True,
                methods=['GET', 'POST'])
    def portal_blog_edit_profile(self, blog_id, **kwargs):
        print('1111111111111111111111111111111111111111111111111111111111111111')
        BlogPost = request.env['blog.post'].sudo()
        blog_blog_id = self._get_community_id()

        blog_entry = BlogPost.browse(blog_id)
        partner = request.env.user.partner_id
        blog_posts = blog_entry or BlogPost.search(portal._get_blogs_domain(self, partner.id)).filtered(
            lambda x: x.blog_id.id == blog_blog_id.id
        )

        # if blog_posts:
        #     blog_entry = blog_posts[0]
        #     blog_id = blog_posts[0].id

        # if blog_id == 0:
        if not blog_posts:
            # if request.httprequest.method == 'POST':
            vals = {
                'blog_id': blog_blog_id.id,
                'name': kwargs.get('name') or request.env.user.partner_id.name,
                'subtitle': '',
                'content': '',
                'is_published': False,
            }
            blog_entry = BlogPost.create(vals)
            blog_id = blog_entry.id
            # else:
            #     blog_entry = BlogPost.new({
            #         'blog_id': blog_blog_id.id,
            #         'name': kwargs.get('name') or request.env.user.partner_id.name,
            #     })

        if blog_entry.create_uid.partner_id != request.env.user.partner_id:
            return request.redirect('/my/blogs')

        # Manejar el envío del formulario (POST)
        if request.httprequest.method == 'POST':
            try:
                # Procesar categorías
                tag_ids = [int(value) for key, value in kwargs.items() if key.startswith("category-")]

                # Lista para las tuplas de comandos de actualización del one2many
                multimedia_updates = []

                # Obtener todos los índices de los campos de multimedia del formulario
                multimedia_indices = sorted(
                    # list(set(re.findall(r"multimedia_ids\[(-?\d+)\]\.id", ' '.join(kwargs.keys())))), key=int)
                    list(set(re.findall(r"multimedia_ids\[(-?\d+)]\.id", ' '.join(kwargs.keys())))), key=int)

                # Itera sobre los índices para procesar los campos de multimedia de forma segura
                for multimedia_index in multimedia_indices:
                    multimedia_id = int(kwargs.get('multimedia_ids[%s].id' % multimedia_index))
                    multimedia_type = kwargs.get('multimedia_ids[%s].content_type' % multimedia_index)
                    multimedia_url = kwargs.get('multimedia_ids[%s].content_url' % multimedia_index)

                    multimedia_file = request.httprequest.files.get(
                        'multimedia_ids[%s].content_file' % multimedia_index)

                    file_data = False
                    filename = kwargs.get('multimedia_ids[%s].content_file_filename' % multimedia_index)
                    mimetype = kwargs.get('multimedia_ids[%s].content_file_mimetype' % multimedia_index)

                    if multimedia_file and multimedia_file.filename:
                        file_data = base64.b64encode(multimedia_file.read())
                        filename = multimedia_file.filename
                        mimetype = multimedia_file.content_type

                    multimedia_vals = {
                        'content_type': multimedia_type,
                        'content_url': multimedia_url,
                    }
                    if file_data:
                        multimedia_vals['content_file'] = file_data
                        multimedia_vals['content_file_filename'] = filename
                        multimedia_vals['content_file_mimetype'] = mimetype

                    if multimedia_id > 0:
                        multimedia_updates.append((1, multimedia_id, multimedia_vals))
                    elif file_data or multimedia_url:
                        multimedia_updates.append((0, 0, multimedia_vals))

                current_multimedia_ids = blog_entry.multimedia_ids.ids
                submitted_multimedia_ids = [m[1] for m in multimedia_updates if m[0] == 1]
                multimedia_to_remove = list(set(current_multimedia_ids) - set(submitted_multimedia_ids))
                for multimedia_id in multimedia_to_remove:
                    multimedia_updates.append((2, multimedia_id))

                vals = {
                    'name': kwargs.get('name'),
                    'subtitle': kwargs.get('subtitle'),
                    'is_published': kwargs.get('is_published') == '1',
                    'only_text_content': kwargs.get('only_text_content'),
                    # 'content': kwargs.get('content'),
                    # 'content': multimedia_html,
                    'website_meta_title': kwargs.get('website_meta_title'),
                    'website_meta_description': kwargs.get('website_meta_description'),
                    'website_meta_keywords': kwargs.get('website_meta_keywords'),
                    'tag_ids': [(6, 0, tag_ids)],
                    'cover_properties': self._get_background_json(
                        kwargs.get('bg-img') or f'/web/image/blog.post/{blog_entry.id}/blog_entry_html'),
                    'multimedia_ids': multimedia_updates,
                }

                # Manejo de imágenes de cabecera de forma segura
                blog_entry_html_file = request.httprequest.files.get('blog_entry_html')
                if blog_entry_html_file and blog_entry_html_file.filename:
                    vals['blog_entry_html'] = base64.b64encode(blog_entry_html_file.read())

                main_image_file = request.httprequest.files.get('main_image')
                if main_image_file and main_image_file.filename:
                    vals['main_image'] = base64.b64encode(main_image_file.read())

                social_media_fields = [
                    'facebook_url',
                    'instagram_url',
                    'linkedin_url',
                    'twitter_url',
                    'youtube_url',
                    'github_url'
                ]

                # Creamos un diccionario para almacenar los valores que se van a actualizar
                author_vals = {}
                for field in social_media_fields:
                    url = kwargs.get(field, False)
                    # if url:
                    # Agregamos el campo y su URL al diccionario
                    author_vals[field] = url

                # Si hay URLs para actualizar, usamos el método 'write' en el registro del autor
                if author_vals:
                    blog_entry.author_id.write(author_vals)

                blog_entry.sudo().write(vals)

                multimedia_html = request.env['ir.ui.view']._render_template(
                    "wb_portal_blogs.portal_blog_multimedia_html",
                    {
                        'dynamic_text_content': blog_entry.only_text_content or '',
                        'id': blog_entry.id,  # Pasar el objeto blog_entry completo
                        'multimedia_items': blog_entry.multimedia_ids,
                    }
                )

                vals = {
                    'content': multimedia_html,
                }

                blog_entry.sudo().write(vals)

                return request.redirect('/my/blog/edit/%s?success=1' % blog_id)
                # vals['success'] = True
                # return request.render("wb_portal_blogs.portal_my_blogs_form_view_edit", vals)
            except exceptions.UserError as e:
                _logger.exception(e)
                return request.redirect('/my/blog/edit/%s?error=1' % blog_id)
                # return request.render("wb_portal_blogs.portal_my_blogs_form_view_edit", {'error': True})
            except Exception as e:
                _logger.exception(e)
                return request.redirect('/my/blog/edit/%s?error=1' % blog_id)
                # return request.render("wb_portal_blogs.portal_my_blogs_form_view_edit", {'error': True})

        # Manejar la carga de la página (GET)
        multimedia_items = blog_entry.multimedia_ids or request.env['blog.post.multimedia'].sudo()

        multimedia_html = request.env['ir.ui.view']._render_template(
            "wb_portal_blogs.portal_blog_multimedia_html",
            {
                'dynamic_text_content': blog_entry.only_text_content or '',
                'id': blog_entry.id,  # Pasar el objeto blog_entry completo
                'multimedia_items': multimedia_items,
            }
        )

        full_content = multimedia_html

        values = {
            'action': 'edit' if blog_id > 0 else 'new',
            'page_name': 'blog_edit',
            'blog_entry': blog_entry,
            'blog_entry_html': self._extract_image_html(blog_entry.cover_properties),
            'blog_ids': blog_blog_id,
            'tag_ids': request.env['blog.tag'].search([]),
            'full_content': full_content,
        }

        if kwargs.get('success'):
            values['error'] = False
        if kwargs.get('error'):
            values['error'] = True

        return request.render("wb_portal_blogs.portal_my_blogs_form_view_edit", values)

    def _get_background_json(self, val):
        # Se espera recibir el HTML en el parámetro "html_string"
        html_string = val

        # Buscamos la etiqueta <img> y extraemos lo que esté dentro de src=""
        # match = re.search(r'<img[^>]+src="([^"]+)"', html_string)
        match = val or False
        if match:
            # image_src = match.group(1)
            image_src = val
            # Se define el JSON actualizado para el caso en que se encuentra una imagen:
            result_data = {
                "background-image": "url(" + image_src + ")",
                "background_color_class": "o_cc3 o_cc",  # Puedes ajustar este valor según tus necesidades
                "background_color_style": "",
                "opacity": "0.2",
                "resize_class": "o_half_screen_height o_record_has_cover",
                # Igual puedes modificarlo según tus requerimientos
                "text_align_class": ""
            }
        else:
            # Si no se encontró ninguna ruta, se utiliza el JSON por defecto
            result_data = {
                "background-image": "none",
                "background_color_class": "o_cc3 o_cc",
                "background_color_style": "",
                "opacity": "0.2",
                "resize_class": "cover_auto",
                "text_align_class": ""
            }

        # Odoo se encargará de serializar el diccionario a JSON automáticamente
        return json.dumps(result_data)

    def _extract_image_html(self, json_str):
        """
        Recibe una cadena JSON con la siguiente estructura:
          {
            "background-image": "url(/web/image/1216-bfc69190/EMCOOP-7.jpg)",
            "background_color_class": "o_cc3 o_cc",
            "background_color_style": "",
            "opacity": "0.2",
            "resize_class": "o_half_screen_height o_record_has_cover",
            "text_align_class": ""
          }

        Si se encuentra la URL en el campo "background-image", se retorna un HTML con ese formato:
          <p><img src="/web/image/1216-bfc69190/EMCOOP-7.jpg" class="img img-fluid o_we_custom_image" style="width: 50%;"><br></p>

        Si no se encuentra la URL, se devuelve por defecto:
          <p><img src="/web/image/1360-f72d89e1/marvin-meyer-SYTO3xs06fU-unsplash.jpg" class="img img-fluid o_we_custom_image" style="width: 50%;"><br></p>
        """
        # HTML por defecto a usar si la URL no se encuentra o si ocurre un error al parsear
        default_html = (
            '                                <p><img src="/web/image/1360-f72d89e1/marvin-meyer-SYTO3xs06fU-unsplash.jpg" '
            'class="img img-fluid o_we_custom_image" style="width: 50%;"><br></p>\n'
        )

        try:
            data = json.loads(json_str.strip())
        except Exception as e:
            # Si falla el parseo del JSON, devolvemos el HTML por defecto
            print("Error al parsear el JSON:", e)
            return default_html

        # Extraemos el valor de "background-image"
        bg_image = data.get("background-image", "")

        # Extraemos la URL que se encuentre dentro de url(...)
        match = re.search(r'url\((.*?)\)', bg_image)
        if match:
            image_url = match.group(1)
            html = (
                '<p><img src="{}" class="img img-fluid o_we_custom_image" style="width: 50%;"><br></p>'
            ).format(image_url)
            return html
        else:
            # Si no se encuentra el patrón, devolvemos el HTML por defecto
            return default_html

    def _get_community_id(self):
        BlogPost = request.env['blog.post'].sudo()
        return BlogPost.blog_id.search([('name', 'ilike', 'comunidad')], limit=1)

    def portal_blog_edit(self, action, blog_id, **kwargs):
        print('11111111111111111111111111111111222222222222')
        values = {}
        try:
            BlogPost = request.env['blog.post'].sudo()
            blog_entry = BlogPost.browse(blog_id)
            # Verificar que el usuario actual es el autor de la entrada.
            # if blog_entry.author_id != request.env.user.partner_id:
            #     return request.render('http_routing.404')

            # Si el método es POST, se actualizan los datos
            if request.httprequest.method == 'POST' and kwargs:
                # Actualiza los campos de la entrada
                # vals = {
                #     'name': kwargs.get('name'),
                #     'content': kwargs.get('content'),
                # }
                vals = {
                    'is_published': kwargs.get('is_published') == '1',
                    'blog_id': int(kwargs.get('blog_id_edit')) if kwargs.get('blog_id_edit') else False,
                    'name': kwargs.get('name'),
                    'subtitle': kwargs.get('subtitle', ''),
                    # Para el campo Many2many "tag_ids", se espera un comando (6, 0, [ids])
                    # Suponiendo que 'tag_id' viene como una cadena con los IDs separados por comas,
                    # se parsea y se monta la lista; si ya es una lista, adapta según corresponda.
                    'tag_ids': [(6, 0, [int(value) for key, value in kwargs.items() if key.startswith("category-")])],
                    # if kwargs.get('tag_id') else [],
                    'cover_properties': self._get_background_json(kwargs.get('bg-img')),
                    'content': kwargs.get('content'),
                    'website_meta_title': kwargs.get('website_meta_title', ''),
                    'website_meta_description': kwargs.get('website_meta_description', ''),
                    'website_meta_keywords': kwargs.get('website_meta_keywords', ''),
                }
                if action == 'new':
                    resp = BlogPost.create(vals)
                    action = 'complete'
                elif action == 'edit':
                    blog_entry.sudo().write(vals)
                # Redirige tras la actualización
                # return request.redirect('/my/blogs')

                values['error'] = False
            if action == 'new':
                values.update({
                    'action': action,
                    'page_name': 'blog_edit',
                    'blog_entry': BlogPost,
                    'blog_entry_html': self._extract_image_html(''),
                    'blog_ids': blog_entry.blog_id.search([('name', 'ilike', 'comunidad')], limit=1),
                    # BlogPost.blog_id.search([]),
                    'tag_ids': BlogPost.tag_ids.search([])
                })
            elif action == 'edit':
                values.update({
                    'action': action,
                    'page_name': 'blog_edit',
                    'blog_entry': blog_entry,
                    'blog_entry_html': self._extract_image_html(blog_entry.cover_properties),
                    'blog_ids': blog_entry.blog_id.search([('name', 'ilike', 'comunidad')], limit=1),
                    # blog_entry.blog_id.search([]),
                    'tag_ids': blog_entry.tag_ids.search([])
                })
        except Exception as exc:
            values.update({
                'error': True,
                'page_name': 'blog_edit',
                'blog_entry': blog_entry if blog_entry else BlogPost,
            })
        return request.render("wb_portal_blogs.portal_my_blogs_form_view_edit", values)

    # ───────────────────────────────────────────────────────────────
    # 📬 REGIÓN: Lógica relacionada con mensajes y comunicación
    # Aquí se agrupan todas las operaciones de lectura, agrupación,
    # y conteo de mensajes de usuarios (portal u otros).
    # ───────────────────────────────────────────────────────────────

    # @http.route(['/my/messages', '/my/messages/page/<int:page>'], auth='user', website=True)
    # def myMessagesListView(self, page=1, **kw):
    #     partner = request.env.user.partner_id.id
    #     blog_blog_id = self._get_community_id()
    #     # blog_posts = request.env['blog.post'].sudo().search(portal._get_blogs_domain(self, partner)).filtered(
    #     blog_posts_messages = request.env['blog.post'].sudo().search([]).filtered(lambda x:
    #                                                                               x.blog_id.id == blog_blog_id.id
    #                                                                               and x.message_ids
    #                                                                               )
    #     # blog_posts_messages = blog_posts.filtered(lambda blog_id: blog_id.message_ids)
    #
    #     message_ids = list()
    #     for bpm in blog_posts_messages:
    #         author_ids = bpm.message_ids.filtered(lambda x: x.author_id.id != partner).author_id
    #         for a in author_ids:
    #             message_id = request.env['mail.message'].sudo()
    #             message_id |= bpm.message_ids.filtered(lambda x: x.author_id.id == a.id)
    #             message_ids.append({
    #                 'blog_id': bpm,
    #                 'message_id': message_id,
    #                 'count_message': len(message_id)
    #             })
    #
    #     pager = request.website.pager(
    #         url='/my/messages',
    #         total=len(message_ids),
    #         page=page,
    #         step=self._items_per_page,
    #         scope=7
    #     )
    #
    #     return request.render("wb_portal_blogs.portal_my_messages_list_view", {
    #         'message_ids': message_ids[pager['offset']:pager['offset'] + self._items_per_page],
    #         'pager': pager,
    #         'page_name': 'my_messages',
    #         'breadcrumb': [('/my/home', 'Inicio'), ('/my/messages', 'Mis Mensajes')],
    #     })

    @http.route(['/my/messages', '/my/messages/page/<int:page>'], auth='user', website=True)
    def myMessagesListView(self, page=1, **kw):
        print("------ ENTER myMessagesListView ------")
        print(f"Page: {page}, kw: {kw}")

        partner = request.env.user.partner_id.id
        print(f"Current Partner ID: {partner}")

        blog_blog_id = self._get_community_id()
        print(f"Community Blog ID: {blog_blog_id.id if blog_blog_id else 'No Blog Found'}")

        # Fetch blog posts that belong to this blog and have messages
        blog_posts_messages = request.env['blog.post'].sudo().search([]).filtered(lambda x:
                                                                                  x.blog_id.id == blog_blog_id.id
                                                                                  and x.message_ids
                                                                                  )
        print(f"Found {len(blog_posts_messages)} blog posts with messages")

        message_ids = list()
        for bpm in blog_posts_messages:
            print(f"Processing Blog Post: {bpm.id} - {bpm.name}")
            author_ids = bpm.message_ids.filtered(lambda x: x.author_id.id != partner).author_id
            print(f"Found {len(author_ids)} unique authors (excluding current partner)")

            for a in author_ids:
                print(f"Processing Author: {a.id} - {a.name}")
                message_id = request.env['mail.message'].sudo()
                filtered_msgs = bpm.message_ids.filtered(lambda x: x.author_id.id == a.id)
                print(f"Messages by this author in this post: {len(filtered_msgs)}")
                message_id |= filtered_msgs

                message_data = {
                    'blog_id': bpm,
                    'message_id': message_id,
                    'count_message': len(message_id)
                }
                print(f"Appending message data: blog_id={bpm.id}, count={len(message_id)}")
                message_ids.append(message_data)

        print(f"Total message groups prepared: {len(message_ids)}")

        pager = request.website.pager(
            url='/my/messages',
            total=len(message_ids),
            page=page,
            step=self._items_per_page,
            scope=7
        )
        print(f"Pager Info: {pager}")

        render_data = {
            'message_ids': message_ids[pager['offset']:pager['offset'] + self._items_per_page],
            'pager': pager,
            'page_name': 'my_messages',
            'breadcrumb': [('/my/home', 'Inicio'), ('/my/messages', 'Mis Mensajes')],
        }
        print(f"Rendering with {len(render_data['message_ids'])} paginated items")

        print("------ EXIT myMessagesListView ------")
        return request.render("wb_portal_blogs.portal_my_messages_list_view", render_data)

    @http.route(['/my/messages/thread/partner/<int:partner_id>/blog/<int:blog_id>'], type='http', auth="user",
                website=True, csrf=True)
    def portal_messages_profile(self, partner_id, blog_id, **kwargs):
        values = {}
        try:
            blog_entry = partner = filtered_messages = None

            if blog_id and partner_id:
                blog_entry = request.env['blog.post'].sudo().browse(int(blog_id))
                partner = request.env['res.partner'].sudo().browse(int(partner_id))

                # filtered_messages = blog_entry.message_ids.filtered(
                #     lambda m: m.author_id.id in [partner.id] and m.message_type == 'comment' or not m.parent_id
                # )
                #
                # blog_entry.message_ids = filtered_messages
            values = {
                'blog_entry': blog_entry,
                'partner': partner,
            }
        except Exception as exc:
            values.update({
                'error': True,
                # 'page_name': 'blog_edit',
            })
        return request.render("wb_portal_blogs.portal_my_messages_form_view", values)
