def load_from_api(id, page, division):
    from decouple import config

    import requests
    import json

    params = {'affiliate': id, 'page': page, 'division': division}

    response = requests.get(config('OPEN_URL'), params=params)
    content = json.loads(response.text)

    pagination = content.get('pagination', None)
    total_pages = pagination.get('totalPages') if pagination else 0

    return content.get('leaderboardRows', []), total_pages
