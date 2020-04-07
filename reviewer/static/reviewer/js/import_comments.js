	
	const importComment =  {

		module_name: "importComment",
		comments : {
			pageLimit : undefined,
			likeLimit : 6,
			likedPressed : {},
			spamMsg : "You are not supposed to spam the like buttons.",

			// Functions
			loadLikeIcon : function(commentArray){
				var commentvisual = commentArray;

				for(i = 0; i < commentvisual.length; i++){
					let liked_vis = "[data-comment-id='comment-" + commentvisual[i] + "']";
					$(liked_vis).find(".comment-like").html("star");
					$(liked_vis).find(".comment-like").addClass("liked");
				}
			},

			updateLikeIcon: function(id, state, count, addhtml){

				let icons = ["star_border", "star"];
				let liked_comm = "[data-comment-id='" + id + "']";
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
					renderMathInElement(document.querySelector(cvars[1]));
					liked_comm = $(liked_comm);
					liked_comm.find(cvars[2]).html(icons[1]);
					liked_comm.find(cvars[2]).addClass("liked");
					liked_comm.removeClass("mb-3");
					liked_comm.addClass("my-3");
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

			likeClick : function(thes){

				let commentpass = $(thes).parents(".comment");
		 		let commentpassID = commentpass.attr("data-comment-id");

		 		commentpassID in importApp.comments.likedPressed? importApp.comments.likedPressed[commentpassID]++ : (importApp.comments.likedPressed[commentpassID] = 1);
		 		importApp.comments.detectManyLike();

		 		current_likd = $("[data-comment-id='" + commentpassID + "']");
				curr_likdct = parseInt(current_likd.find(".comment-like-count").html());
				curr_state = current_likd.find(".comment-like").html();
				curr_state = !(curr_state == 'star');
				curr_state? curr_likdct++ : curr_likdct--;  
				importApp.comments.updateLikeIcon(commentpassID, curr_state, curr_likdct);
	
				importApp.requests.likeRequest = $.ajax({
					url: importApp.urls.likeURL.replace('$course_code', commentpass.attr("data-code")).replace('123456789', commentpass.attr("data-number")),
					method: "post",
					data: {'commentID': commentpassID},
					headers: {'X-CSRFToken': importApp.csrfToken },
					error: importApp.requests.ajaxFail,
					success: function (response, textStatus, xhr){
						importApp.comments.updateLikeIcon(commentpassID, response.state, response.count, response.com_html);
					}
				});			
			}
		},
	
		requests:{
			likeRequest : undefined
		},

		urls: {
			likeURL : undefined
		}
	}
	
	Object.defineProperty(importComment.comments, 'likeLimit', { writable: false, configurable: false });
	importApp.load(importComment);

	$(".comment-action").on("click", ".comment-like" , function(e){ e.stopPropagation(); importApp.comments.likeClick(this) }); 