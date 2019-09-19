
	
	
	 function replace_url(content){

	  	   let url_length = 40;

	  	   let linkico = ` <i class="material-icons link-ico my-auto ml-1 ">link</i>`;

		   var exp_match = /(\b(https?|):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
		   var element_content=content.replace(exp_match, function(url){

		   		url = url.trim()

		   		let urltrim = url;

		   		if (urltrim.length > url_length)
		   			urltrim = urltrim.substring(0, url_length) + "..."

		   		return ` <a class="d-inline-flex import-ex-link" target='_blank' href='` + url +`'>` 
		   		+ `<img class="ml-1 mr-2 my-auto" src='http://s2.googleusercontent.com/s2/favicons?domain_url=` + url + 
		   		`'>` + urltrim + linkico + `</a>` 

		   });
		   var new_exp_match =/(^|[^\/])(www\.[\S]+(\b|$))/gim;
		   var new_content= element_content.replace(new_exp_match, function(url){

		   		hotfix = false;
		   		if (url.charAt(0) == ">")
		   			hotfix = true;

		   		url = url.trim();
		   		url = url.replace(/>/g, '');

		   		let urltrim = url;

		   		if (urltrim.length > url_length)
		   			urltrim = urltrim.substring(0, url_length) + "..."

		   		url = "http://" + url;

		   		retval =  `<a class="d-inline-flex import-ex-link" target="_blank" href="` + url +`">` 
		   		+ `<img class="ml-1 mr-2 my-auto" src='http://s2.googleusercontent.com/s2/favicons?domain_url=` + url + 
		   		`'>` + urltrim + linkico + `</a>`;

		   		if (hotfix)
		   			retval = ">" + retval;

		   		return retval;

		   });
		   return new_content;
	 }

	function headerEffect(){
	 	var scroll = $(window).scrollTop();

	    if (scroll < 15){
	    	$(".import-header").removeClass("import-header-scrolled");
	    }
	    else{
	    	$(".import-header").addClass("import-header-scrolled");
	    }

	}

	$(document).ready(function(){

	   $('.comment-body').each(function(){

	   		var content = $(this).html();
	   		$(this).html(replace_url(content));

	   });

	   headerEffect;
	   
	});

	$(window).scroll(function (event) {
	   headerEffect();
	    
	});
	
