import vk_api
import json


def get_auth_data_from_json(filename):
    app_auth_data = read_json(filename)
    app_auth_data = json_data_check(app_auth_data, ['app_id', 'service_token', 'login', 'password'])
    return app_auth_data


def json_data_check(json_data, keys):
    for key in keys:
        if key not in json_data:
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


def captcha_handler(captcha):
    key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
    # Пробуем снова отправить запрос с капчей
    return captcha.try_again(key)


def get_vk_session(file_with_auth_data, scope=1, api_version='5.63'):
    auth_data = get_auth_data_from_json(file_with_auth_data)
    vk_session = vk_api.VkApi(app_id=auth_data['app_id'], login=auth_data['login'], password=auth_data['password'],
                              scope=scope, token=auth_data['service_token'], captcha_handler=captcha_handler,
                              api_version=api_version)
    return vk_session


if __name__ == '__main__':
    get_vk_session('auth_data.json', 2)
