import requests

usernames = ['hannahann_sluss', 'vlfuller']

search_string = '"edge_followed_by":{"count":'
for username in usernames:
    response = requests.get(f'https://www.instagram.com/{username}/')
    index1 = response.text.find(search_string) + len(search_string)
    index2 = response.text.find('}', index1)
    follower_count = response.text[index1:index2]
    print(f'{username}: {follower_count}')
