import requests
import sys
from vk_auth import get_vk_session


def check_args():
    if len(sys.argv) == 1:
        return None
    elif len(sys.argv) > 2:
        print('Too much arguments for the script')
    elif not str(sys.argv[1]).isdigit():
        print('Argument must be an id (digit)!')
    else:
        return sys.argv[1]
    sys.exit()


def get_friends_online_list(id_for_searching, api):
    if id_for_searching:
        online_friends = api.friends.getOnline(user_id=id_for_searching, online_mobile=1, order='hints', v='5.63')
    else:
        online_friends = api.friends.getOnline(online_mobile=1, order='hints', v='5.63')
    return online_friends


def make_request_to_vk(method, parameters):
    url = 'https://api.vk.com/method/%s?' % method
    for key in parameters:
        items = ''
        if type(parameters[key]) == list or type(parameters[key]) == set:
            for item in parameters[key]:
                items += '%s,' % item
            parameter = '%s=%s' % (key, items[:-1])
        else:
            parameter = '%s=%s' % (key, parameters[key])
        url += '%s&' % parameter
    return url[:-1]


def online_friends_output(online_friends_ids, token):
    if 'error' in founded_friends_ids:
        print(founded_friends_ids['error']['error_msg'])
        sys.exit()
    online_friends = {}
    for mode in online_friends_ids:
        # doesn't work with list(
        # vk.users.get(user_ids=online_friends_ids[mode], v='5.63')

        # works, but slowly
        # for user_id in online_friends_ids[mode]:
        #     online_friends.extend(vk.users.get(user_ids=user_id, v='5.63'))

        # So, there is only one way...
        # Use make_request_to_vk because if i send to request.get params list with ids,
        #  it will be the same as in vk.users.get
        url_for_request = make_request_to_vk(method='users.get',
                                             parameters={'user_ids': online_friends_ids[mode], 'v': '5.63',
                                                         'access_token': token})
        response = requests.get(url=url_for_request).json()
        online_friends[mode] = response['response']

    for mode in sorted(online_friends):
        if mode == 'online':
            print('Online:')
        elif mode == 'online_mobile':
            print('Online from mobile:')
        else:
            print('Something else:')
        if len(online_friends[mode]) == 0:
            print('\t', 'Nobody(')
        else:
            for friend in online_friends[mode]:
                print('\t', friend['first_name'], friend['last_name'], '\t:\t',  'https://vk.com/id%d' % friend['id'])
        print()


if __name__ == '__main__':
    id_for_searching = check_args()
    vk_session = get_vk_session('auth_data.json', 2)
    vk_session.auth()
    vk = vk_session.get_api()
    founded_friends_ids = get_friends_online_list(id_for_searching, vk)
    online_friends_output(founded_friends_ids, vk_session.token['access_token'])
