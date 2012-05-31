google.load("visualization", "1", {packages:["corechart"]});

function draw_chart(data) {
	var content = google.visualization.arrayToDataTable(data);
	var chart = new google.visualization.LineChart(document.getElementById("chart_div"));
	chart.draw(content, 
	{
		'title': '',
		'legend': 'none',
		'series': [ {'color': '#1c1c1b'} ]
	});
}

function fetch_data() {
	$.get("/data", {}, function(data) {
		draw_chart(data.data);
	});
}

function load_page(page) {
	$.get("/page/" + page, {}, function(data) {
		$(".bet:last").after(data);
	});
}

$(window).scroll(function(){
	if  ($(window).scrollTop() == $(document).height() - $(window).height()){
	   load_page(--page);
	}
});