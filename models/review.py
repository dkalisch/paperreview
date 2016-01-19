# -*- coding: utf-8 -*-
from openerp import models, fields, api  # Odoo modules
from openerp.exceptions import ValidationError  # Validation Error
import logging  # logging

_logger = logging.getLogger(__name__)  # initialize logger

MAX_SINGLE_GRADING = 5  # max value for the gradings


class Review(models.Model):
    """
    Model class representing the database structure of the review table.

    Attributes:
        _name: name of the model

        titel: title of the review
        reviewer_id: link to the assigned reviews
        interest (int): interest grading
        originality (int): originality grading
        contribution (int): contribution grading
        relevance (int): relevance grading
        theory (int): theory grading
        methodology (int): methodology grading
        presentation (int): presentation grading
        validity (int): validity grading
        references (int): references grading
        comment: comment of the reviewer
        full_review: complete review as text
        paper_id: link to the reviewed paper
        avg_grade: computed value of the average grade
        minitrack_id: automatically added id of the minitrack the reviewed paper is submitted to
        author_ids: automatically added ids of the authors of the the reviewed paper
        state: state variable of the review
    """
    _name = 'paper_submission.review'

    title = fields.Char(default="", string="Title")
    reviewer_id = fields.Many2one('res.users', string='Reviewer', required="True")
    interest = fields.Integer(string="Interest", required="True")
    originality = fields.Integer(string="Originality", required="True")
    contribution = fields.Integer(string="Contribution", required="True")
    relevance = fields.Integer(string="Relevance", required="True")
    theory = fields.Integer(string="Theory", required="True")
    methodology = fields.Integer(string="Methodology", required="True")
    presentation = fields.Integer(string="Presentation", required="True")
    validity = fields.Integer(string="Vailidity", required="True")
    references = fields.Integer(string="References", required="True")
    comment = fields.Text(string='Comment', required="True", default="Enter comment here")
    full_review = fields.Text(string='Full Review', required="True", default="Paste full review here")
    paper_id = fields.Many2one('paper_submission.paper', string='Paper ID', required="True")

    # computed fields:
    avg_grade = fields.Float(string="Average Grading", compute="_compute_avg_grade")
    minitrack_id = fields.Many2one('event.track', string='Paper Minitrack', compute="_compute_minitrack_id")
    author_ids = fields.Many2many('res.partner', string='Authors', compute="_compute_author_ids")

    state = fields.Selection([
        ('draft', "Draft"),
        ('submitted', "Submitted"),
        ('finished', "Finished"),
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
    def action_finish(self):
        """ Change the state to finished """
        self.state = 'finished'

    # --------------------- review constraints ---------------------
    @api.constrains('interest')
    def check_interest_grading_in_range(self):
        """ Check if interest grading is in range, by calling the general grade checking method """
        self._check_grading_in_range(self.interest)

    @api.constrains('originality')
    def check_originality_grading_in_range(self):
        """ Check if originality grading is in range, by calling the general grade checking method """
        self._check_grading_in_range(self.originality)

    @api.constrains('contribution')
    def check_contribution_grading_in_range(self):
        """ Check if contribution grading is in range, by calling the general grade checking method """
        self._check_grading_in_range(self.contribution)

    @api.constrains('relevance')
    def check_relevance_grading_in_range(self):
        """ Check if relevance grading is in range, by calling the general grade checking method """
        self._check_grading_in_range(self.relevance)

    @api.constrains('theory')
    def check_theory_grading_in_range(self):
        """ Check if theory grading is in range, by calling the general grade checking method """
        self._check_grading_in_range(self.theory)

    @api.constrains('methodology')
    def check_methodology_grading_in_range(self):
        """ Check if methodology grading is in range, by calling the general grade checking method """
        self._check_grading_in_range(self.methodology)

    @api.constrains('presentation')
    def check_presentation_grading_in_range(self):
        """ Check if presentation grading is in range, by calling the general grade checking method """
        self._check_grading_in_range(self.presentation)

    @api.constrains('validity')
    def check_validity_grading_in_range(self):
        """ Check if validity grading is in range, by calling the general grade checking method """
        self._check_grading_in_range(self.validity)

    @api.constrains('references')
    def check_references_grading_in_range(self):
        """ Check if references grading is in range, by calling the general grade checking method """
        self._check_grading_in_range(self.references)

    def _check_grading_in_range(self, grading):
        """ General method for checking if a grading is in range of 0 and MAX_SINGLE_GRADING """
        if grading > MAX_SINGLE_GRADING or grading < 0:
            raise ValidationError('A grading can not be higher than 5')

    # --------------------- review computed values ---------------------
    @api.one
    @api.depends('interest', 'originality', 'contribution', 'relevance', 'theory', 'methodology', 'presentation',
                 'validity', 'references')
    def _compute_avg_grade(self):
        """ Computing the average grading by summing up all other grades """
        self.avg_grade = self.interest + self.originality + self.contribution + self.relevance + self.theory + \
                self.methodology + self.presentation + self.validity + self.references

    @api.one
    @api.depends('paper_id', 'minitrack_id')
    def _compute_minitrack_id(self):
        """ Computing the minitrack_id by retrieving if from the linked paper """
        self.minitrack_id = self.paper_id.minitrack_id

    @api.one
    @api.depends('paper_id', 'author_ids')
    def _compute_author_ids(self):
        """ Computing the author_ids by looking them up from the linked paper """
        self.author_ids = self.paper_id.author_ids

    @api.depends('paper_id')
    def _compute_title(self):
        """ Compute the title by retrieving the number of reviews the paper has, plus 'Review' """
        number_of_reviews = len(self.paper_id.review_ids)
        self.title = "Review " + str(number_of_reviews)