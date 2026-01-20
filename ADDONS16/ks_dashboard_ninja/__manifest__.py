# -*- coding: utf-8 -*-
{
	'name': ' Fusion Dashboard Ninja',

	'summary': """
Fusion Dashboard Ninja gives you a wide-angle view of your business that you might have missed. Get smart visual data with interactive and engaging dashboards for your CloudBi Fusion.  Fusion Dashboard, CRM Dashboard, Inventory Dashboard, Sales Dashboard, Account Dashboard, Invoice Dashboard, Revamp Dashboard, Best Dashboard, CloudBI Best Dashboard, CloudBI Apps Dashboard, Best Ninja Dashboard, Analytic Dashboard, Pre-Configured Dashboard, Create Dashboard, Beautiful Dashboard, Customized Robust Dashboard, Predefined Dashboard, Multiple Dashboards, Advance Dashboard, Beautiful Powerful Dashboards, Chart Graphs Table View, All In One Dynamic Dashboard, Accounting Stock Dashboard, Pie Chart Dashboard, Modern Dashboard, Dashboard Studio, Dashboard Builder, Dashboard Designer, CoreAI Studio.  Revamp your Fusion Dashboard like never before! It is one of the best dashboard Fusion apps in the market.
""",

	'description': """
	Advanced AI powered self-service Dahboard for easy analytics
	integrated and compatible with all CloudBI Fusion Core Module
	Including: CRM, Projects, Sales, Purchasing, MRP, HRM, Accounting
	eCommerce and much more.
""",

	'author': 'Eqilibrium Solutions Pty Ltd.',

	'license': 'OPL-1',

	'currency': 'EUR',

	'price': '363',

	'website': 'https://eqilibriumsolutions.com/',

	'maintainer': 'Eqilibrium Solutions Pty Ltd.',

	'live_test_url': 'https://eqilibriumsolutions.com',

	'category': 'Tools',
	'version': '16.0.1.1.0',

	'support': 'sales@eqilibriumsolutions.com',

	'images': ['static/description/dn_v16_optimize.gif'],

	'depends': ['base', 'web', 'base_setup', 'bus'],

	'data': ['security/ir.model.access.csv', 'security/ks_security_groups.xml', 'data/ks_default_data.xml', 'views/ks_dashboard_ninja_view.xml', 'views/ks_dashboard_ninja_item_view.xml', 'views/ks_dashboard_action.xml', 'views/ks_import_dashboard_view.xml', 'wizard/ks_create_dashboard_wiz_view.xml', 'wizard/ks_duplicate_dashboard_wiz_view.xml'],

	'demo': ['demo/ks_dashboard_ninja_demo.xml'],

	'assets': {'web.assets_backend':
				   ['ks_dashboard_ninja/static/src/css/ks_dashboard_ninja.scss',
					'ks_dashboard_ninja/static/src/css/ks_dashboard_ninja_item.css',
					'ks_dashboard_ninja/static/src/css/ks_icon_container_modal.css',
					'ks_dashboard_ninja/static/src/css/ks_dashboard_item_theme.css',
					'ks_dashboard_ninja/static/src/css/ks_dn_filter.css',
					'ks_dashboard_ninja/static/src/css/ks_toggle_icon.css',
					'ks_dashboard_ninja/static/src/css/ks_dashboard_options.css',
					'ks_dashboard_ninja/static/lib/css/Chart.min.css',
					'ks_dashboard_ninja/static/lib/js/Chart.bundle.min.js',
					'ks_dashboard_ninja/static/lib/js/chartjs-plugin-datalabels.js',
					'ks_dashboard_ninja/static/src/js/ks_global_functions.js',
					'ks_dashboard_ninja/static/src/js/ks_dashboard_ninja.js',
					'ks_dashboard_ninja/static/src/js/ks_to_do_dashboard.js',
					'ks_dashboard_ninja/static/src/js/ks_filter_props.js',
					'ks_dashboard_ninja/static/src/js/ks_color_picker.js',
					'ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_item_preview.js',
					'ks_dashboard_ninja/static/src/js/ks_image_basic_widget.js',
					'ks_dashboard_ninja/static/src/js/ks_dashboard_item_theme.js',
					'ks_dashboard_ninja/static/src/js/ks_widget_toggle.js',
					'ks_dashboard_ninja/static/src/js/ks_import_dashboard.js',
					'ks_dashboard_ninja/static/src/js/ks_domain_fix.js',
					'ks_dashboard_ninja/static/src/js/ks_owl_widget.js',
					'ks_dashboard_ninja/static/src/js/owl_image.js',
					'ks_dashboard_ninja/static/src/js/ks_quick_edit_view.js',
					'ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_kpi_preview.js',
					'ks_dashboard_ninja/static/src/js/ks_date_picker.js',
					'ks_dashboard_ninja/static/lib/css/gridstack.min.css',
					'ks_dashboard_ninja/static/lib/js/gridstack-h5.js',
					'ks_dashboard_ninja/static/lib/js/Chart.bundle.min.js',
					'ks_dashboard_ninja/static/src/css/ks_dashboard_ninja_pro.css',
					'ks_dashboard_ninja/static/src/css/ks_to_do_item.css',
					'ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_graph_preview.js',
					'ks_dashboard_ninja/static/src/js/ks_dashboard_ninja_list_view_preview.js',
					'ks_dashboard_ninja/static/src/js/ks_to_do_preview.js',
					'ks_dashboard_ninja/static/src/js/owl_image.js',
					'ks_dashboard_ninja/static/src/js/ks_item_theme.js',
					'ks_dashboard_ninja/static/src/js/ks_dashboard_item_theme_old.js',
					'ks_dashboard_ninja/static/src/xml/owl_template.xml',
					'ks_dashboard_ninja/static/src/xml/**/*',
					],
			   },

	'uninstall_hook': 'uninstall_hook',
}
