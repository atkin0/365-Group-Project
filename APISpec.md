#### Atkin Rong, Gary Yim, Rishan Baweja, Tyler Bao Tien
#### Pierce, Lucas
#### CSC 365
#### 20 April 2025


# <p align="center"> Gamer Society API Specification and Example Flows</p>

## API Specification:
## 1. Creating Review 

The API calls are made in this sequence when making a review:
1. `New Review`
2. `Optional Review`
3. `Publish Review`

### 1.1: `/reviews/` (POST)
**Description**: Creates a new review for a user

**Request**:
```json
[
	{
		"user_id": "int",
		"user_name": "string",
		"game_name": "string",
		"required_rating": "int",
		"description_of_game": "string"
	}
]
```
**Response**:
```json
[
	{
		"review_id": "int"
	}
]
```

1.2: /reviews/{review_id}/optional (PUT)
Description: Creates an additional optional review for parts of the game that they want to review. For example if someone was reviewing “Red Dead Redemption II” and wanted a separate rating for just the characters or the story, they could add one in.
Request:
“aspect_to_review”: “string”,
“optional_rating”: “int”
Reponse:
“success”: boolean
1.4: /reviews/{review_id}/publish (POST)
Description: Publish review to profile
Response:
“success”: “boolean”

Patching Review
2.1: /Reviews/{review_id}/Edit
Request:
“review_id”: integer
“description_title”: string
“score”: integer
Reponse:
“success”: boolean
2.2: /Reviews/{review_id}/Publish
Request:
“review_id”: integer
Reponse:
“success”: boolean
Adding Games
3.1: /Games
Display popular games that have been reviewed recently
Response:
“game_id”: integer
“game_name”: string
“review_num”: int
3.2 /Games/Search
Search for games based on the name or other parameters.
Parameter
“game_name”: string (Optional)
“genre”: string (Optional)
“sort_by”: Choose from options such as alphabetically, amount of reviews, or genre
Response:
“game_id”: integer
“game_name”: string
3.3/Games/{game_id}
Display reviews for a specific game
Response:
“game_name”: string
“game_genre”: string
“game_description”: string
“review_num”: int
 View User Profile
4.1: /Users/{user_id}/Friends
Display a specific users list of friends
Response:
“user_id”: id
“user_name”: string
4.2: /Users/{user_id}/Settings
Display users settings
4.2: /Users/{user_id}/Settings/Edit
4.2: /Users/{user_id}/Settings/Edit/Post
4.3: /Users/{user_id}/History 
Let you see specific users review history and their top rated games.
Request:
“user_id”: int
Response:
“review_id”: int
View Feed

Example Flows:
	Steve the Minecraft gamer has come to Gamer Society to review his favorite game Minecraft, because he needs to show everyone how much he loves it. To leave his review he:
Starts by calling POST /Reviews to get a new Review with ID 101. 
Then he leaves the basic, required review by calling POST /Reviews/101/ratings/required and passes in his rating of 10/10. 
Then, he decides he wants to leave an additional, optional review for his favorite part of Minecraft: its creativity. So, he calls POST /Reviews/101/ratings/optional and passes in his rating of 10/10 for its creativity. 
He then calls POST /Reviews/101/description to leave a description of his thoughts on the game. 
After he has finished up writing his thoughts about it, he calls  POST /Reviews/101/publish to finish the review. 
The review then gets posted to his profile, where he can share how much he loves Minecraft.

	John wants to add a new friend
Starts by passing GET /Users/user_id to check out the guy’s profile
Then he passes a POST /Users/user_id/Friends to add the guy as a new friend
But then say the guy doesn’t add him back
so he passes a DELETE /Users/user_id/Friends

	
Louis wants to find recommended games
GET /Reviews/review_id and GET /Users/{user_id}/Friends
get reviews friends did on games and filter out the lowly rated ones
get reviews done by other people sorted by helpfulness
GET /Users/{user_id}/History
get a list of games Louis played before
GET /Genres/{game_id}
Join the datasets to get recommendations on games based on the genre Louis wants to play, what he’s played before, what his friends have played and liked, and what other people like. Louis can also read the reviews from his friends and other reviews rated highly useful to select the game he wants.

