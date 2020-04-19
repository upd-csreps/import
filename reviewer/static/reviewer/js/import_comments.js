	
	var importComment =  {

		module_name: "importComment",
		comments : {
			pageLimit : undefined,
			likeLimit : 6,
			likedPressed : {},
			spamMsg : "You are not supposed to spam the like buttons.",
			deleteMsg : 'Do you want to delete this comment?',

			// Functions

			count: {
				mem : {},
				byType: function(ct, type){
					ct === undefined? null : this.mem[type] = ct;
					return this.mem[type]
				},
				byCourse : function(ct){
					return this.byType(ct, 'course');
				},
				byUser : function(ct){
					return this.byType(ct, 'user');
				},
			},

			submit: function(that){
				if (importApp.requests.ajax)
				        importApp.requests.ajax.abort();
				  
				var form = $(that);
				var formData = new FormData(that);
				var inputs = form.find("input, select, button, textarea");
				inputs.prop("disabled", true);

				importApp.requests.ajax =  $.ajax({
				    type: 'post',
				    url: window.location.href,
				    data: formData,
				    cache: false,
				    contentType: false,
				    processData: false,
				    complete: function(){ inputs.prop("disabled", false); },
				    success: function (response, status, xhr){

				    	let newcomment = response.comment_html;
						importApp.comments.count.byCourse() != 0? $(".course-comments").prepend(newcomment) : $(".course-comments").html(newcomment);
						newcomment = $(`.course-comments [data-comment-id='comment-${response.commentid}']`);
						newcomment.addClass("the-new-comment");
						newcomment.fadeIn(2000);
						newcomment.removeClass("the-new-comment");
						renderMathInElement(document.querySelector('.course-comments'));
						$('.page-count-parent').html(response.page_create);
						importApp.comments.count.byCourse( importApp.comments.count.byCourse()+1);
						$(".comme-count").html(importApp.comments.count.byCourse());
				    	$(".comment-text-area").val("");
				    	clearImage("comment-image-upload", document.querySelector(".import-image-drag"));
				    	$(`.course-comments .comment:nth-of-type(${(importApp.comments.pageLimit+1)})`).remove();
				    }
				});
			},

			delete:  function(that){

				let decision = confirm(importApp.comments.deleteMsg);

				if(decision){
					commentpass = $(that).parents(".comment");
			 		commentpassid = commentpass.attr("data-comment-id");
			 		if (importApp.requests.ajax) {
				        importApp.requests.ajax.abort();
				    }

			 		importApp.requests.ajax = $.ajax({
						url: encodeURI(importApp.urls.courseURL.replace('$course_code', commentpass.attr("data-code")).replace('123456789', commentpass.attr("data-number"))),
						method: "delete",
						data: {'commentID': commentpassid },
						headers: {'X-CSRFToken': importApp.csrfToken },
						success: function (response, status, xhr){
							commentpass.fadeOut(1000, function(){

								commentpass.remove();

								if ($(".course-comments").length){
									if(importApp.comments.count.byCourse() > 0){
										importApp.comments.count.byCourse(response.course_comment_count);
										$(".comme-count").html(importApp.comments.count.byCourse());
									}

									response.page_count>1? null: $(".page-count-parent").html('');
									
									if ( $(".course-comments .comment").length > 0){
										response.comment_html? $(".course-comments").append(response.comment_html) : null;
									}
									else{
										response.page_count > 0? importApp.urls.redirect(encodeURI(importApp.urls.courseURL.replace('$course_code', commentpass.attr("data-code")).replace('123456789', commentpass.attr("data-number")) + `c/${response.page_count}/`) ) : $(".course-comments").append(response.empty_html);				
									}
								}
								else if ($(".created-comments").length){
									var commecount = parseInt($(".created-count").html());
									$(".created-count").html(commecount-1);
								}
								renderMathInElement(document.body);
							});
						}
				    });
			 	}
			},

			updateLikeIcon: function(id, state, count, addhtml){

				let icons = ["star_border", "star"];
				let liked_comm = `[data-comment-id='${id}']`;
				let cvars = [".liked-count", ".liked-comments", ".comment-like"];

				let liked_ct = parseInt($(cvars[0]).html());
				$(liked_comm).find(".comment-like-count").html(count);

				$(cvars[1] + liked_comm).fadeOut(2000,
					function(){ 
						$(cvars[1] + liked_comm).remove();
					}
				);

				if (state){
					$(cvars[1]).prepend(addhtml);
					$(cvars[1]).length? renderMathInElement(document.querySelector(cvars[1])): null;
					$(liked_comm).find(cvars[2]).html(icons[1]);
					$(liked_comm).find(cvars[2]).addClass("liked");
					$( `${cvars[1]} ${liked_comm}`).removeClass("mb-3");
					$( `${cvars[1]} ${liked_comm}`).addClass("my-3");
					$(cvars[0]).html(liked_ct+1);
				}
				else{
					liked_comm = $(liked_comm);
					liked_comm.find(cvars[2]).html(icons[0]);
					liked_comm.find(cvars[2]).removeClass("liked");
					$(cvars[0]).html(liked_ct-1);
				}
			},

			detectManyLike : function(){

				var spamFlag = false;
				var disableClick = false;
				for (let comment of Object.keys(importApp.comments.likedPressed)) {
					if (importApp.comments.likedPressed[comment] > importApp.comments.likeLimit){
						spamFlag=true;
						if (importApp.comments.likedPressed[comment] > 10){
							disableClick = true;
						}
						break;
					}
				}

				spamFlag? alert(importApp.comments.spamMsg) : null;

				if (disableClick){
					$(".comment-like").addClass("-disabled");
					importApp.comments.likeClick = function(){};
				}
			},

			likeClick : function(that){

				let commentpass = $(that).parents(".comment");
		 		let commentpassID = commentpass.attr("data-comment-id");

		 		commentpassID in importApp.comments.likedPressed? importApp.comments.likedPressed[commentpassID]++ : (importApp.comments.likedPressed[commentpassID] = 1);
		 		importApp.comments.detectManyLike();

		 		current_likd = $(`[data-comment-id='${commentpassID}']`);
				curr_likdct = parseInt(current_likd.find(".comment-like-count").html());
				curr_state = current_likd.find(".comment-like").html();
				curr_state = !(curr_state == 'star');
				curr_state? curr_likdct++ : curr_likdct--;  
				importApp.comments.updateLikeIcon(commentpassID, curr_state, curr_likdct);
	
				importApp.requests.likeRequest = $.ajax({
					url: encodeURI(importApp.urls.likeURL.replace('$course_code', commentpass.attr("data-code")).replace('123456789', commentpass.attr("data-number"))),
					method: "post",
					data: {'commentID': commentpassID},
					headers: {'X-CSRFToken': importApp.csrfToken },
					success: function (response, textStatus, xhr){
						importApp.comments.updateLikeIcon(commentpassID, response.state, response.count, response.com_html);
					}
				});			
			},

			trackCount: function(that){
				var max_length = $(that).attr("maxlength");
				var letterct = max_length - $('.comment-text-area').val().length;
				var percent = $('.comment-text-area').val().length/max_length;
				$('.comment-letter-count').html(letterct);
				$('#comment-circle').circleProgress('value', percent); 
			}
		},
	
		requests:{
			likeRequest : undefined
		},

		urls: {
			courseURL : undefined,
			likeURL : undefined
		},

		init: function(){
			$('.comment-letter-count').html($('.comment-text-area').attr("maxlength"));
		}
	}
	
	Object.defineProperty(importComment.comments, 'likeLimit', { writable: false, configurable: false });
	importApp.load(importComment);
	delete importComment;

	$(".comment-action").on("click", ".comment-like" , function(e){ e.stopPropagation(); importApp.comments.likeClick(this) }); 