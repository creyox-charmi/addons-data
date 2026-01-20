odoo.define('cr_website_blog_customisation.cr_random_blogs', function (require) {
'use strict';

const publicWidget = require('web.public.widget');

const BlogWidget = publicWidget.Widget.extend({
    selector: '.cr_random_blogs',

    init: function () {
        this._super.apply(this, arguments);
    },

    willStart: function () {
    let url = window.location.href;
    let parts = url.split('-');  // Split by '-'
    let lastPart = parts[parts.length - 1]; // Get the last part
    console.log(lastPart);
        return fetch(`/blog/random?id=${lastPart}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        })
        .then(response => response.json())
        .then(data => {
            this.blogData = data;
        })
        .catch(error => {
            this.blogData = [];
        });
    },

    start: function () {
        const refEl = this.$el.find("#random-blogs");

        if (refEl.length === 0) return;

        if (this.blogData && this.blogData.length > 0) {
            let html = this._generateHTML();
            refEl.html(html);
            const dataset = this.el.dataset;
        } else {
            console.log("No client data available.");
        }
        return this._super(...arguments);
    },

    _generateHTML: function () {
    let html = '';
        this.blogData.forEach(blog => {
            html += `
            <a class="cr-related-blog" href="${blog.url}" style="background-color:${blog.background_color}">
                            <h3>${blog.title}</h3>
                            <p class="cr-author">${blog.author_name}</p>
            </a>`;
        });
        return html;
    },


});

publicWidget.registry.randomblogs = BlogWidget;

return BlogWidget;
});


