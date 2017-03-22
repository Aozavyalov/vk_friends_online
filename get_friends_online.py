import vk_api
import requests
import sys
import json


def json_data_check(json_data, keys):
    if json_data == {}:
        for key in keys:
            print('Input %s:' % key)
            json_data[key] = input()
    return json_data


def read_json(filename):
    try:
        with open(filename, 'r') as read_file:
            json_data = json.load(read_file)
    except FileNotFoundError:
        return {}
    except json.decoder.JSONDecodeError:
        return {}
    return json_data


def get_auth_data_for_token():
    app_auth_data = read_json('auth_data.json')
    app_auth_data = json_data_check(app_auth_data, ['app_id', 'secure_key'])
    return app_auth_data


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
        online_friends = api.friends.getOnline(user_id=id_for_searching, online_mobile=1, v='5.63')
    else:
        online_friends = api.friends.getOnline(online_mobile=1, v='5.63')
    return online_friends


def captcha_handler(captcha):
    key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
    # Пробуем снова отправить запрос с капчей
    return captcha.try_again(key)


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
                print('\t', friend['first_name'], friend['last_name'], '\t',  'https://vk.com/id%d' % friend['id'])


if __name__ == '__main__':
    id_for_searching = check_args()
    auth_data = get_auth_data_for_token()
    vk_session = vk_api.VkApi(app_id=auth_data['app_id'], login=auth_data['login'], password=auth_data['password'],
                              scope='2', token=auth_data['service_token'], captcha_handler=captcha_handler,
                              api_version='5.63')
    vk_session.auth()
    vk = vk_session.get_api()
    founded_friends_ids = get_friends_online_list(id_for_searching, vk)
    online_friends_output(founded_friends_ids, vk_session.token['access_token'])
