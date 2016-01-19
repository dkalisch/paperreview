# -*- coding: utf-8 -*-
from openerp import models, fields, api #openerp modules


class Author(models.Model):
    """
    Model class representing the database structure of the author table.
    Inherits from the res.partner class.

    Attributes:
        affiliation: Char field containing the author's affiliation
        paper_ids: Many2many link to a paper record
    """
    _inherit = 'res.partner'

    affiliation = fields.Char()
    paper_ids = fields.Many2many('paper_submission.paper', string='Authored Papers',
                                 relation="paper_submission_paper_author_relation")