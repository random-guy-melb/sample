import requests
from datetime import datetime
import time
import random
import re

def unix_timestamp(dt):
    """Convert a datetime object to a Unix timestamp."""
    return int(dt.timestamp())

def make_request_with_backoff(client, url, params, max_retries=5, initial_backoff=1):
    """Make a request with exponential backoff for rate limiting."""
    for attempt in range(max_retries):
        try:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Too Many Requests
                if attempt < max_retries - 1:
                    backoff_time = initial_backoff * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Rate limited. Retrying in {backoff_time:.2f} seconds...")
                    time.sleep(backoff_time)
                else:
                    print("Max retries reached. Skipping this request.")
                    return None
            else:
                print(f"HTTP Error: {e}")
                return None
        except requests.RequestException as e:
            print(f"Request Error: {e}")
            return None

def fetch_replies(client, channel_id, thread_ts):
    """Fetch all replies for a given thread."""
    replies_url = 'https://slack.com/api/conversations.replies'
    replies_params = {
        'channel': channel_id,
        'ts': thread_ts
    }
    data = make_request_with_backoff(client, replies_url, replies_params)
    if data and data['ok']:
        return data['messages'][1:]  # Exclude the parent message
    return []

def fetch_users(client):
    """Fetch all users in the workspace."""
    users_url = 'https://slack.com/api/users.list'
    users = {}
    cursor = None
    while True:
        params = {'limit': 200}
        if cursor:
            params['cursor'] = cursor
        data = make_request_with_backoff(client, users_url, params)
        if data and data['ok']:
            for member in data['members']:
                users[member['id']] = member['real_name']
            if data.get('response_metadata', {}).get('next_cursor'):
                cursor = data['response_metadata']['next_cursor']
            else:
                break
        else:
            print("Error fetching users. Some user IDs may not be resolved.")
            break
    return users

def fetch_channels(client):
    """Fetch all channels in the workspace."""
    channels_url = 'https://slack.com/api/conversations.list'
    channels = {}
    cursor = None
    while True:
        params = {'limit': 200, 'types': 'public_channel,private_channel'}
        if cursor:
            params['cursor'] = cursor
        data = make_request_with_backoff(client, channels_url, params)
        if data and data['ok']:
            for channel in data['channels']:
                channels[channel['id']] = channel['name']
            if data.get('response_metadata', {}).get('next_cursor'):
                cursor = data['response_metadata']['next_cursor']
            else:
                break
        else:
            print("Error fetching channels. Some channel IDs may not be resolved.")
            break
    return channels

def fetch_usergroups(client):
    """Fetch all user groups in the workspace."""
    usergroups_url = 'https://slack.com/api/usergroups.list'
    usergroups = {}
    data = make_request_with_backoff(client, usergroups_url, {})
    if data and data['ok']:
        for group in data['usergroups']:
            usergroups[group['id']] = group['handle']
    else:
        print("Error fetching user groups. Some user group IDs may not be resolved.")
    return usergroups

def resolve_names(text, users, channels, usergroups):
    """Replace user, channel, and user group IDs with their respective names."""
    def replace_id(match):
        id = match.group(1)
        if id.startswith('U'):
            return f"@{users.get(id, id)}"
        elif id.startswith('C'):
            return f"#{channels.get(id, id)}"
        elif id.startswith('S'):
            return f"@{usergroups.get(id, id)}"
        return match.group(0)
    
    return re.sub(r'<(@U\w+|#C\w+|!subteam\^S\w+)>', replace_id, text)

# Replace with your actual Slack bot token
slack_token = 'YOUR_SLACK_BOT_TOKEN'

# Replace with your actual channel ID
channel_id = 'C04TSF0'

# Set your date range
start_date = datetime(2024, 9, 1)  # Year, Month, Day
end_date = datetime(2024, 9, 18)   # Year, Month, Day

# Convert to Unix timestamps
oldest = unix_timestamp(start_date)
latest = unix_timestamp(end_date)

# Base API URL
base_url = 'https://slack.com/api/conversations.history'

# Parameters for the API request
params = {
    'channel': channel_id,
    'oldest': oldest,
    'latest': latest,
    'limit': 100  # Adjust as needed
}

# Headers for authentication
headers = {
    'Authorization': f'Bearer {slack_token}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Create a session for more efficient requests
session = requests.Session()
session.headers.update(headers)

# Fetch users, channels, and user groups
print("Fetching user information...")
users = fetch_users(session)
print("Fetching channel information...")
channels = fetch_channels(session)
print("Fetching user group information...")
usergroups = fetch_usergroups(session)

all_threads = []

while True:
    data = make_request_with_backoff(session, base_url, params)
    
    if data and data['ok']:
        for message in data['messages']:
            thread = [message]
            if message.get('thread_ts'):
                # This message has replies, fetch them
                replies = fetch_replies(session, channel_id, message['ts'])
                thread.extend(replies)
            all_threads.append(thread)
        
        # Check if there are more messages
        if data.get('has_more'):
            params['latest'] = data['messages'][-1]['ts']
        else:
            break  # No more messages, exit the loop
    else:
        print("Error fetching messages. Exiting.")
        break

# Print threads with resolved names
for thread in all_threads:
    user_id = thread[0].get('user', 'Unknown')
    user_name = users.get(user_id, user_id)
    print(f"Thread started by: {user_name}")
    print(f"Original message: {resolve_names(thread[0]['text'], users, channels, usergroups)}")
    print(f"Timestamp: {thread[0]['ts']}")
    if len(thread) > 1:
        print("Replies:")
        for reply in thread[1:]:
            reply_user_id = reply.get('user', 'Unknown')
            reply_user_name = users.get(reply_user_id, reply_user_id)
            print(f"  User: {reply_user_name}")
            print(f"  Message: {resolve_names(reply['text'], users, channels, usergroups)}")
            print(f"  Timestamp: {reply['ts']}")
    print("---")

print(f"Total threads retrieved: {len(all_threads)}")
