# -*- coding: utf-8 -*-
{
    'name': "paper_submission",

    'summary': """
        Paper Submission module including peer review and call for paper configuration""",

    'description': """
        This module provides the full functionality of a paper submission and review system for conferences.
        Including the configuration of call for paper meta data and stylish frontend.
    """,

    'author': "Conf720",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.9',

    # any module necessary for this one to work correctly
    'depends': ['website',
                'website_event_track',
                'base',
                'advanced_tracks'],

    # always loaded
    'data': [
        'views/groups.xml',
        'security/ir.model.access.csv',
        'static/src/xml/paper_submission.xml',
        'views/paper.xml',
        'views/paper_workflow.xml',
        'views/review_workflow.xml',
        'views/additional_file.xml',
        'views/author.xml',
        'views/review.xml',
        'views/menu.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}