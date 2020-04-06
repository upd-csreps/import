

	const importComment =  {

		comments : {
			page_limit : undefined,
			like_limit : 6,
			liked_pressed : {},
			spamMsg : "You are not supposed to spam the like buttons.",

			// Functions
			loadLikeIcon : function(comment_array){
				var commentvisual = comment_array;

				for(i = 0; i < commentvisual.length; i++){
					let liked_vis = "[data-comment-id='comment-" + commentvisual[i] + "']";
					$(liked_vis).find(".comment-like").html("star");
					$(liked_vis).find(".comment-like").addClass("liked");
				}
			},

			updateLikeIcon: function(id, state, count, addhtml){
				let icons = ["star_border", "star"];
				let liked_comm = $("[data-comment-id='" + id + "']");

				liked_comm.find(".comment-like-count").html(count);

				$(".liked-comments [data-comment-id='" + id + "']").fadeOut(2000,
					function(){ 
						$(".liked-comments [data-comment-id='" + id + "']").remove()
					}
				);

				if (state){
					liked_comm.find(".comment-like").html(icons[1]);
					liked_comm.find(".comment-like").addClass("liked");
					$(".liked-comments").prepend(addhtml);
					$(".liked-count").html( parseInt($(".liked-count").html()) + 1 )
				}
				else{
					liked_comm.find(".comment-like").html(icons[0]);
					liked_comm.find(".comment-like").removeClass("liked");
					$(".liked-count").html( parseInt($(".liked-count").html()) - 1 )
				}
			},

			detectManyLike : function(){

				var spamFlag = false;
				var disableClick = false;
				for (let comment of Object.keys(importApp.comments.liked_pressed)) {
					if (importApp.comments.liked_pressed[comment] > importApp.comments.like_limit){
						spamFlag=true;
						if (importApp.comments.liked_pressed[comment] > 10){
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
		 		let commentpassid = commentpass.attr("data-comment-id");

		 		commentpassid in importApp.comments.liked_pressed? importApp.comments.liked_pressed[commentpassid]++ : (importApp.comments.liked_pressed[commentpassid] = 1);
		 		importApp.comments.detectManyLike();

		 		current_likd = $("[data-comment-id='" + commentpassid + "']");
				curr_likdct = parseInt(current_likd.find(".comment-like-count").html());
				curr_state = current_likd.find(".comment-like").html()
				curr_state = !(curr_state == 'star');
				curr_state? curr_likdct++ : curr_likdct--;  
				importApp.comments.updateLikeIcon(commentpassid, curr_state, curr_likdct);

				importApp.requests.like_request = $.ajax({
					url: importApp.urls.like_url.replace('$course_code', commentpass.attr("data-code")).replace('123456789', commentpass.attr("data-number")),
					type: "post",
					data: {'commentID': commentpassid},
					headers: {'X-CSRFToken': importApp.csrfToken }
				});

				// Callback handler that will be called on success
				importApp.requests.like_request.done(function (response, textStatus, jqXHR){
					importApp.comments.updateLikeIcon(commentpassid, response.state, response.count, response.com_html);
				});

				// Callback handler that will be called on failure
				importApp.requests.like_request.fail(function (jqXHR, textStatus, errorThrown){
					console.error("The following error occurred: "+ textStatus, errorThrown );
				});		 	
			}

		},
	
		requests:{
			like_request : undefined
		},

		urls: {
			like_url : undefined
		}
		
	}
	
	Object.defineProperty(importComment.comments, 'like_limit', { writable: false, configurable: false });
	importApp.load(importComment);

	
	$(".comment-action").on("click", ".comment-like" , function(){ importApp.comments.likeClick(this) }); 
