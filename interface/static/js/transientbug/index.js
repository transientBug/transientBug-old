// Generated by CoffeeScript 1.5.0
(function() {

  $(function() {
    var tags;
    tags = $.ajax({
      url: "/phots/tags/json",
      async: false
    });
    $('#q').typeahead({
      name: 'tag_search',
      local: tags.responseJSON[0]["tags"],
      limit: 10
    });
    $(".twitter-typeahead").css("display", "block");
    $(".tt-dropdown-menu").css("top", "initial");
    $(".tt-hint").css("padding-top", "1px");
    $("#phot_tags").pillbox({
      url: "/phots/tags/json",
      name: "phot"
    });
    $("#note_tags").pillbox({
      url: "/notes/tags/json",
      name: "note"
    });
    $("#phot_name").check_field({
      url: "/phots/names/json",
      reason: "That name is already in use."
    });
    return $("#quick_phot").check_form();
  });

}).call(this);