
	// AJAX Request Dummy
	var request;

	// File Image Check
	function isFileImage(file) {
	    return file && file['type'].split('/')[0] === 'image';
	}

	// Comment Images

		function clearImage(target, dragicon){
			$("." + target + " input[type=file]").val("");
			try{
				document.querySelector("#id_imagehascleared").setAttribute('checked', 'checked');
			}
			catch(err){
				
			}
			dragicon.querySelector(".material-icons").innerHTML = "add_a_photo";
			dragicon.querySelector(".material-icons").classList.remove("import-image-uploaded-icon");
			dragicon.style.backgroundImage = "";
			dragicon.querySelector(".addphoto-popper").innerHTML = "Add a photo"
		}


		function hasImage(response, req){

			returnval = ""; 

			if (req == "comment"){
				if (response.image)
					returnval =  `<img class="mt-3 d-block comment-image" src="` + response.image +`">`;
			}
			else if (req == "profile"){
				if (response.user_img){
					returnval =  response.user_img;
				}
				else{
					returnval = "{% static 'reviewer/images/default_profile.png' %}";
				}
			}

			return returnval;
		}

		function updateImagePhoto(files, dragicon){
			$(".import-image-drag-enabled").removeClass("dragging");
			let reader = new FileReader();
			
			reader.onload = function(){

				if (isFileImage(files[0])){

					dragicon.style.backgroundImage = "url("+ reader.result +")";
					dragicon.querySelector(".material-icons").innerHTML = "close";
					dragicon.querySelector(".material-icons").classList.add("import-image-uploaded-icon");		
					dragicon.querySelector(".addphoto-popper").innerHTML = "<small>" + files[0].name + "</small>";
					dragicon.querySelector
				}
				else{
					alert("Please upload an image file.");
					clearImage(dragicon.getAttribute("data-file-target"), dragicon);
				}
			}
			reader.readAsDataURL(files[0])
		}


	// Image Button Events

	function PhotoUploadTooltip(){
		// Image button Popup
		try{
			var popper = new Popper($(".import-image-drag"), $(".addphoto-popper"), {
			    placement: 'right',
			    modifiers:{

			    	arrow:{
			    		
			    	}
			    }
			});
		}
		catch(error){

		}
	}

	function initPhotoLoad(){

		let targetElements = document.querySelectorAll(".import-image-drag");
		let upphotos = [];

		for (i=0; i<targetElements.length; i++){
			var temphole = targetElements[i].getAttribute("data-file-target");
			upphotos[i] = document.querySelector("."+temphole+ " input[type=file]");	
		}

		let upphoto_drag = document.querySelectorAll(".import-image-drag-enabled");

		$(".import-image-drag-enabled").on("click", "" , function(){
			let targetClassName = $(this).attr("data-file-target");

			var photouploaded = true;

			if ($("."+targetClassName + " a").length){
				photouploaded = true;
			}
			else{
				photouploaded = false;
			}

			

			if($("." + targetClassName + " input[type=file]").val() == "" && photouploaded == false){
				$("."+targetClassName + " input[type=file]").click();
			}
			else{
				clearImage(targetClassName, this);
			}
		}); 


		function GetAroundEventListenerUpdate(i){
			upphotos[i].addEventListener('change', function(e){
				updateImagePhoto(upphotos[i].files, targetElements[i]);
				document.querySelector("#id_imagehascleared").setAttribute('checked', 'checked');

			});
		}


		for (i = 0; i < upphotos.length; i++){
			GetAroundEventListenerUpdate(i);
		}

		document.addEventListener('dragover', function(e){
			e.preventDefault();
			e.stopPropagation();
			$(".import-image-drag-enabled").addClass("dragging");
			$(".import-image-drag-enabled").find(".material-icons").html("mouse");
		})

		document.addEventListener('dragleave', function(e){
			e.preventDefault();
			e.stopPropagation();
			$(".import-image-drag-enabled").removeClass("dragging");

			$(".import-image-drag").each(function(){
				var targetClassName = $(this).attr("data-file-target");
				if($("." + targetClassName + " input[type=file]").val() == "")
					$(this).find(".material-icons").html("add_a_photo");
				else
					$(this).find(".material-icons").html("close");
			})
		});


		function GetAroundEventListenerDrop(i){
			
			upphoto_drag[i].addEventListener('drop', function(e){
				e.preventDefault();
				e.stopPropagation();


				var temphole = upphoto_drag[i].getAttribute("data-file-target");
				var upphoto = document.querySelector("."+temphole+ " input[type=file]");
				if (isFileImage(e.dataTransfer.files[0])){
					upphoto.files = e.dataTransfer.files
					updateImagePhoto(upphoto.files, upphoto_drag[i]);
				}
			});
		}

		for (i = 0; i < upphoto_drag.length; i++){
			GetAroundEventListenerDrop(i);
		}

		PhotoUploadTooltip();
	}


	$("body").on("click", ".togglable" , function(){
		$(this).toggleClass("active-button");

		var currenthtml = $(this).html().trim();

		if (currenthtml == "visibility"){
			$(this).html("visibility_off")
		}
		else if (currenthtml == "visibility_off"){
			$(this).html("visibility")
		}
		else if (currenthtml == "check_box_outline_blank"){
			$(this).html("check_box")
		}
		else if (currenthtml == "check_box"){
			$(this).html("check_box_outline_blank")
		}

	}); 


	

	//Hyperlink Support
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

	 // Scroll Header
	function headerEffect(){
	 	var scroll = $(window).scrollTop();

	    if (scroll < 15){
	    	$(".import-header").removeClass("import-header-scrolled");
	    }
	    else{
	    	$(".import-header").addClass("import-header-scrolled");
	    }

	}


	function initSection(){
    		

		// Check if there is image TODO

		var image_drops = document.querySelectorAll(".import-image-drag");
		for (i = 0; i < image_drops.length; i++){
			//Get Image
			var log = $("." + image_drops[i].getAttribute("data-file-target") +" input[type=file]").val();

			var dragicon = image_drops[i];						
			var pic;


			try{
				if (image_drops[i].parentElement.querySelector("a").getAttribute("href") != null){

					pic = image_drops[i].parentElement.querySelector("a").getAttribute("href")
					$(".import-image-drag-enabled").removeClass("dragging");
			
					dragicon.style.backgroundImage = "url("+ pic +")";
					dragicon.querySelector(".material-icons").innerHTML = "close";
					dragicon.querySelector(".material-icons").classList.add("import-image-uploaded-icon");		
					dragicon.querySelector(".addphoto-popper").innerHTML = "<small>" + pic.split("/").pop() + "</small>";	
				}
			}
			catch(error){

			}
			
				


			//clearImage(image_drops[i].getAttribute("data-file-target"),image_drops[i])
		}

    }

	$(document).ready(function(){
		//Initialize
	   $('.comment-body').each(function(){

	   		var content = $(this).html();
	   		$(this).html(replace_url(content));

	   });


	   headerEffect();
	   initPhotoLoad();
	   
	});

	$(window).scroll(function (event) {
	   headerEffect();    
	});

	initSection();
	
