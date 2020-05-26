	
	var importLessons =  {

		 // Output Question // Randomize
         // Keyboard Detect // Press Enter Event
         // Check Answer // Check & Submit Answer 
         // Make Progress // Depends on Total
         // Reset // Reset Input Fields

		module_name: "importLessons",
		builder: {

			editor: undefined,
			script: {
				data : undefined,
				questions: undefined,
				qdata: undefined,
				load: function(){

					$(".import-code-console").html("");
					let code = importApp.builder.editor.session.getValue();
					let errors = importApp.builder.editor.session.getAnnotations();
					let hasError = false;
					let retval = false;

					errors.forEach(function(item){
						if (item.type == "error"){
							console.log(`ERROR: ${item.text} (${item.row + 1}, ${item.column + 1})`);
							hasError = true;
						}
					});

					if (/<\/\s*script\s*>/ig.test(code)){
						alert("Closing script tags are not allowed.");
					}
					else if (/window\.location/ig.test(code)){
						alert("window.location is not allowed.");
					}
					else if (/importApp/g.test(code)){
						alert("Using importApp with the builder is not allowed.");
					}
					else if (!hasError){
						if (importApp.builder.script.data)
							$("#import-script").remove()

						importApp.builder.script.data = document.createElement("script");
						importApp.builder.script.data.innerHTML = code;
						document.body.appendChild(importApp.builder.script.data);
						importApp.builder.script.data.setAttribute("id", "import-script");
						$("#import-script").appendTo(".scripts");

						importApp.builder.script.questions = question();

						if (importApp.builder.script.questions != undefined && Array.isArray(importApp.builder.script.questions) ){
							importApp.builder.script.qdata = {
								remq: importApp.builder.script.questions,
								currentq: undefined
							}

							try{
								importApp.builder.script.qdata.currentq = Math.floor(Math.random() * importApp.builder.script.qdata.remq.length); 
								let currentq = importApp.builder.script.qdata.currentq;
								$(".import-question").html(importApp.builder.script.qdata.remq[currentq].question);
								if ($(".import-subquestion").length && importApp.builder.script.qdata.remq[currentq].subquestion != undefined)
									$(".import-subquestion").html(importApp.builder.script.qdata.remq[currentq].subquestion);

								if ($(".import-choices").length){
									$(".import-choices").html("");
									for (var choc = 0; choc < importApp.builder.script.qdata.remq[currentq].choices.length; choc++){
										$(".import-choices").append(`<div class="d-flex layer-container p-2 mb-2 import-choice">
											<div class="py-2 px-3 my-auto">
												${String.fromCharCode(65+choc)}
											</div>
											<div class="mx-2 my-auto import-choice-data">
												${importApp.builder.script.qdata.remq[currentq].choices[choc]}
											</div>
										</div>`);
										if (choc == 4)
											break;
									}
								}

								retval = true;
							}
							catch(err){
							}
						}
						else{
							alert("Question Set must be an array.");
						}
					}
					return retval;
				}
			},
			init: function(div_id){
				importApp.builder.editor =	ace.edit(div_id);
				importApp.builder.editor.session.setMode("ace/mode/javascript");
	    		importApp.builder.editor.session.setTabSize(2);
	    		importApp.builder.editor.setShowPrintMargin(false);
			}
		},

		questions:{
			create: function(that, url=window.location.href){

				if (importApp.requests.ajax)
					importApp.requests.ajax.abort();
				  
				var form = document.getElementById(that);
				var formData = new FormData(form);
				$(".import-question-create").prop("disabled", true);

				importApp.requests.ajax =  $.ajax({
					type: 'post',
					url: url,
					data: formData,
					cache: false,
					contentType: false,
					processData: false,
					complete: function(){ $(".import-question-create").removeAttr("disabled"); },
					success: function (response, status, xhr){
						if (response.error)
							alert(response.error)
						else{
							$("#importModal").modal('hide');
							if($(".lesson-question").length > 0){
								$(".questions").append(response.question);
							}
							else{
								$(".questions").html(response.question);
							}
						}
				    }
				});
			},
			input:{
				allow: function(that){
					let charCount = $(that).val().trim();

					if (charCount == 0){
						$(".import-code-iden-submit").prop("disabled", true);
					}
					else{
						$(".import-code-iden-submit").removeAttr("disabled");
					}
				},
				check: function(){
					if ($(".import-code-iden-input").val().trim().length > 0){
						//Modify to work with actual lesson page
						let currentq = importApp.builder.script.qdata.currentq;
						let userInput = $(".import-code-iden-input").val().trim();
						let result = importApp.builder.script.qdata.remq[currentq].answer(userInput);

						if (userInput == result){

						}
					}
				}
			}
		},
		init: function(){

		}
	}
	
	importApp.load(importLessons);
	delete importLessons;
