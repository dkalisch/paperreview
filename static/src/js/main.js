jQuery(document).ready(function ($) {
    /*
    Document ready function, called at the beginning.
    Retrieving values and setting up the dynamic fields.
     */

    //disable sending form with enter
    $('#form').on('keyup keypress', function(e) {
      var code = e.keyCode || e.which;
      if (code == 13) {
        e.preventDefault();
        return false;
      }
    });

    //build tag selector
    var tag_data = $("#tag-data").val();
    var formatted_tag_data = tag_data.replace(/'/g,"");
    //console.log(JSON.parse(formatted_tag_data));
    var tag_json = JSON.parse(formatted_tag_data);
    var tag_names = [];
    console.log(tag_json);

    var tags_selector = $("#tags-selector");

    for(var i = 0; i < tag_json.length; i++){
        tag_names.push(tag_json[i]["name"]);
    }

    console.log(tag_names);

    var tag_names_bloodhound = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.whitespace,
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      // `states` is an array of state names defined in "The Basics"
      local: tag_json
    });
    tag_names_bloodhound.initialize();

    tags_selector.tagsinput({
      typeaheadjs: {
        name: 'tag_names_bloodhound',
        displayKey: 'name',
        valueKey: 'name',
        source: tag_names_bloodhound.ttAdapter()
      }
    });

    // add test to select file
    $('.btn-file :file').on('fileselect', function(event, numFiles, label) {
            console.log(numFiles);
            console.log(label);
    });
});

$(document).on('change', '.btn-file :file', function() {
    /*
    Called when the file button is clicked and a file is selected
     */
    console.log("bäm");

    var input = $(this);

    console.log(input);

    var numFiles = input.get(0).files ? input.get(0).files.length : 1;

    var label = input.val().replace(/\\/g, '/').replace(/.*\//, '');

    input.trigger('fileselect', [numFiles, label]);
});


var author_cnt = 1;

function trackChange(tracks, value) {
    /*
    Called when a track is selected from the dropdown
    */

    var select = document.getElementById("select-minitrack");

    var minitracks = tracks[value];

    //remove current options
    while(select.firstChild){
        select.removeChild(select.firstChild);
    }

    //add fitting minitracks
    for(var i = 0; i < minitracks.length; i++){

        var option = document.createElement("option");
        option.setAttribute("value", minitracks[i].id);

        var text = document.createTextNode(minitracks[i].name);
        option.appendChild(text);
        select.appendChild(option);
    }
}

function saveAuthor(){
    /*
    Called when an author was enterd in the modal
     */

    //create html elements
    var div_auth = document.getElementById("author-input-group");
    var div_auth_childs = div_auth.children;

    var id = document.getElementById("author_id");
    var author_id = id.value;

    console.log(div_auth_childs);

    //input for storing short displayed author information
    var new_input = document.createElement("input");

    for(var i = 0; i < div_auth_childs.length; i++){
        child = div_auth_childs[i];
        if(child.tagName.toLowerCase() == "input"){
            var name = child.getAttribute("name");
            var value = child.value;

            if(name == "author_firstname"){
                var first_name = value;
            }
            else if (name == "author_lastname"){
                var last_name = value;
            }
            else if (name == "author_email"){
                var email = value;
            }
            else if (name == "author_affiliation"){
                var affiliation = value;
            }

            //clean up
            child.value = "";
        }
    }

    if(author_id == "") {
        // if there is no existing author create everything from scratch
        new_input.setAttribute("class", "form-control author-input col-md-10 author-modal-trigger");
        new_input.setAttribute("style", "margin-bottom:5px");
        new_input.setAttribute("data-id", author_cnt);
        new_input.setAttribute("id", "input_author"+author_cnt);

        $(new_input).click(function () {
            // called when the form input field that stored the information is clicked, opens modal
            console.log("hello I was clicked");

            var hidden_input = $("#input_hidden_author" + $(this).data('id'));
            var author_values = JSON.parse(hidden_input.val());
            console.log(hidden_input);
            console.log(author_values);

            $("#author-firstname").val(author_values.first_name);
            console.log($("#author-firstname"));
            console.log(author_values.first_name);
            $("#author-lastname").val(author_values.last_name);
            $("#author-email").val(author_values.email);
            $("#author-affiliation").val(author_values.affiliation);

            var author_id = $('#author_id');
            console.log(author_id);
            console.log($(this).data('id'));
            $('#author_id').val($(this).data('id'));
            $('#authorModal').modal('show');
        });

        //add shortened author information to input field
        new_input.value = last_name + ", " + first_name + " - " + affiliation + " (" + email + ")";

        var form_div_author = document.getElementById("authors");
        form_div_author.insertBefore(new_input, document.getElementById("author-modal-trigger"));

        // build author json info and add to hidden input, for sending to the server
        var author_info = {
            "last_name": last_name,
            "first_name": first_name,
            "email": email,
            "affiliation": affiliation
        };
        var new_hidden_input = document.createElement("input");
        new_hidden_input.setAttribute("type", "hidden");
        new_hidden_input.setAttribute("id", "input_hidden_author" + author_cnt);
        new_hidden_input.setAttribute("name", "author" + author_cnt);
        new_hidden_input.value = JSON.stringify(author_info);

        form_div_author.appendChild(new_hidden_input);
        author_cnt++;
        $("#author_count").val(author_cnt);

        $("#author-modal-trigger").attr("required","");
        $("#author-modal-trigger").attr("readonly","readonly");

        if(author_cnt > 5){
            // if there are already 5 authors deny author
            console.log("too high");
            $("#author-modal-trigger").attr("disabled","disabled");
            $("#author-modal-trigger").attr("data-toggle","");
            $("#author-modal-trigger").attr("data-target","");
            $("#author-modal-trigger").val("Maximum number of authors reached.");
        }
    }
    else {
        //add new author to existing ones
        $("#input_author"+author_id).val(last_name + ", " + first_name + " - " + affiliation + " (" + email + ")");

        $("#input_hidden_author"+author_id).val(JSON.stringify({
            "last_name": last_name,
            "first_name": first_name,
            "email": email,
            "affiliation": affiliation
        }));
    }

    //clear input field
    $("#author_id").val("");
}
