let current_size = 0;
let current_line = 1;
let auto_scroll = false;
let scrolled_to_hash = false;
let query_next = true;
let query_next_status = true;

function scroll_to(index) {
    $('html, body').animate({
        scrollTop: $(index).offset().top
    }, 500);
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
        text = text.substr(text.lastIndexOf('\r') + 1, text.length)
    }
    if (text.lastIndexOf('8') !== -1) {
        text = text.substr(text.lastIndexOf('') + 2, text.length)
    }

    text = text.replace(/\s/g, '&nbsp;');
    let current_element = $("#" + current_line);
    if (current_element.length) {
        text = current_element.html() + text;
        if (text.lastIndexOf('\r') !== -1) {
            text = text.substr(text.lastIndexOf('\r'), text.length)
        }
        if (text.lastIndexOf('8') !== -1) {
            text = text.substr(text.lastIndexOf('') + 2, text.length)
        }
        current_element.html(text);
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
        url: url + current_size,
        dataType: 'json'
    }).done(
        function (data) {
            if (data['query_next'] === false) {
                query_next_status = false;
            }
            current_size = data['current_size'];
            if (data['text'].length > 0) {
                let text = data['text'];
                while (text.includes('\n')) {
                    let line_break = text.indexOf('\n');
                    let line = text.substr(0, line_break);
                    text = text.substr(line_break + 1, text.length);
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
                }
                scrolled_to_hash = true;
            }
            if (query_next_status) {
                setTimeout(refresh_log, 500);
            }
        }
    );
}

function emptyLog() {
    $("#log-body").html("<div class=\"scroll-log\" onclick=\"toggle_auto_scroll()\">Auto-scroll: off</div>");
}

function refresh_status() {
    $.ajax({
        type: 'POST',
        url: window.location.href,
        dataType: 'json'
    }).done(
        function (data) {
            // if (data['query_next'] === false) {
            //     query_next = false;
            // }
            let runtime = data['runtime'].replace("just now", "1 second");
            $("#runtime").html("<i class=\"fe fe-clock\"></i> Ran for " + runtime);
            $("#start_time").html("<i class=\"fe fe-calendar\"></i> " + data['created_at_hr']);

            let build_card_class = "success-card";
            if (data['status'] === 1 || data['status'] === 4) {
                build_card_class = "in-progress-card";
            } else if (data['status'] === 2) {
                build_card_class = "error-card";
            }

            let $buildCard = $("#build_card");
            if (!$buildCard.hasClass(build_card_class)) {
                $buildCard.removeClass("success-card").removeClass("in-progress-card")
                    .removeClass("error-card").addClass(build_card_class);
                if (build_card_class === "in-progress-card") {
                    emptyLog();
                    current_size = 0;
                    current_line = 1;
                    query_next_status = true;
                    refresh_log();
                }
            }
            if (query_next === true) {
                setTimeout(refresh_status, 1000);
            }
        }
    );
}

function restart() {
    $.ajax({
        type: 'GET',
        url: restart_url
    });
}

requirejs(['jquery'], function ($) {
    $(document).ready(
        function () {
            refresh_log();
            refresh_status();
        }
    );
});
