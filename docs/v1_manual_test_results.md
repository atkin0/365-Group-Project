Steve the Minecraft gamer has come to Gamer Society to review his favorite game Minecraft, because he needs to show everyone how much he loves it. To leave his review he:
- Starts by calling POST /Reviews to get a new Review with ID 1. 
- Then he leaves the basic, required review by calling POST /Reviews/review and passes in his rating of 10/10 and adds his description of I love minecraft. 
- Then, he decides he wants to leave an additional, optional review for his favorite part of Minecraft: its creativity. So, he calls POST /Reviews/10/optional and passes in his rating of 10/10 for its creativity. 
- After he has finished up writing his thoughts about it, he calls  POST /Reviews/1/publish to finish the review. 

The review then gets posted to his profile, where he can share how much he loves Minecraft.

Testing results
curl -X 'POST' \
  'http://127.0.0.1:3000/review/review' \
  -H 'accept: application/json' \
  -H 'access_token: brat' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": 0,
  "game_id": 5,
  "score": 10,
  "description": "I love minecraft"
}'
Response 
{
  "review_id": 1
}


curl -X 'POST' \
  'http://127.0.0.1:3000/review/review/1/optional' \
  -H 'accept: */*' \
  -H 'access_token: brat' \
  -H 'Content-Type: application/json' \
  -d '{
  "aspect_to_review": "Creativity",
  "optional_rating": 10
}'

 access-control-allow-credentials: true 
 content-type: application/json 
 date: Fri,09 May 2025 22:47:32 GMT 
 server: uvicorn 

curl -X 'POST' \
  'http://127.0.0.1:3000/review/review/1/publish' \
  -H 'accept: */*' \
  -H 'access_token: brat' \
  -d ''

access-control-allow-credentials: true 
content-type: application/json 
 date: Fri,09 May 2025 22:48:27 GMT 
 server: uvicorn 