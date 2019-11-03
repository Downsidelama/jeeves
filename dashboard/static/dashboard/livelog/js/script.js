let current_size = 0;
let current_line = 1;
let auto_scroll = false;
let scrolled_to_hash = false;

function query_next() {
    // Evaluate whether the queries should continue or not.
    return false;
}

function scroll_to(index) {
    $('html, body').animate({
        scrollTop: $(index).offset().top
    }, 1000);
}

function scroll_to_last_line() {
    scroll_to("#" + (current_line - 1));
}

function toggle_auto_scroll(value = null) {
    if (value === true || value === false) {
        auto_scroll = value;
    } else {
        auto_scroll = !auto_scroll;
    }
    if (auto_scroll) {
        $(".scroll-log").html("Auto-scroll: on");
        scroll_to_last_line()
    } else {
        $(".scroll-log").html("Auto-scroll: off");
    }
}

function add_to_element(text) {
    if (text.lastIndexOf('\r') !== -1) {
        text = text.substr(text.lastIndexOf('\r'), text.length)
    }
    if (text.lastIndexOf('') !== -1) {
        text = text.substr(text.lastIndexOf(''), text.length)
    }

    text = text.replace(/\s/g, '&nbsp;');
    let current_element = $("#" + current_line);
    if (current_element.length) {
        current_element.html(current_element.html() + text);
    } else {
        $("#log-body").append(
            "        <div class=\"log-line\">\n" +
            "            <a href=\"#" + current_line + "\">" + current_line + "</a>\n" +
            "            <span id=\"" + current_line + "\">" + text + "</span>\n" +
            "        </div>"
        );
    }
}

function refresh_log() {
    $.ajax({
        type: 'GET',
        url: '/livelog/28b23758-69e5-433a-a70b-2453879c35c8/' + current_size,
        dataType: 'json'
    }).done(
        function (data) {
            current_size = data['current_size'];
            if (data['text'].length > 0) {
                let text = data['text'];
                while (text.includes('\r\n')) {
                    let line_break = text.indexOf('\r\n');
                    let line = text.substr(0, line_break);
                    text = text.substr(line_break + 2, text.length);
                    add_to_element(line);
                    current_line++;
                }

                if (text !== "") {
                    add_to_element(text);
                }

                if (auto_scroll && scrolled_to_hash) {
                    scroll_to_last_line();
                }

                if (window.location.hash && !scrolled_to_hash) {
                    scroll_to(window.location.hash);
                    scrolled_to_hash = true;
                }
            }
            if (query_next()) {
                setTimeout(refresh_log, 1000);
            }
        }
    );
}

requirejs(['jquery'], function ($) {
    $(document).ready(
        function () {
            setTimeout(refresh_log, 1000);
        }
    );
});
