odoo.define('wb_portal_blogs.wysiwyg_custom', function (require) {
'use strict';
    //   alert('hola mundo');
    //console.info('-----------------------------');
    var publicWidget = require('web.public.widget');
    var wysiwygLoader = require('web_editor.loader');
    //console.log(publicWidget);
    //console.log(wysiwygLoader);

    //    import Wysiwyg from 'web_editor.wysiwyg';
    //    import { qweb as QWeb, _t } from 'web.core';
    //    var Wysiwyg = require('web_editor.wysiwyg');
    var core = require('web.core');
    var QWeb = core.qweb;
    //    console.log(Wysiwyg);
    //console.log(QWeb);


    publicWidget.registry['public_user_editor_test'] = publicWidget.Widget.extend({
        selector: 'textarea.o_public_user_editor_test_textarea',

        /**
         * @override
         */
        start: async function () {
            await this._super(...arguments);
            await wysiwygLoader.loadFromTextarea(this, this.el, {
                // 1. Habilitamos explícitamente el comando de imagen
                'allowCommandImage': false,
                'allowCommandVideo': false,

                // 2. Deshabilitamos todos los demás comandos comunes
//                'allowCommandFontStyle': false,      // Desactiva negrita, cursiva, subrayado
//                'allowCommandList': false,           // Desactiva listas ordenadas y desordenadas
                'allowCommandLink': false,           // Desactiva la creación de enlaces
//                'allowCommandTable': false,          // Desactiva la creación de tablas
//                'allowCommandViewSource': false,     // Desactiva el botón para ver el código fuente HTML
//                'allowCommandYoutube': false,        // Desactiva la inserción de videos de YouTube
//                'allowCommandCodeView': false,       // Desactiva la vista de código
//                'powerbox': false,

            }).then(wysiwyg => {
                console.log('Editor WYSIWYG cargado solo con imágenes.');
            });
        },
    });
});
