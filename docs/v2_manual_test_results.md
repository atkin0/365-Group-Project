### Example Flow 3:
- GET /Reviews/review_id and GET /Users/{user_id}/Friends
  - get reviews friends did on games and filter out the lowly rated ones
  - get reviews done by other people sorted by helpfulness
- GET /Users/{user_id}/History
  - get a list of games Louis played before
- GET /Genres/{game_id}
- Join the datasets to get recommendations on games based on the genre Louis wants to play, what he’s played before, what his friends have played and liked, and what other people like. Louis can also read the reviews from his friends and other reviews rated highly useful to select the game he wants.

curl -X 'GET' \
  'http://127.0.0.1:3000/recommendation/?user_id=2' \
  -H 'accept: application/json' \
  -H 'access_token: brat'

response body
[
  {
    "game_name": "csgo",
    "score": 9,
    "reviews": [
      "r"
    ]
  },
  {
    "game_name": "overwatch",
    "score": 9,
    "reviews": [
      "hi"
    ]
  },
  {
    "game_name": "leagueoflegends",
    "score": 10,
    "reviews": [
      "t"
    ]
  },
  {
    "game_name": "adventurecapitalist",
    "score": 5,
    "reviews": [
      "lol"
    ]
  }
]
