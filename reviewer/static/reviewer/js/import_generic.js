
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
			},
			xhr : function(){
				let xhr = $.ajaxSettings.xhr();
				let last_response_length = false;

				xhr.onabort = function(e){}

				xhr.onprogress = function(e) {

					var this_response, response = e.currentTarget.response;

					if(last_response_len == false){
						this_response = response;
						last_response_len = response.length;
					}
					else{
						this_response = response.substring(last_response_len);
						last_response_len = response.length;
					}

					console.log(this_response);
			    }

			    xhr.upload.onprogress = function(e){}

				return xhr;
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

		//Initialize
		headerEffect();
		importApp.initialize();
	});

	// Header Scroll

	$(window).scroll(function (event) {
		headerEffect();
	});