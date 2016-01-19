# -*- coding: utf-8 -*-
from openerp import models, fields, api  # odoo modules
from openerp.exceptions import ValidationError  # ValidationError
import magic  # file type guesser
import binascii  # ascii converter
import logging  # logging

_logger = logging.getLogger(__name__) # initialize logger


class Paper(models.Model):
    """
    Model class representing the database structure of the paper table.

    Attributes:
        _name: name of the model
        _rec_name: name that is shown in views

        title: title of the paper as char field
        submitter_id: link to the user, who submitted the paper
        author_ids: links to the authors (res.partner)
        minitrack_id: link to the minitrack
        abstract: abstract of the paper
        tag_ids: links to tags
        best_paper: flag if the paper is nominated as best paper
        review_ids: links to the reviews
        file_ids: links to the additional files submitted
        document: binary representation of the submission
        document_filename: computed file name of the document
        state: state of the paper
    """
    _name = 'paper_submission.paper'
    _rec_name = "title"

    title = fields.Char(string='Title', required='True')
    submitter_id = fields.Many2one('res.users', string="Submitter", required="True", default="uid")
    author_ids = fields.Many2many('res.partner', string='Authors', relation="paper_submission_paper_author_relation")
    minitrack_id = fields.Many2one('event.track', string='Minitrack', required="True")
    abstract = fields.Text(string='Abstract')
    tag_ids = fields.Many2many('event.track.tag', string='Tags')
    accepted = fields.Boolean(string="Accepted")
    best_paper = fields.Boolean(string="Best Paper")
    review_ids = fields.One2many('paper_submission.review', 'paper_id', string='Reviews')
    file_ids = fields.One2many('paper_submission.file', 'paper_id', string='Additional Files')
    document = fields.Binary(string="Document")
    document_filename = fields.Char(string="Document File Name", compute="_get_document_filename")

    state = fields.Selection([
        ('draft', "Draft"),
        ('submitted', "Submitted"),
        ('in_review', "In Review"),
        ('reviewed', "Reviewed"),
        ('accepted', "Accepted"),
    ])

    # --------------------- workflow state change actions ---------------------
    @api.one
    def action_draft(self):
        """ Change the state to draft """
        self.state = 'draft'

    @api.one
    def action_submit(self):
        """ Change the state to submitted """
        self.state = 'submitted'

    @api.one
    def action_in_review(self):
        """ Change the state to in_review """
        self.state = 'in_review'

    @api.one
    def action_reviewed(self):
        """ Change the state to reviewed """
        self.state = 'reviewed'

    @api.one
    def action_accepted(self):
        """ Change the state to accepted """
        self.state = 'accepted'

    # --------------------- accepting buttons actions ---------------------
    @api.one
    def reject_paper(self):
        """ Rejecting the paper, setting accepted to False and the state to accepted """
        self.accepted = False
        self.state = 'accepted'


    @api.one
    def accept_paper(self):
        """ Accepting the paper, setting accepted to True and the state to accepted """
        self.accepted = True
        self.state = 'accepted'

    @api.one
    def accept_paper_and_nominate(self):
        """
        Accepting the paper, setting accepted to True and the state to accepted.
        Additionally nominate it as best paper and set best_paper to True
        """
        self.accepted = True
        self.best_paper = True
        self.state = 'accepted'

    # --------------------- paper constraints ---------------------
    @api.constrains('best_paper')
    def check_best_paper(self):
        """
        Check that a rejected paper is not nominated as best paper
        :return: can raise ValidationError
        """
        if self.best_paper and not self.accepted:
            raise ValidationError('A paper can not be a best paper when its not accepted')

    @api.constrains('accepted')
    def check_best_paper(self):
        """
        Check that a best paper is not rejected
        :return: can raise ValidationError
        """
        if self.best_paper and not self.accepted:
            raise ValidationError('A best paper can not be rejected')

    @api.constrains('document')
    def check_document_is_pdf(self):
        """
        Check if a uploaded document is of the file type pdf.
        :return: can raise ValidationError
        """
        document_class = self.document.__class__.__name__

        if document_class == "str":
            # file is uploaded from frontend and checked for pdf there
            file_type = "application/pdf"
        else:
            # file is uploaded from backend
            try:
                doc = binascii.a2b_base64(self.document)
                file_type = magic.from_buffer(doc, mime=True)
            except:
                file_type = "xy"

        if file_type != "application/pdf":
                raise ValidationError('Document must be of file type pdf')

    # --------------------- computed values ---------------------
    @api.depends('title')
    def _get_document_filename(self):
        """ Compute the file name of the document from the paper title """
        self.document_filename = self.title + ".pdf"

    # --------------------- further methods ---------------------
    @api.one
    def open_review_popup(self, cr, uid, ids, context=None):
        """
        Opens a pop-up, when clicking on the "Assign reviews..." button

        :param cr: database cursor
        :param uid: user id
        :param ids: record ids
        :param context: context
        :return: pop-up view
        """
        _logger.info("OPEN POPUP")

        if context is None:
            context = {}


        sale_ids = self.pool.get('sale.order').search(cr, uid,
                                                      [('project_id', '=',
                                                        context.get('search_default_project_id', False)),
                                                       ('partner_id', 'in',
                                                        context.get('search_default_partner_id', False))])

        names = [record.name for record in self.browse(cr, uid, ids, context=context)]

        name = ('Sales Order Lines of %s') % ','.join(names)

        return {

            'type': 'ir.actions.act_window',

            'name': name,

            'view_type': 'form',

            'view_mode': 'tree,form',

            'context': context,

            'domain': [('order_id', 'in', sale_ids)],

            'res_model': 'sale.order.line',

            'nodestroy': True,

        }


class File(models.Model):
    """
    Representation of a additional file in the database.

    Attributes:
        _name: name of the model

        paper_id: link to the paper the file belongs to
        description: description of the file
        category: category the file belongs to as char (e.g. Source Code)
        file_name: name of the file
    """
    _name = 'paper_submission.file'

    paper_id = fields.Many2one('paper_submission.paper', 'Paper')
    description = fields.Char('Description', required="True")
    category = fields.Char('Category')
    binary = fields.Binary(string="Binary", required="True")
    file_name = fields.Char()


class TrackPaperExtension(models.Model):
    """
    Extension of the Track model, adding the submitted papers.
    Inherits from the event.track model.

    Attribute:
        _name: name of the model (the same value as _inherit)
        _inherit: name of the inheriting model

        paper_ids: link to the submitted papers
    """
    _name = "event.track"
    _inherit = "event.track"

    paper_ids = fields.One2many('paper_submission.paper', 'minitrack_id', string="Submitted Papers")


class UserSubmitterExtension(models.Model):
    """
    Extension of the User model, adding submitted papers.

    Attributes:
        _name: name of the model (the same value as _inherit)
        _inherit: name of the inheriting model

        submitted_paper_ids: link to the submitted papers
    """
    _name = "res.users"
    _inherit = "res.users"

    submitted_paper_ids = fields.One2many('paper_submission.paper', 'submitter_id', string="Submitted Papers")


class UserReviewerExtension(models.Model):
    """
    Extension of the User model, adding assigned reviews.

    Attributes:
        _name: name of the model (the same value as _inherit)
        _inherit: name of the inheriting model

        assigned_reviews_ids: link to the assigned reviews
    """
    _name = "res.users"
    _inherit = "res.users"

    assigned_review_ids = fields.One2many('paper_submission.review', 'reviewer_id', string="Assigned Reviews")