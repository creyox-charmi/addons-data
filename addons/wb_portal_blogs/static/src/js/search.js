/** @odoo-module **/

import { onMounted } from "@odoo/owl";
import Tagify from '@yaireo/tagify';
console.log('45612354')
onMounted(() => {
    const input = document.querySelector('.tag-input');
    console.log('dvdgdhdbdjjd')
    if (input && !input.classList.contains('tagify-loaded')) {
        const tagify = new Tagify(input, {
            delimiters: ", ",   // split tags by comma or space
            originalInputValueFormat: valuesArr => valuesArr.map(item => item.value).join(" ")
        });
        input.classList.add('tagify-loaded');
    }
});
