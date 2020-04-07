
	const importApp = {

		// Variables
		name : "Import*",
		csrfToken : Cookies.get('csrftoken'),
		modules : [],
		requests : {
			ajax : undefined,
			ajaxFail: function (xhr, status, error){
				// Callback handler that will be called on failure
				console.error( "The following error occurred: "+ xhr.status, error);
			}
		},

		// Functions
		load : function(module){
			module.module_name? importApp.modules.push(module.module_name) : null;
			$.extend(true, importApp, module);
			delete module;
		},
		
		setConfig: function(config, setting){
			importApp[config] = setting;
			return importApp[config];
		},

		debug : function(debug){
			if (debug != "True"){
				var console = {};
				console.log = function(){};
				window.console = console;
			}
			$('#debug-script').remove();
			delete importApp.debug;
		},

		urls : {
			redirect :  function(url, bool=true){
				bool? (window.location.href = window.location.origin + url) : null;
			},
			refresh : function(){
				window.location.href = window.location.href;
			}
		},

		users: {
			check : function(url){
				// Redirect for Fields
				if (importApp.requests.ajax)
					importApp.requests.ajax.abort();

				importApp.requests.ajax =  $.ajax({
					type: 'post',
					url: url,
					data: {'url' : window.location.pathname },
					headers: {'X-CSRFToken': importApp.csrfToken },
					error: importApp.requests.ajaxFail,
					success: function (response, status, xhr){
						importApp.urls.redirect(response.url_redirect, response.field_redirect);
					}
				});
			}
		}

	}

	
	// File Image Check
	function isFileImage(file) {
		return file && file['type'].split('/')[0] === 'image';
	}

	// Drag Box Image
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
		document.querySelector(".addphoto-popper").innerHTML = "Add a photo"
	}

	function hasImage(response, req){

		returnval = ""; 

		if (req == "comment" && response.image){
			returnval =  `<img class="mt-3 d-block comment-image" src="` + response.image +`">`;
		}
		else if (req == "profile"){
			returnval = ( response.user_img? response.user_img : "{% static 'reviewer/images/default_profile.png' %}" );
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
				document.querySelector(".addphoto-popper").innerHTML = "<small>" + files[0].name + "</small>";
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

		try{
			let popperInstance = null;
			const button = document.querySelector('#photo_upload');
			const tooltip = document.querySelector('#addphoto-popper');

			function create() {
				popperInstance = Popper.createPopper(button, tooltip, {
					placement: 'right',
					modifiers: [
						{
							name: 'offset',
							options: {
							  offset: [0, 8],
							},
						}
					],
				});
			}

			function destroy() {
			  if (popperInstance) {
				popperInstance.destroy();
				popperInstance = null;
			  }
			}

			function show() {
			  	tooltip.setAttribute('data-show', '');
			}

			function hide() {
				tooltip.removeAttribute('data-show');
			}

			create();

			const showEvents = ['mouseenter', 'focus'];
			const hideEvents = ['mouseleave', 'blur'];

			showEvents.forEach(event => {
			  button.addEventListener(event, show);
			});

			hideEvents.forEach(event => {
			  button.addEventListener(event, hide);
			});

		}
		catch(err){

		}

		

	}

	function initPhotoDragBox(){

		let targetElements = document.querySelectorAll(".import-image-drag");
		let upphoto_drag = document.querySelectorAll(".import-image-drag-enabled");
		let upphotos = [];

		for (i=0; i<targetElements.length; i++){
			var temphole = targetElements[i].getAttribute("data-file-target");
			upphotos[i] = document.querySelector("."+temphole+ " input[type=file]");	
		}

		$(".import-image-drag-enabled").on("click", "" , function(){
			let targetClassName = $(this).attr("data-file-target");
			let photouploaded = $("."+targetClassName + " a").length;

			if($("." + targetClassName + " input[type=file]").val() == "" && !photouploaded ){
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
				$(this).find(".material-icons").html(
					($("." + targetClassName + " input[type=file]").val() == "")? "add_a_photo" : "close"
				);
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

	function initDragBoxData(clear=false){

		// Get each Drag Box
		var image_drops = document.querySelectorAll(".import-image-drag");
		for (i = 0; i < image_drops.length; i++){
			
			var dragicon = image_drops[i];

			if (clear){
				clearImage(dragicon.getAttribute("data-file-target"),dragicon)
			}
			else{
				//Get Image
				var log = $("." + dragicon.getAttribute("data-file-target") +" input[type=file]").val();
				var pic;

				try{
					if (dragicon.parentElement.querySelector("a").getAttribute("href") != null){
						pic = dragicon.parentElement.querySelector("a").getAttribute("href")
						$(".import-image-drag-enabled").removeClass("dragging");
				
						dragicon.style.backgroundImage = "url("+ pic +")";
						dragicon.querySelector(".material-icons").innerHTML = "close";
						dragicon.querySelector(".material-icons").classList.add("import-image-uploaded-icon");		
						//dragicon.querySelector(".addphoto-popper").innerHTML = "<small>" + pic.split("/").pop() + "</small>";	
						document.querySelector(".addphoto-popper").innerHTML = "<small>" + pic.split("=").pop() + "</small>";
					}
				}
				catch(error){
				}
			}
		}
	}

	// Togglable Icons/Captions
	$("body").on("click", ".togglable" , function(){
		var captexists = ($(this).parent().find(".icaption").length > 0)
		$(this).toggleClass("active-button");

		if (captexists){
			$(this).parent().find(".icaption").toggleClass("active-button");
			var caption = $(this).parent().find(".icaption").html().trim();
		}
		
		var currenthtml = $(this).html().trim();

		var activearray = ['visibility', 'check_box', 'brightness_3', 'notifications_active'];
		var disabledarray = ['visibility_off', 'check_box_outline_blank', 'brightness_5', 'notifications_off'];
		var activecaption = ["Shown", "On"];
		var disabledcaption = ["Hidden", "Off"];

		for (i = 0; i < activearray.length ; i++){
			if (currenthtml == activearray[i])
				$(this).html(disabledarray[i]);
			else if (currenthtml == disabledarray[i])
				$(this).html(activearray[i]);
		}

		if (captexists){
			for (i = 0; i < activecaption.length ; i++){
				if (caption == activecaption[i])
					$(this).parent().find(".icaption").html(disabledcaption[i]);
				else if (caption == disabledcaption[i])
					$(this).parent().find(".icaption").html(activecaption[i]);
			}
		}
	}); 

	function replace_vid_url(content){
		var pattern1 = /(?:http?s?:\/\/)?(?:www\.)?(?:vimeo\.com)\/?(.+)/g;
		var pattern2 = /(?:http?s?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?(.+)/g;
		// var pattern3 = /([-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?(?:jpg|jpeg|gif|png))/gi;

		// var replacement = '<iframe width="420" height="345" src="//player.vimeo.com/video/$1" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>';
		// var new_content = content.replace(pattern1, replacement);

		var new_content = content.replace(pattern2, function(url){

			var newpattern2 = /(?:http?s?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?/g
			url = url.replace(newpattern2, '');

			var hotfix = url.includes('</p>');

			if(hotfix){
				url = url.replace('</p>', '');
			}
			
			var new_url = '<iframe class="mt-2" width="445" height="250" src="https://www.youtube.com/embed/' + url +'"" frameborder="0" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>';

			if (hotfix){
				new_url = new_url +'</p>';
			}

			return new_url;

			});

		return new_content;
	}

	//Hyperlink Support
	function replace_url(content){

		let url_length = 40;
		let linkico = ` <i class="material-icons link-ico my-auto ml-1 ">link</i>`;

		var exp_match = /(\b[^\"](https?|):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
		var element_content=content.replace(exp_match, function(url){

			hotfix = (url.charAt(0) == ">");

			url = url.trim().replace(/>/g, '');
			let urltrim = url;

			if (urltrim.length > url_length)
				urltrim = urltrim.substring(0, url_length) + "..."

			var retval = ` <a class="d-inline-flex import-ex-link" target='_blank' href='` + url +`'>` 
			+ `<img class="ml-1 mr-2 my-auto" src='http://s2.googleusercontent.com/s2/favicons?domain_url=` + url + 
			`'>` + urltrim + linkico + `</a>`;

			if (hotfix)
				retval = ">" + retval;

			return retval;	

		});
		var new_exp_match =/(^|[^\/])(www\.[\S]+(\b|$))/gim;
		var new_content= element_content.replace(new_exp_match, function(url){

			hotfix = false;
			if (url.charAt(0) == ">")
				hotfix = true;

			url = url.trim().replace(/>/g, '');

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
		( $(window).scrollTop() < 15)? 
		$(".import-header").removeClass("import-header-scrolled") :
		$(".import-header").addClass("import-header-scrolled");
	}	

	

	// Final stuff after web Load

	$(document).ready(function(){

		//Initialize
		$('.comment-body').each(function(){
				$(this).html( replace_url( replace_vid_url( $(this).html() ) ) );
		});

		for (let [key, value] of Object.entries(importApp)) {
			typeof value == "function"? Object.defineProperty(importApp, key, { writable: false, configurable: false }) : null
		}

		headerEffect();
		initPhotoDragBox();
	});

	initDragBoxData();

	// Header Scroll

	$(window).scroll(function (event) {
		headerEffect();
	});