# -*- coding: utf-8 -*-
from openerp import http  # Odoo http
from openerp.http import request  # Odoo http request
from openerp import SUPERUSER_ID  # Odoo superuser id

import os  # system library
import logging  # logging
import json  # json library

_logger = logging.getLogger(__name__)  # initialize logging


class PaperSubmission(http.Controller):
    """
    Controller of the Paper Submission Modules

    Available Routes:
        '/paper_submission/': returns the website
        '/paper_submission/submit/': paper submission data is send to this route
    """
    @http.route('/paper_submission/', auth='public', website='True')
    def index(self, **kw):
        """
        Route is called when opening the paper submission website.
        It retrieves Tracks and Tags from the models and renders the template.
        The rendered template is then returned

        :param kw: submitted request data
        :return: rendered paper submission website
        """

        cr = request.cr
        registry = request.registry
        context = request.context

        orm_track = registry.get('event.track')
        tracks = orm_track.search(cr, SUPERUSER_ID, [], context=context)
        track_names = orm_track.name_get(cr, SUPERUSER_ID, tracks, context=context)

        values = {"tracks": track_names}

        track_objects = orm_track.browse(cr, SUPERUSER_ID, tracks, context=context)

        track_dict = {}
        main_tracks = []

        # get main tracks
        for track in track_objects:

            if track.is_main_track:
                minitracks = []
                main_tracks.append(track.name)

                for minitrack in track_objects:

                    if not minitrack.is_main_track:
                        tags = minitrack.tag_ids
                        tags_json = []
                        #_logger.debug(tags)

                        for tag in tags:

                            if tag.name == track.name:
                                #_logger.debug(minitrack)
                                for tag in tags:
                                    tags_json.append({"name": str(tag.name), "id": tag.id})

                                minitracks.append({"name": str(minitrack.name), "id": minitrack.id, "tags": tags_json})

                track_dict[str(track.name)] = minitracks

        _logger.debug(track_dict)

        values["tracks"] = track_dict
        values["main_tracks"] = main_tracks

        #get available tags
        orm_tag = registry.get('event.track.tag')
        tag_ids = orm_tag.search(cr, SUPERUSER_ID, [], context=context)
        tag_objects = orm_tag.browse(cr, SUPERUSER_ID, tag_ids, context=context)

        tag_json = []

        for tag in tag_objects:
            tag_obj = {"name": str(tag.name), "id": tag.id}
            tag_json.append(json.dumps(tag_obj))

        values["tags"] = tag_json

        # render and return
        return request.website.render('paper_submission.main', values)

    # mandatory values
    mandatory_values = ["title", "abstract", "minitrack", "tag_ids", "document"]

    @http.route('/paper_submission/submit/', auth='user', website='True')
    def paper_submit(self, **post):
        """
        Submitted papers are send to this route.
        The data is then validated and if valid stored in the model.
        Afterwards the '/paper_submission/' route is called

        :param post: submitted request data
        :return: the '/paper_submission/' route
        """

        cr = request.cr
        registry = request.registry
        context = request.context
        uid = request.uid

        error = []

        for value in self.mandatory_values:

            if value in post:
                pass


        # parse request values and store in variables
        if "title" in post:
            title = post["title"]

        if "abstract" in post:
            abstract = post["abstract"]

        submitter_id = uid

        if "minitrack" in post:
            minitrack_id = post["minitrack"]

        if "tag_ids" in post:
            tag_names = post["tag_ids"]
            tag_names = tag_names.split(",")

            orm_tag = registry.get("event.track.tag")

            # get tags from the system
            curr_tag_ids = orm_tag.search(cr, SUPERUSER_ID, [], context=context)
            curr_tag_objects = orm_tag.browse(cr, SUPERUSER_ID, curr_tag_ids, context=context)

            tag_ids = []

            for tag_name in tag_names:

                tag_id = self.get_tag_id(tag_name, curr_tag_objects)

                if tag_id == -1:
                    tag_id = orm_tag.create(cr, SUPERUSER_ID, {"name": tag_name}, context=context)

                tag_ids.append(tag_id)

        if "document" in post:
            document = post["document"]
        else:
            error.append("document")

        if "add_files_file" in post:

            if "add_files_desc" in post:
                additional_file_desc = post["add_files_desc"]
                additional_file_file = post["add_files_file"]
                file_ids = []

                if additional_file_desc != "" and additional_file_file:
                    orm_file = registry.get('paper_submission.file')
                    file_info = {"description": additional_file_desc, "binary": additional_file_file}
                    file_id = orm_file.create(cr, SUPERUSER_ID, file_info, context=context)
                    file_ids.append(file_id)

            else:
                error.append("add_files_desc")

        else:
            file_ids = []

        if "author_count":
            author_count = int(post["author_count"])

        else:
            error.append("author")

        # if there are no errors append insert paper and other model stuff
        if len(error) == 0:

            # document_file_name = "/opt/odoo/my-modules/paper_submission/papers/" + document.filename
            # destination = open(document_file_name, "wb")
            # document.save(destination)

            # add authors
            author_ids = []
            orm_partner = registry.get('res.partner')

            for x in range(1, author_count):
                author_data = post["author"+str(x)]
                author_info = json.loads(author_data)
                author_info["name"] = author_info["first_name"] + " " + author_info["last_name"]

                curr_author_ids = orm_partner.search(cr, SUPERUSER_ID, [], context=context)
                curr_author_objects = orm_partner.browse(cr, SUPERUSER_ID, curr_author_ids, context=context)
                author_id = self.get_author_id(author_info["email"], curr_author_objects)

                if author_id == -1:
                    author_id = orm_partner.create(cr, SUPERUSER_ID, author_info, context=context)

                    # create user:
                    #orm_user = registry.get('res.users')
                    #user_id = orm_user.create(cr, SUPERUSER_ID, {'partner_id': author_id, 'login': author_info["email"]}, context=context)

                author_ids.append(author_id)

            # add paper
            orm_paper = registry.get('paper_submission.paper')

            paper_info = {"title": title, "abstract": abstract, "submitter_id": submitter_id, "minitrack_id": minitrack_id, "tag_ids": [(6, 0, tag_ids)], "author_ids": [(6, 0, author_ids)], "file_ids": [(6, 0, file_ids)], "document": document}
            paper_id = orm_paper.create(cr, SUPERUSER_ID, paper_info, context=context)

            # add paper link to files
            if file_ids:
                file_records = orm_file.browse(cr, SUPERUSER_ID, file_ids, context=context)
                file_records.write({"paper_id": paper_id})

            # add paper link to authors
            authors = orm_partner.browse(cr, SUPERUSER_ID, author_ids, context=context)
            for author in authors:
                author.write({"paper_ids": [(4, paper_id, 0)]})

        return request.redirect("/paper_submission/")

    def write_file_to_directory(self, directory, file_data, file_name):
        """
            write a file "file_data" with the name "file_name" to the specified directory "directory".
        """

        _logger.debug("Writing file " + file_name + " to " + directory)

        # set destination to point to the right file
        path = os.path.join(directory, file_name)

        # if the file already exists, dont overwrite it. return -1
        if os.path.exists(path):
            _logger.error("File: " + file_name + " in " + directory + " allready exists")
            raise IOError

        destination = open(path, 'wb')


        # write the file to the destination
        for chunk in file_data.chunks():
            destination.write(chunk)

        _logger.debug("File: " + file_name + " written successfully to " + directory)

        # return the absolute file path to the file
        return path

    def get_tag_id(self, tag_name, tag_objects):
        """
        Get the id of a tag from its name and a list of tag objects

        :param tag_name: name of the tag
        :param tag_objects: tags object representation
        :return: id of the tag (if not found -1)
        """

        tag_id = -1

        for tag in tag_objects:
            if tag_name == tag["name"]:
                tag_id = tag["id"]

        return tag_id

    def get_author_id(self, author_email, author_objects):
        """
        Get the id of an author from its email and a list of author objects

        :param author_email: email of the author
        :param author_objects: author objects
        :return: id of the author (if not found -1)
        """

        author_id = -1

        for author in author_objects:
            if author_email == author["email"]:
                author_id = author["id"]

        return author_id