$(function() {
    $('#side-menu').metisMenu();
});

//Loads the correct sidebar on window load,
//collapses the sidebar on window resize.
// Sets the min-height of #page-wrapper to window size
$(function() {
    $(window).bind("load resize", function() {
        var topOffset = 50;
        var width = (this.window.innerWidth > 0) ? this.window.innerWidth : this.screen.width;
        if (width < 768) {
            $('div.navbar-collapse').addClass('collapse');
            topOffset = 100; // 2-row-menu
        } else {
            $('div.navbar-collapse').removeClass('collapse');
        }

        var height = ((this.window.innerHeight > 0) ? this.window.innerHeight : this.screen.height) - 1;
        height = height - topOffset;
        if (height < 1) height = 1;
        if (height > topOffset) {
            $("#page-wrapper").css("min-height", (height) + "px");
        }
    });

    var url = window.location;
    // var element = $('ul.nav a').filter(function() {
    //     return this.href == url;
    // }).addClass('active').parent().parent().addClass('in').parent();
    var element = $('ul.nav a').filter(function() {
        return this.href === url;
    }).addClass('active').parent();

    while (true) {
        if (element.is('li')) {
            element = element.parent().addClass('in').parent();
        } else {
            break;
        }
    }
});

$("#synset-search").keyup(function(event) {
    if (event.keyCode === 13) {
        location.href = '/synsets?gq='+$('#synset-search').val();
    }
});

var user_activity_now = function(date){

       var u = $("#user-activity-today").attr("user-data");
       $("#user-activity-today").empty();

       var url = '';
       if( date !== '') {
           url = '/api/users/activity/date/'+date;
           $("#chart-activity-name").text('Users Activity '+ date );
       } else {
           url = '/api/users/activity/now';
           $("#chart-activity-name").text('Today\'s Users Activity');
       }
       if (u !== ''){
           url=url+"?q="+u;
       }
       return $.ajax({
        type: 'GET',
        url: url,
        dataType: "json",
        async: true,
        contentType: "application/json; charset=utf-8",
        beforeSend: function() {
            $("#no-user-activity").hide();
            $("#d_ylabel-axis").hide();
            $("#d_xlabel-axis").hide();
            $("#user-activity-today-spinner").show();
        },
        success: function(json){
           $("#user-activity-today-spinner").hide();
           if(json.ykeys.length > 0) {
                $("#no-user-activity").hide();
                draw_linear_graph(json);
                $("#d_ylabel-axis").show();
                $("#d_xlabel-axis").show();
           } else {
                $("#no-user-activity").show();
                $("#d_ylabel-axis").hide();
                $("#d_xlabel-axis").hide();
           }
        }
    })
};

var user_activity_yesterday = function(){
     var previousDay =  moment(new Date()).add(-1, 'days').format("YYYY-MM-DD").toString();
     user_activity_now(previousDay);
     $("#chart-activity-name").text('Users Activity Yesterday');
};

var user_activity_by_date = function(){
     let d = $("#activity_date").val();
     user_activity_now(d);
};

var user_activity_monthly = function(){
       var u = $("#user-activity-monthly").attr("user-data");
       var url = '/api/users/activity/monthly';
       if (u !== ''){
           url=url+"?q="+u;
       }
       return $.ajax({
        type: 'GET',
        url: url,
        dataType: "json",
        async: true,
        contentType: "application/json; charset=utf-8",
        beforeSend: function() {
            $("#m_no-user-activity").hide();
            $("#m_ylabel-axis").hide();
            $("#m_xlabel-axis").hide();
            $("#m_user-activity-monthly-spinner").show();
        },
        success: function(json){
           $("#user-activity-monthly-spinner").hide();
           if(json.ykeys.length > 0) {
                $("#m_no-user-activity").hide();
                draw_linear_graph(json);
                $("#m_ylabel-axis").show();
                $("#m_xlabel-axis").show();

           } else {
                $("#m_no-user-activity").show();
                $("#m_ylabel-axis").hide();
                $("#m_xlabel-axis").hide();
           }
        }
    })
};

var draw_linear_graph = function(json){
   conf=json;
   conf.parseTime =false;
   Morris.Line(conf);
};

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
    $('#date_from').datetimepicker({
        format: 'YYYY-MM-DD'
    });
    $('#date_to').datetimepicker({
        format: 'YYYY-MM-DD'
    });
    $('#activity_date').datetimepicker({
        format: 'YYYY-MM-DD'
    });
});
