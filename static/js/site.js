$(document).ready(function() {
	var party = $('p.party');

	if(party.text()=='Republican'){
		$(party).addClass('republican');
	}else{
		$(party).addClass('democrat');
	}
	

	var vote_result = $('td.vote_result');

	vote_result.each(function(){
		if($(this).text()==='pass'){

			$(this).addClass('vote_pass');
		}else{
			$(this).addClass('vote_fail');
		}
	});
	

	console.log(vote_result.text());

});