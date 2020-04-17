
	var importDragPhoto = {

		module_name: "importDragPhoto",
		dragPhoto: {

			clear: function (target, dragicon){
				$("." + target + " input[type=file]").val("");
				if($('#id_imagehascleared').length)
					document.querySelector("#id_imagehascleared").setAttribute('checked', 'checked');
				dragicon.querySelector(".material-icons").innerHTML = "add_a_photo";
				dragicon.querySelector(".material-icons").classList.remove("import-image-uploaded-icon");
				dragicon.style.backgroundImage = "";
				document.querySelector(".addphoto-popper").innerHTML = "Add a photo"
			},
			update: function (files, dragicon){
				$(".import-image-drag-enabled").removeClass("dragging");
				let reader = new FileReader();
				
				reader.onload = function(){
					if (importApp.isImage(files[0])){
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
			},
			tooltip: function(){
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
			},

			init: function(){

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
						importApp.dragPhoto.clear(targetClassName, this);
					}
				}); 

				function GetAroundEventListenerUpdate(i){
					upphotos[i].addEventListener('change', function(e){
						importApp.dragPhoto.update(upphotos[i].files, targetElements[i]);
						if ($('#id_imagehascleared').length)
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
						if (importApp.isImage(e.dataTransfer.files[0])){
							upphoto.files = e.dataTransfer.files
							importApp.dragPhoto.update(upphoto.files, upphoto_drag[i]);
						}
					});
				}

				for (i = 0; i < upphoto_drag.length; i++){
					GetAroundEventListenerDrop(i);
				}

				importApp.dragPhoto.tooltip();
			},

			load: function(clear=false){
				// Get each Drag Box
				var image_drops = document.querySelectorAll(".import-image-drag");
				for (i = 0; i < image_drops.length; i++){
					
					var dragicon = image_drops[i];

					if (clear){
						importApp.dragPhoto.clear(dragicon.getAttribute("data-file-target"),dragicon)
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
		},

		isImage: function (file) {
			return file && file['type'].split('/')[0] === 'image';
		},
		init: function(){
			importApp.dragPhoto.init();
			importApp.dragPhoto.load();
		}
	} 

	importApp.load(importDragPhoto);
	delete importDragPhoto;