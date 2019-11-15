import sys
import requests

base_url = "https://api.trello.com/1/{}"
auth_params = {
    'key': "",
    'token': "", }
board_id = ""
long_board_id = ''


def read():
    # Получим данные всех колонок на доске:
    # print(base_url.format('boards') + '/' + board_id + '/lists')
    column_data = requests.get(base_url.format('boards') + '/' + long_board_id + '/lists', params=auth_params).json()

    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:
    for column in column_data:
        print('Список "{}" '.format(column['name']), end='')
        # Получим данные всех задач в колонке и перечислим все названия
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        print(' - количество задач: {} '.format(len(task_data)))
        if not task_data:
            print('\t' + 'Нет задач!')
            continue
        for task in task_data:
            print('\t' + task['name'])


def create(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна
    for column in column_data:
        # print(column)
        if column['name'] == column_name:
            # Создадим задачу с именем _name_ в найденной колонке
            response = requests.post(base_url.format('cards'),
                                     data={'name': name, 'idList': column['id'], **auth_params}).json()
            if response['id']:
                print('Задача "{}" создана'.format(response['name']))
            break


def create_list(name):
    # создание новой колонки
    # проверяем, есть ли колонка с таким названием
    column_data = requests.get(base_url.format('boards') + '/' + long_board_id + '/lists', params=auth_params).json()
    for column in column_data:
        if column['name'] == name:
            print("Колонка с подобным названием уже существует")
            return

    response = requests.post(base_url.format('lists'),
                             data={'name': name, 'idBoard': long_board_id, **auth_params}).json()
    if response['id']:
        print('Колонка "{}" создана'.format(response['name']))


def move(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Среди всех колонок нужно найти задачу по имени и получить её id
    task_list = []
    for column in column_data:
        # print(column['name'])
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == name:
                task_list.append({
                    'task_id': task['id'],
                    'task_name': task['name'],
                    'column_name': column['name']
                })
                # break
        # if task_id:
        #     break
    task_id = None
    if len(task_list) == 0:
        print('Задача "{}" не найдена'.format(name))
    elif len(task_list) == 1:
        task_id = task_list[0]['task_id']
    else:
        print('Задача "{}" найдена в нескольких карточках. '
              'Выберете нужную карточку. Нажмите цифру с нужным порядковым номером'.format(name))
        i = 1
        for item in task_list:
            print(i, item['column_name'])
            i += 1
        i = int(input('Нажмите цифру с нужным порядковым номером ')) - 1
        task_id = task_list[i]['task_id']
        # print(task_list[i])

    if task_id:
        # Теперь, когда у нас есть id задачи, которую мы хотим переместить
        # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу
        for column in column_data:
            if column['name'] == column_name:
                # И выполним запрос к API для перемещения задачи в нужную колонку
                requests.put(base_url.format('cards') + '/' + task_id + '/idList',
                             data={'value': column['id'], **auth_params})
                break


def find_all_cards():
    # Получим данные всех колонок на доске
    response = requests.get(base_url.format('boards') + '/' +
                            long_board_id + '/cards', params=auth_params).json()
    for it in response:
        print(it['name'])
        print(it['id'])
        print(it['idBoard'])
        print(it['idList'])


if __name__ == "__main__":
    if len(sys.argv) <= 2:
        read()
    elif sys.argv[1] == 'create':
        create(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'create_list':
        create_list(sys.argv[2])
    elif sys.argv[1] == 'find_all_cards':
        find_all_cards()
