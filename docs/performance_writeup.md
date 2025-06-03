# Performance Review

### Fake Data Modeling - How many rows are generated for each endpoint and why did we choose these values?
- genres: 11
- games: 500
- users: 10000
- history 10000-50000
- friends: 0-100000
- reviews: 250000
- comments: 0-300000
- optional_reviews: 500000

We chose these values because we thought they are somewhat of the right ratio of a gaming site. 
Some are less than normal because if we added more faking data would take too long.

### Endpoint Execution Times Before Improvement

- delete post: 0174 ms
- get feed: 0395 ms
- get popular recommendations: 1718 ms
- post review: 0018 ms
- post optional review: 0102 ms
- publish review: 0020 ms
- edit review: 0018 ms
- get review from id: 0021 ms
- post comment: 0063 ms
- get comments: 0053 ms
- create user: 0016 ms
- add friends: 0022 ms
- display my friended: 0011 ms
- display friended me: 0022 ms
- show history: 0055 ms
- show top: 0035 ms
- add game played: 0094 ms
- get recent games: 0161 ms
- search games: 0056 ms
- get reviews for games: 0007 ms
- add game history: 0018 ms
- get game overview: 0017 ms

### What is our slowest endpoint and how did we improve it?
slowest end point is get popular recommendations: 1400ish ms


```
SELECT games.genre_id AS genre_id
FROM history
JOIN games on history.game_id = games.id
WHERE user_id = :user_id
ORDER BY (last_played / time_played) DESC
LIMIT 10
```

PRE_OPTIMIZATION:
```
Limit  (cost=22.23..22.23 rows=3 width=12)
  ->  Sort  (cost=22.23..22.23 rows=3 width=12)
        Sort Key: history.last_played/time_played DESC
        ->  Hash Join  (cost=11.88..22.20 rows=3 width=12)
              Hash Cond: (games.id = history.game_id)
              ->  Seq Scan on games  (cost=0.00..9.00 rows=500 width=8)
              ->  Hash  (cost=11.84..11.84 rows=3 width=12)
                    ->  Index Scan using history_pkey on history  (cost=0.29..11.84 rows=3 width=12)
                          Index Cond: (user_id = 151500)
```

MY_EXPLANATION:
```
limiting results
    sorting results by last_played or time_played
        using a hashmap to join games and history
            doing a full table scan on games to find the corresponding game to history.game_id
                finding history entries with corresponding user_id
```

No post optimizaiton, because no index is optimal here except games(id) when the table gets larger, but id is a primary key and there is already index for it.



I think adding an index on reviews.updated_at will make it faster because we are doing sequential scans on a large table
CREATE INDEX idx_reviews_updated_at
ON reviews(updated_at);

result: 1005ish ms

There is not much difference in the query plans except for some of the cost numbers but I've tried the pre-optimized and post-optimized queries multiple times and the post-optimized one is noticably faster.
I didn't expect it to be much faster because it still has to check for if individual review's updated dates are within the 30 day interval, but maybe it can find a cutoff day faster.


```
SELECT reviews.game_id, games.genre_id, AVG(reviews.score) as avg_score
FROM reviews
JOIN games on reviews.game_id = games.id
WHERE EXISTS (
    SELECT 1 FROM friends
    WHERE friends.user_adding_id = :user_id
    AND friends.user_added_id = reviews.user_id
)
AND NOW() - reviews.updated_at < INTERVAL '30 days'
GROUP BY reviews.game_id, games.genre_id
ORDER BY avg_score DESC
LIMIT 10
```

PRE_OPTIMIZED:
```
Limit  (cost=6953.93..6953.96 rows=10 width=40)
  ->  Sort  (cost=6953.93..6954.08 rows=60 width=40)
        Sort Key: (avg(reviews.score)) DESC
        ->  GroupAggregate  (cost=6951.29..6952.64 rows=60 width=40)
              Group Key: reviews.game_id, games.genre_id
              ->  Sort  (cost=6951.29..6951.44 rows=60 width=12)
                    Sort Key: reviews.game_id, games.genre_id
                    ->  Nested Loop  (cost=1004.74..6949.51 rows=60 width=12)
                          ->  Gather  (cost=1004.47..6932.09 rows=60 width=8)
                                Workers Planned: 1
                                ->  Hash Join  (cost=4.47..5926.09 rows=35 width=8)
                                      Hash Cond: (reviews.user_id = friends.user_added_id)
                                      ->  Parallel Seq Scan on reviews  (cost=0.00..5767.53 rows=58676 width=12)
                                            Filter: ((now() - updated_at) < '30 days'::interval)
                                      ->  Hash  (cost=4.39..4.39 rows=6 width=4)
                                            ->  Index Only Scan using friends_pkey on friends  (cost=0.29..4.39 rows=6 width=4)
                                                  Index Cond: (user_adding_id = 151500)
                          ->  Index Scan using games_pkey on games  (cost=0.27..0.29 rows=1 width=8)
                                Index Cond: (id = reviews.game_id)
```

POST_OPTIMIZED:
```
Limit  (cost=6962.02..6962.05 rows=10 width=40)
  ->  Sort  (cost=6962.02..6962.17 rows=60 width=40)
        Sort Key: (avg(reviews.score)) DESC
        ->  GroupAggregate  (cost=6959.37..6960.72 rows=60 width=40)
              Group Key: reviews.game_id, games.genre_id
              ->  Sort  (cost=6959.37..6959.52 rows=60 width=12)
                    Sort Key: reviews.game_id, games.genre_id
                    ->  Nested Loop  (cost=1004.74..6957.60 rows=60 width=12)
                          ->  Gather  (cost=1004.47..6940.18 rows=60 width=8)
                                Workers Planned: 1
                                ->  Hash Join  (cost=4.47..5934.18 rows=35 width=8)
                                      Hash Cond: (reviews.user_id = friends.user_added_id)
                                      ->  Parallel Seq Scan on reviews  (cost=0.00..5775.23 rows=58824 width=12)
                                            Filter: ((now() - updated_at) < '30 days'::interval)
                                      ->  Hash  (cost=4.39..4.39 rows=6 width=4)
                                            ->  Index Only Scan using friends_pkey on friends  (cost=0.29..4.39 rows=6 width=4)
                                                  Index Cond: (user_adding_id = 101500)
                          ->  Index Scan using games_pkey on games  (cost=0.27..0.29 rows=1 width=8)
                                Index Cond: (id = reviews.game_id)
```

MY_EXPLANATION:
```
limiting results
    sort by reviews.score
        aggregate game_id and genre_id
            different processes doing:
                using hashmap to join reviews and friends to get reviews written by friends
                do a full table scan on reviews to find reviews within 30 days
                    using index to find user's friends
            using index to get its genre_id from reviews.game_id
```



```
SELECT reviews.game_id, games.genre_id, AVG(reviews.score) as avg_score
FROM reviews
JOIN games on reviews.game_id = games.id
WHERE NOW() - reviews.updated_at < INTERVAL '30 days'
GROUP BY reviews.game_id, games.genre_id
HAVING COUNT(reviews.score) >= 1
ORDER BY avg_score DESC
LIMIT 10
```

PRE_OPTIMIZED:
```
Sort Key: (avg(reviews.score)) DESC
->  Finalize HashAggregate  (cost=8184.86..8267.36 rows=1833 width=40)
      Group Key: reviews.game_id, games.genre_id
      Filter: (count(reviews.score) >= 1)
      ->  Gather  (cost=7524.86..8129.86 rows=5500 width=48)
            Workers Planned: 1
            ->  Partial HashAggregate  (cost=6524.86..6579.86 rows=5500 width=48)
                  Group Key: reviews.game_id, games.genre_id
                  ->  Hash Join  (cost=15.25..5938.10 rows=58676 width=12)
                        Hash Cond: (reviews.game_id = games.id)
                        ->  Parallel Seq Scan on reviews  (cost=0.00..5767.53 rows=58676 width=8)
                              Filter: ((now() - updated_at) < '30 days'::interval)
                        ->  Hash  (cost=9.00..9.00 rows=500 width=8)
                              ->  Seq Scan on games  (cost=0.00..9.00 rows=500 width=8)
```

POST_OPTIMIZED:
```
Limit  (cost=8316.55..8316.58 rows=10 width=40)
  ->  Sort  (cost=8316.55..8321.13 rows=1833 width=40)
        Sort Key: (avg(reviews.score)) DESC
        ->  Finalize HashAggregate  (cost=8194.44..8276.94 rows=1833 width=40)
              Group Key: reviews.game_id, games.genre_id
              Filter: (count(reviews.score) >= 1)
              ->  Gather  (cost=7534.44..8139.44 rows=5500 width=48)
                    Workers Planned: 1
                    ->  Partial HashAggregate  (cost=6534.44..6589.44 rows=5500 width=48)
                          Group Key: reviews.game_id, games.genre_id
                          ->  Hash Join  (cost=15.25..5946.20 rows=58824 width=12)
                                Hash Cond: (reviews.game_id = games.id)
                                ->  Parallel Seq Scan on reviews  (cost=0.00..5775.23 rows=58824 width=8)
                                      Filter: ((now() - updated_at) < '30 days'::interval)
                                ->  Hash  (cost=9.00..9.00 rows=500 width=8)
                                      ->  Seq Scan on games  (cost=0.00..9.00 rows=500 width=8)
```

MY_EXPLANATION:
```
using a hashmap for aggregation functions on game_id and genre_id
    filtering results that have at least x reviews
        each process does a bit of a hashaggregate
            using a hashmap to join reviews and games
                each process does a part of a sequential scan to find reviews in the last 30 days
                    scanning full games table to find corresponding game to the review
```





