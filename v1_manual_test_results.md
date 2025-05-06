## Creating Review Workflow

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
