import requests
import json
import os

from config.twitter_creds import (
    CONSUMER_KEY,
    CONSUMER_SECRET,
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET,
    BEARER_TOKEN,
)
from requests_oauthlib import OAuth1


OAUTH = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)


def get_tweets_with_text(text: str):
    """Query twitters search API for tweets with specific text"""

    endpoint = "https://api.twitter.com/2/tweets/search/recent"
    headers = {"authorization": f"Bearer {BEARER_TOKEN}"}
    params = {
        "query": text,
        "tweet.fields": "created_at,lang,author_id,conversation_id,referenced_tweets",
        "max_results": "100",  # Max is 100
    }

    # HTTP VERBS: POST, PUT, DELETE, HEAD, and OPTIONS.
    # GET request
    response = requests.get(endpoint, params=params, headers=headers)
    tweets = response.json()["data"]

    authors = []
    # Collect all author ids to block
    for tweet in tweets:
        authors.append(tweet["author_id"])

    return authors


def get_info_on_users(users: list, description_keywords: list):
    """From a list of user IDs get a subset based on the users description"""

    author_ids_as_string = ",".join(users)
    endpoint = "https://api.twitter.com/2/users"
    headers = {"authorization": f"Bearer {BEARER_TOKEN}"}
    params = {"ids": author_ids_as_string, "user.fields": "description,created_at"}

    response = requests.get(endpoint, params=params, headers=headers)
    user_profiles = response.json()["data"]

    # Check description of user for more confident match
    accounts_of_interest = []
    for user in user_profiles:
        description = user["description"].lower()
        if any(keyword in description for keyword in description_keywords):
            accounts_of_interest.append(user["id"])

    return accounts_of_interest


def block_users(user_ids: list):

    for user_id in user_ids:
        endpoint = "https://api.twitter.com/1.1/blocks/create.json"
        params = {"user_id": user_id}

        response = requests.post(endpoint, params=params, auth=OAUTH)
        user_profile = response.json()
        print(user_profile["name"])

        # Save blocked user info
        with open(os.path.join("blocked_users", f"{user_id}.json"), "w") as f:
            json.dump(user_profile, f)


def main():
    tweet_authors = get_tweets_with_text("#Tag")
    accounts_of_interest = get_info_on_users(
        tweet_authors, ["stuff1", "stuff2", "stuff3"]
    )
    block_users(accounts_of_interest)


if __name__ == "__main__":
    main()
