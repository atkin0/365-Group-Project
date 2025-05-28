#### Atkin Rong, Gary Yim, Rishan Baweja, Tyler Bao Tien
#### Pierce, Lucas
#### CSC 365
#### 20 April 2025


# <p align="center"> Gamer Society API Specification</p>

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

### 1.2: `/reviews/{review_id}/optional` (PUT)  
**Description**: Creates an additional optional review for parts of the game that they want to review. For example if someone was reviewing “Red Dead Redemption II” and wanted a separate rating for just the characters or the story, they could add one in.

**Request**:
```json
[
	{
	  "aspect_to_review": "string",
	  "optional_rating": "int"
	}
]
```

**Response**:
```json
[
	{
		"success": "boolean"
	}
]
```

### 1.3: `/reviews/{review_id}/publish` (POST)  
**Description**: Publishes review to profile  

**Request**:  
```json  
[
    {
        "review_id": "int"
    }
]
```

**Response**:  
```json  
[
    {
        "success": "boolean"
    }
]
```

## 2. Patching a Review

The API calls are made in this sequence when making a review:
1. `Edit Review`
2. `Edit Optional Review`
3. `Publish Review`

### 2.1: `/reviews/{review_id}/edit` (PUT)  
**Description**: If a user changes their mind on a review, and wants to go back and edit it.

**Request**:  
```json
[
    {
        "review_id": "int",
        "change_required_rating": "int",
        "change_description_of_game": "string"
    }
]
```

**Response**:  
```json
[
    {
        "success": "boolean"
    }
]
```

### 2.2: `/reviews/{review_id}/optional` (PUT)  
**Description**: Edits the additional optional review.

**Request**:  
```json  
[
    {
        "change_aspect_to_review": "string",
        "change_optional_rating": "int"
    }
]
```

**Response**:  
```json  
[
    {
        "success": "boolean"
    }
]
```

### 2.3: `/reviews/{review_id}/publish` (PATCH)  
**Description**: Edited review will be published

**Request**:  
```json  
[
    {
        "review_id": "int"
    }
]
```
**Response**:  
```json  
[
    {
        "success": "boolean"
    }
]
```

## 3. View List of Games 
### 3.1: `/games/` (GET)  
**Description**: Displays popular games that have been reviewed recently

**Response**:  
```json  
[
    {
        "game_id": "int",
        "game_name": "string",
        "review_num": "int"
    }
]
```
### 3.2: `/games/search` (GET)  
**Description**: Searches for games based on the name or other parameters.

**Parameter**:  
```json  
[
    {
        "game_name": "string (Optional)",
        "genre": "string (Optional)",
        "sort_by": "string"
    }
]
```

**Response**:  
```json  
[
    {
        "game_id": "int",
        "game_name": "string"
    }
]
```

### 3.3: `/games/{game_id}` (GET)  
**Description**: Display reviews for a specific game

**Response**:  
```json  
[
    {
        "game_name": "string",
        "game_genre": "string",
        "game_description": "string",
        "review_ids": "int",
        "review_name": "string",
        "review_rating": "int",
        "review_description": "string"
    }
]
```
### 3.4: `/games/{game_id}/overview` (GET)
**Description**: Retrieves comprehensive information about a specific game including reviews, comments, optional reviews, and aggregate statistics.

**Response**:
```json
{
    "game_id": "int",
    "title": "string",
    "aggregate_rating": "float",
    "total_playtime": "int",
    "reviews": [
        {
            "id": "int",
            "user_id": "int",
            "username": "string",
            "score": "float",
            "text": "string",
            "updated_at": "datetime"
        }
    ],
    "optional_reviews": [
        {
            "id": "int",
            "review_name": "string",
            "optional_rating": "int",
            "review_id": "int",
            "updated_at": "datetime"
        }
    ]
}
```

## 4. View User Profile
### 4.1: `/users/{user_id}/friends` (GET)  
**Description**: Display a specific user's list of friends

**Response**:  
```json  
[
    {
        "user_id": "int",
        "user_name": "string"
    }
]
```

### 4.2: `/users/{user_id}/settings` (GET)  
**Description**: Display all settings for a specific user. Can only access your own settings

**Response**:  
```json  
[
    {
        "setting_id": "int",
        "setting_value": "int"
    }
]
```

### 4.3: `/users/{user_id}/settings/edit` (PATCH)  
**Description**: Update a user's setting

**Request**:  
```json  
[
    {
        "setting_id": "int",
        "setting_name": "string",
        "setting_value": "int"
    }
]
```

**Response**:  
```json  
[
    {
        "success": "boolean"
    }
]
```

### 4.4: `/users/{user_id}/history` (GET)  
**Description**: Let you see a specific user's review history and their top-rated games.

**Request**:  
```json  
[
    {
        "user_id": "int"
    }
]
```

**Response**:  
```json  
[
    {
        "review_id": "int",
        "game_reviewing": "string",
        "review_rating": "int",
        "review_description": "string"
    }
]
```

### 4.5: `/users/{user_id}/favorite` (GET)  
**Description**: Displays a user's 5 favorite games

**Request**:  
```json  
[
    {
        "user_id": "int"
    }
]
```

**Response**:  
```json  
[
    {
        "review_id": "int",  
        "game_reviewing": "string",
        "review_rating": "int",
        "review_description": "string"
    }
]
```

## 5. View Feed
### 5.1: `/feed/` (GET)  
**Description**: Gets a list of recent friend reviews and view them on feed

**Response**:  
```json  
[
    {
        "title_of_game": "string",
        "friend_name": "string",
        "friend_rating": "int",
        "friend_description_of_game": "string"
    }
]
```

## 6. Admin Functions
### 6.1: `/admin/delete` (POST)  
**Description**: A call to delete a post that we deem is not fit for the site

**Request**:  
```json  
[
    {
        "review_id": "int"
    }
]
```
**Response**:  
```json  
[
    {
        "success": "boolean"
    }
]
```

## 8. Comment On Review
### 8.1: `/comments/` (POST)  
**Description**: Creates a new comment for a user to post on someone else’s review.

**Request**:  
```json  
[
    {
        "review_id": "int",
        "comment_of_review": "string"
    }
]
```
**Response**:  
```json  
[
    {
        "comment_id": "int"
    }
]
```
### 8.2: `/comments/{comment_id}/publish` (POST)  
**Description**: Publishes comment to someone else’s review

**Request**:  
```json  
[
    {
        "review_id": "int"
    }
]
```

**Response**:  
```json  
[
    {
        "success": "boolean"
    }
]
```
## 9. Recommendations (Complex Endpoint)
### 8.1: `/recommendations/user_id` (GET)  
**Description**: Gets recommended games based on user historical genres, recently played genres, overall top recent games, and friend's top recent games.

**Request**:  
```json  
[
    {
        "user_id": "int",
    }
]
```
**Response**:  
```json  
[
    {
        "game_name": "string",
        "score": "float",
        "reviews": "string[]"
    }
]
```