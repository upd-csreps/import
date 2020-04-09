
	const importApp = {

		// Variables
		name : "Import*",
		csrfToken : Cookies.get('csrftoken'),
		modules : [],
		initfunc: [],
		requests : {
			ajax : undefined,
			ajaxFail: function (event, xhr, settings, error){
				console.error(`The following error occurred:\n ${settings.method.toUpperCase()} ${settings.url} ${xhr.status} (${error})`);
			}
		},

		// Functions
		initialize: function(){
			for (i = 0; i < importApp.initfunc.length; i++) {
			  	importApp.initfunc[i]();
			}

		},

		log : function(){
			return this.name;
		},
		
		load : function(module){
			module.module_name? importApp.modules.push(module.module_name) : null;
			module.init? importApp.initfunc.push(module.init) : null;
			$.extend(true, importApp, module);
			eval(module.module_name + " = undefined");
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
			},

			hyperlink: function (content){
				//Hyperlink Support
				let linksFound = [];

				let url_length = 30;
				let linkIco = `<i class="material-icons link-ico my-auto ml-1">link</i>`;

				let hlinkRegExParts = {
					scheme : /(?:([a-z][a-z0-9+.-]*):)?/i,
					slash : /(?:\/\/)?/i,
					auth : /(?:([-a-z0-9_'](?:(?:\.?(?:[-a-z0-9_'~]|%[a-f]{2}))*[-a-z0-9_'])?)(?::((?:[-a-z0-9_'~!$&()\*+,;=]|%[a-f]{2})*))@)?/i,
					host : /((?:localhost)|(?:(?:1?[0-9]{1,2}|2[0-5]{1,2})(?:\.(?:1?[0-9]{1,2}|2[0-5]{1,2})){3})|(?:\[(?:[0-9a-f:]+)\])|(?:[a-z0-9](?:(?:\.?[-a-z0-9])*[a-z0-9])?\.[a-z0-9](?:[-a-z0-9]*[a-z0-9])?))/i,
					port : /(?::[0-9]+)?/i,
					path : /((?:\/(?:[-a-z0-9._~:@!$&'()*+,;=]|%[a-f]{2})+)*\/?)/i,
					query : /(\?(?:[-a-z0-9._~:@!$&'()*+,;=/?]|%[a-f]{2})*)?/i,
					fragment : /(#(?:[-a-z0-9._~:@!$&'()*+,;=/?]|%[a-f]{2})*)?/i
				}

				var hlinkRegEx = /(?:^|\b|\s)((?:([A-Za-z][A-Za-z0-9+.-]*):)?(?:\/\/)?(?:([-A-Za-z0-9_'](?:(?:\.?(?:[-A-Za-z0-9_'~]|%[A-Fa-f]{2}))*[-A-Za-z0-9_'])?)(?::((?:[-A-Za-z0-9_'~!$&()\*+,;=]|%[A-Fa-f]{2})*))@)?((?:localhost)|(?:(?:1?[0-9]{1,2}|2[0-5]{1,2})(?:\.(?:1?[0-9]{1,2}|2[0-5]{1,2})){3})|(?:\[(?:[0-9A-Fa-f:]+:[0-9A-Fa-f:]+)+\])|(?:(?:[Ww]{3}\.)?[A-Za-z0-9](?:(?:\.?[-A-Za-z0-9])*[A-Za-z0-9])?\.[A-Za-z0-9](?:[-A-Za-z0-9]*[A-Za-z0-9])?))(?::[0-9]+)?((?:\/(?:[-A-Za-z0-9._~:@!$&'()*+,;=]|%[A-Fa-f]{2})+)*\/?)(\?(?:[-A-Za-z0-9._~:@!$&'()*+,;=/?]|%[A-Fa-f]{2})*)?(#(?:[-A-Za-z0-9._~:@!$&'()*+,;=/?]|%[A-Fa-f]{2})*)?)(?:\b|\s|$)/ig;
				
				content.replace(hlinkRegEx, function(url){

					var tempURL = url;
					var linkMeta = {
						'full_url' : url,
						'favicon' : `http://s2.googleusercontent.com/s2/favicons?domain_url=${url}`,
						'anchor' : `<a class="d-inline-flex import-ex-link" target='_blank' href='${url}'>${url}</a>`
					}

					for (let key of Object.keys(hlinkRegExParts)) {
						tempURL = tempURL.replace(hlinkRegExParts[key], function(item){
								 if (item != ''){
								 	if (key == 'query'){
										linkMeta[key] = {string: item};

										var searchParams = new URLSearchParams(item);
										for (let p of searchParams) {
											linkMeta[key][p[0].replace("amp;", '')] = p[1];
										}
									}
									else
										linkMeta[key] = item;
								 } 

								return '';
							});
					}

					
					
					linksFound.push(linkMeta);

					return '';	
				});

				return linksFound;
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
					success: function (response, status, xhr){
						importApp.urls.redirect(response.url_redirect, response.field_redirect);
					}
				});
			}
		}

	}

	$(document).ajaxError(importApp.requests.ajaxFail);
	importApp.toString = importApp.log;
	importApp.valueOf = importApp.log;


	
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

	
	// Scroll Header
	function headerEffect(){
		( $(window).scrollTop() < 15)? 
		$(".import-header").removeClass("import-header-scrolled") :
		$(".import-header").addClass("import-header-scrolled");
	}	

	

	// Final stuff after web Load

	$(document).ready(function(){

		headerEffect();

		//Initialize
		importApp.initialize();

	
		initPhotoDragBox();
	});

	initDragBoxData();

	// Header Scroll

	$(window).scroll(function (event) {
		headerEffect();
	});