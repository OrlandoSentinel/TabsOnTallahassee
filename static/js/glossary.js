function replace() {
  var watch_words = {
    'Senate Bill': 'a thing',
    'Activity': 'an action',
  };
  function span_wrap(text) {
    return ' <span class="glossary" title="' + watch_words[text] + '">' + text + '</span> ';
  }
  var keys = $.map(watch_words, function(element,index) {return index});
  var re = RegExp('\\b(' + keys.join('|') + ')\\b', "g");
  $('div').html(function(i, html) {
    return html.replace(re, span_wrap);
  });
};

$(document).ready(replace);
