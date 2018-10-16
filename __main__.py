from openlab_automata import OpenLabAutomata

print('''本程序用于自动完成openlab的选择、填空题\n于深职院考试平台（锐格软件）测试通过\n深职院用户主机项请留空''')

map_type = {
    '0': '[选择题]',
    '1': '[填空题]',
    '2': '[编程题]',
}

host = input('主机:')
username = input('用户名:')
password = input('密码:')

if host == '':
    host = '112.64.141.46:8071'

client = OpenLabAutomata(host)
if client.login(username, password):
    print(client.user)
    for i in client.classes:
        print(i)

    if len(client.classes) == 1:
        class_id = client.classes[0]['id']
    else:
        class_id = input('输入班级id:')

    root_nodes = client.get_exercise_root_nodes(class_id)

    print('加载题目中...')
    nodes_all = client.get_exercise_nodes_all(root_nodes[0])

    for node in nodes_all:
        if node['type'] == 'exercise':
            type_str = map_type.get(node['etype'], '[未知类型]')
            if node['correct_sign'] == 0:
                result = False
                if node['etype'] == '0':
                    result = client.submit_select(node['pId'], node['realId'], node['myscore'], class_id,
                                                  node['answerNum'])
                elif node['etype'] == '1':
                    result = client.submit_fill(node['pId'], node['realId'], node['myscore'], class_id)
                elif node['etype'] == '2':
                    result = client.submit_program(node['pId'], node['realId'], node['myscore'], class_id)

                if result:
                    print('[已完成]', type_str, node['name'])
                else:
                    print('[不支持]', type_str, node['name'])
            else:
                pass
                # print('[已完成,忽略]', type_str, node['name'])
        else:
            print(node['name'])
