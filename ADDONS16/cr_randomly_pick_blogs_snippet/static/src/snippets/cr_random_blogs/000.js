odoo.define('cr_randomly_pick_blogs_snippet.cr_random_blogs', function (require) {
'use strict';

const publicWidget = require('web.public.widget');

const BlogWidget = publicWidget.Widget.extend({
    selector: '.cr_random_blogs',

    init: function () {
        this._super.apply(this, arguments);
    },

    willStart: function () {
        return fetch('/blog/random', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        })
        .then(response => response.json())
        .then(data => {
            console.log("data : ",data)
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


