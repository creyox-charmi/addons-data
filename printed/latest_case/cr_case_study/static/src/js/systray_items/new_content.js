///** @odoo-module **/
//
//import { NewContentModal, MODULE_STATUS } from '@website/js/systray_items/new_content';
//import { patch } from 'web.utils';
//
//patch(NewContentModal.prototype, 'website_blog_new_content', {
//    setup() {
//        this._super();
//        console.log('in setup...')
//        const newCaseStudyElement = this.state.newContentElements.find(element => element.moduleXmlId === 'cr_case_study.module_cr_case_study');
//        newCaseStudyElement.createNewContent = () => this.onAddContent('cr_case_study.case_study_action_add', true);
//        newCaseStudyElement.status = MODULE_STATUS.INSTALLED;
//        newCaseStudyElement.model = 'case.study';
//    },
//});
