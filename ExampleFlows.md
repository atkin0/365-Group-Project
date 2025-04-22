#### Atkin Rong, Gary Yim, Rishan Baweja, Tyler Bao Tien
#### Pierce, Lucas
#### CSC 365
#### 20 April 2025


# <p align="center"> Gamer Society Example Flows</p>

### Example Flow 1:
Steve the Minecraft gamer has come to Gamer Society to review his favorite game Minecraft, because he needs to show everyone how much he loves it. To leave his review he:
- Starts by calling POST /Reviews to get a new Review with ID 101. 
- Then he leaves the basic, required review by calling POST /Reviews/101/ratings/required and passes in his rating of 10/10. 
- Then, he decides he wants to leave an additional, optional review for his favorite part of Minecraft: its creativity. So, he calls POST /Reviews/101/ratings/optional and passes in his rating of 10/10 for its creativity. 
- He then calls POST /Reviews/101/description to leave a description of his thoughts on the game. 
- After he has finished up writing his thoughts about it, he calls  POST /Reviews/101/publish to finish the review. 

The review then gets posted to his profile, where he can share how much he loves Minecraft.

### Example Flow 2:
John wants to add a new friend
- Starts by passing GET /Users/user_id to check out the guy’s profile
- Then he passes a POST /Users/user_id/Friends to add the guy as a new friend
- But then say the guy doesn’t add him back
- So he passes a DELETE /Users/user_id/Friends

### Example Flow 3:
- GET /Reviews/review_id and GET /Users/{user_id}/Friends
  - get reviews friends did on games and filter out the lowly rated ones
  - get reviews done by other people sorted by helpfulness
- GET /Users/{user_id}/History
  - get a list of games Louis played before
- GET /Genres/{game_id}
- Join the datasets to get recommendations on games based on the genre Louis wants to play, what he’s played before, what his friends have played and liked, and what other people like. Louis can also read the reviews from his friends and other reviews rated highly useful to select the game he wants.

