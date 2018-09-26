var note = $('#note');

var saveTimer,
    lineHeight = parseInt(note.css('line-height')),
    minHeight = parseInt(note.css('min-height')),
    lastHeight = minHeight,
    newHeight = 0,
    newLines = 0;

var countLinesRegex = new RegExp('\n','g');


note.on('input',function(e){
    // Очистка таймера предотвращает
    // сохранение каждого нажатия клавиш
    if (note.val() != "") {
        clearTimeout(saveTimer);
        saveTimer = setTimeout(ajaxSaveNote, 2000);

        // Подсчет количества новых строк
        newLines = note.val().match(countLinesRegex);

        if(!newLines){
            newLines = [];
        }
        // Увеличиваем высоту заметки (если нужно)
        newHeight = Math.max((newLines.length + 1)*lineHeight, minHeight);
        // Увеличиваем/уменьшаем высоту только один раз при изменеии
        if(newHeight != lastHeight){
            note.height(newHeight);
            lastHeight = newHeight;
        }
    }
}).trigger('input');// Данная строка будет изменять размер заметки при загрузке страницы


function ajaxSaveNote(){
    var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
    var text = note.val();
    var userName = $("#note-block").attr("user");
    if (userName != 'AnonymousUser') {
        $.ajax({
            type: "POST",
            url: "ajax/",
            data: {
                action: 'saveNote',
                text: text,
                userName: userName,
            },
            cache: false,

            success: function (data) {
                console.log('save Note for: ' + userName);
            },

            error: function (request, error) {
                console.log(error + request.status + request.statusText);
            },

            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
        });
    }
}


function ajaxLoadNote(){
    var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
    var userName = $("#note-block").attr("user");
    if (userName != 'AnonymousUser') {
        $.ajax({
            type: "POST",
            url: "ajax/",
            data: {
                action: 'loadNote',
                userName: userName,
            },
            cache: false,

            success: function (data) {
                console.log('load Note for: ' + userName);
                $("#note-block").css("display" , "block");
                note.val(data);
                newLines = note.val().split('\n').length + 1;
                newHeight = Math.max((newLines) * lineHeight, minHeight);
                note.height(newHeight);
            },

            error: function (request, error) {
                console.log(error + request.status + request.statusText);
            },

            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
        });
    } else {

    }
};


$(document).ready(function() {
    ajaxLoadNote();
});


$("#note-link").click(function () {
    if ($("#pad").css("display") != "block") {
        $("#note-link").html("<i class='fas fa-times'></i>");
    } else {
        $("#note-link").html("<i class='fas fa-pencil-alt'></i>");
    }
    $("#pad").toggle();
});