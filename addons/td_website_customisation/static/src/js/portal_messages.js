odoo.define('td_website_customisation.portal_messages', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var rpc = require('web.rpc');
var core = require('web.core');

var PortalMessagesWidget = publicWidget.Widget.extend({
    selector: '.container.my-4',
    events: {
        'click .reply-btn': '_onReplyClick',
        'click #sendMessage': '_onSendMessage',
        'click #cancelReply': '_onCancelReply',
    },

    start: function () {
        this._super.apply(this, arguments);
        this._scrollToBottom();
        return Promise.resolve();
    },

    _onReplyClick: function (ev) {
        ev.preventDefault();
        var $btn = $(ev.currentTarget);
        var messageId = $btn.data('message-id');
        var blogId = $btn.data('blog-id');
        var authorName = $btn.data('author-name');

        var $messageDiv = $('.message-item[data-message-id="' + messageId + '"]');
        var $messageBody = $messageDiv.find('.message-body[data-message-id="' + messageId + '"]');

        var $clonedBody = $messageBody.clone();
        $clonedBody.find('img').each(function() {
            $(this).replaceWith('[Imagen]');
        });

        var messageBodyHtml = $clonedBody.html();

        $('#replyToName').text(authorName);
        $('#replyToPreview').html(messageBodyHtml);
        $('#replyIndicator').removeClass('d-none');
        $('#parentMessageId').val(messageId);
        $('#replyBlogId').val(blogId);

        $('#messageText').focus();
        $('html, body').animate({
            scrollTop: $('#messageText').offset().top - 100
        }, 500);
    },

    _onCancelReply: function (ev) {
        ev.preventDefault();
        this._resetReplyForm();
    },

    _onSendMessage: function (ev) {
        ev.preventDefault();
        var self = this;
        var body = $('#messageText').val().trim();
        var parentMessageId = $('#parentMessageId').val();
        var replyBlogId = $('#replyBlogId').val();
        var otherPartnerId = $('#otherPartnerId').val();
        var myBlogPostId = $('#myBlogPostId').val();
        var otherBlogPostId = $('#otherBlogPostId').val();
        var parentBody = $('#replyToPreview').html();

        if (!body) {
            this._showAlert('Por favor escribe un mensaje', 'warning');
            return;
        }

        var blogPostId = replyBlogId || myBlogPostId || otherBlogPostId;

        if (!blogPostId) {
            this._showAlert('No se pudo determinar el blog para el mensaje', 'danger');
            return;
        }

        $('#sendMessage').prop('disabled', true).html('<i class="fa fa-spinner fa-spin me-1"></i>Enviando...');

        rpc.query({
            route: '/my/messages/send',
            params: {
                body: body,
                parent_message_id: (parentMessageId && parentMessageId !== '') ? parentMessageId : false,
                blog_post_id: blogPostId,
                other_partner_id: parseInt(otherPartnerId),
                parent_body: (parentMessageId && parentMessageId !== '') ? parentBody : false
            }
        }).then(function (result) {
            if (result.success) {
                window.location.reload();
            } else {
                self._showAlert(result.error || 'Error al enviar el mensaje', 'danger');
                $('#sendMessage').prop('disabled', false).html('<i class="fa fa-send me-1"></i>Enviar Mensaje');
            }
        }).catch(function (error) {
            console.error('Error sending message:', error);
            self._showAlert('Error al enviar el mensaje. Por favor intenta de nuevo.', 'danger');
            $('#sendMessage').prop('disabled', false).html('<i class="fa fa-send me-1"></i>Enviar Mensaje');
        });
    },

    _resetReplyForm: function () {
        $('#replyIndicator').addClass('d-none');
        $('#parentMessageId').val('');
        $('#replyBlogId').val('');
        $('#replyToName').text('');
        $('#replyToPreview').text('');
    },

    _scrollToBottom: function () {
        var container = $('#messageContainer');
        if (container.length) {
            setTimeout(function() {
                container.scrollTop(container[0].scrollHeight);
            }, 100);
        }
    },

    _showAlert: function (message, type) {
        var alertHtml = '<div class="alert alert-' + type + ' alert-dismissible fade show" role="alert">' +
                        message +
                        '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>' +
                        '</div>';
        $('.card-footer').prepend(alertHtml);

        setTimeout(function() {
            $('.alert').fadeOut('slow', function() {
                $(this).remove();
            });
        }, 5000);
    }
});

publicWidget.registry.portalMessages = PortalMessagesWidget;

return PortalMessagesWidget;
});