# -*- coding: UTF-8 -*-
# формирование web_reg_save_param

import copy
import time
import random
import string

from lr_lib import (
    defaults,
    pool as lr_pool,
    other as lr_other,
    logger as lr_log,
)


LR_COMENT = '//lr:'

# имя web_reg_save_param - P_число__inf_номера_запросов__и_скомый_para_m
WEB_REG_NUM = 'P_{wrsp_rnd_num}_{infs}_{lb_name}__{wrsp_name}__{rb_name}'


web_reg_save_param = '''
// INF{inf_nums}, [t{param_inf_min}:t{param_inf_max}]={search_inf_len} -> [t{_param_inf_min}:t{_param_inf_max}]={_param_inf_all} | FILE["{Name}"], with_param = {file_index}/{param_files} | {create_time}
// PARAM["{param_Name}"], count={param_part}/{param_count}, NA={param_NotPrintable} | LB[{Lb_len}~{lb_len}] NA={lb_NotPrintable}, RB[{Rb_len}~{rb_len}] NA={rb_NotPrintable}
web_reg_save_param("{web_reg_num}",
    "LB={lb}",
    "RB={rb}",
    "Ord={param_ord}",
    "Search={search_key}",
    LAST); 
'''

# !!! при редактировании web_reg_save_param, учесть что придется изменить wrsp_start/end, чтобы при автозамене, не заменялся param в коментарии // PARAM[{param_Name}], и тд
wrsp_file_start = '| FILE["'
wrsp_file_end = '"],'

wrsp_LB_start = '"LB='
wrsp_LB_end = '",\n'
wrsp_RB_start = '"RB='
wrsp_RB_end = '",\n'

wrsp_start = '// PARAM["'
wrsp_end = '"'
wrsp_start_end = '// PARAM["{param_Name}"]'

wrsp_lr_start = 'web_reg_save_param("'
wrsp_lr_end = '",'

_block_startswith = 'web_'
_block_endswith = '",'
_block_endswith2 = '("'
_block_endswith3 = '");'

Snap1 = '"Snapshot=t'
Snap2 = '.inf",'
Snap = '%s{num}%s' % (Snap1, Snap2)
Web_LAST = 'LAST);'


def param_bounds_setter(param: str, start='{', end='}') -> str:
    '''web_reg_save_param имя "P_1212_2_z_kau_1" -> {} '''
    if not param.startswith(start):
        param = start + param
    if not param.endswith(end):
        param += end
    return param


def create_web_reg_save_param(wrsp_dict=None) -> str:
    '''сформировать web_reg_save_param'''
    if wrsp_dict is None:
        wrsp_dict = defaults.VarWrspDict.get()
    else:
        defaults.VarWrspDict.set(wrsp_dict)

    return web_reg_save_param.format(**wrsp_dict)


wrsp_allow_symb = string.ascii_letters + string.digits + '_!-'  # из каких символов, может состоять param
allow_lrb = set(string.ascii_letters + string.digits)  # из каких символов, может состоять lb rb части имени web_reg_save_param
wrsp_deny_punctuation = {ord(c): '' for c in string.punctuation.replace('_', '')}  # из каких символов, не может состоять имя web_reg_save_param
wrsp_deny_punctuation.update({ord(c): '' for c in string.whitespace})  # из каких символов, не может состоять имя web_reg_save_param


def wrsp_dict_creator(is_param=True) -> dict:
    '''сформировать данные для web_reg_save_param'''
    all_infs = tuple(lr_other.get_files_infs(defaults.AllFiles))
    param_infs = tuple(lr_other.get_files_infs(defaults.FilesWithParam))
    len_param_files = len(defaults.FilesWithParam)
    file = defaults.VarFile.get()
    param_num = defaults.VarPartNum.get() + 1  # нумерация с 0
    param_count = file['Param']['Count']
    Lb = defaults.VarLB.get()
    Rb = defaults.VarRB.get()

    # экранирование
    lb = screening_wrsp(Lb)
    rb = screening_wrsp(Rb)

    param = defaults.VarParam.get()
    if is_param:
        param_ord, param_index = find_param_ord()
    else:
        param_ord, param_index = -1, -1

    if len(Lb) > 2:
        lb_name = ['']
        for b in Lb:
            if b in allow_lrb: lb_name[-1] += b
            elif lb_name[-1]: lb_name.append('')
        lb_name = [b for b in filter(bool, lb_name) if b not in defaults.LRB_rep_list]
        lb_name = '_'.join(sorted(set(lb_name), key=lb_name.index))[-defaults.MaxRbWrspName:]
    else:
        lb_name = ''

    if len(Rb) > 2:
        rb_name = ['']
        for b in Rb:
            if b in allow_lrb: rb_name[-1] += b
            elif rb_name[-1]: rb_name.append('')
        rb_name = [b for b in filter(bool, rb_name) if b not in defaults.LRB_rep_list]
        rb_name = '_'.join(sorted(set(rb_name), key=rb_name.index))[:defaults.MaxRbWrspName]
    else:
        rb_name = ''

    # Печатные символы искомого param(1), войдут в имя для web_reg_save_param(6), втозамена не должна затронуть имя параметра
    wn = [s for s in param  if s in allow_lrb]
    w2 = ''.join(wn[1:-1])
    wrsp_name = '{w1}_{w2}_{w3}'.format(w2=w2, w1=wn[0], w3=wn[-1])[:defaults.MaxParamWrspName + 2]
    wrsp_name = WEB_REG_NUM.format(
        wrsp_rnd_num=random.randrange(defaults.MinWrspRnum, defaults.MaxWrspRnum), wrsp_name=wrsp_name,
        lb_name=lb_name, rb_name=rb_name, infs='_'.join(map(str, file['Inf']['Nums'])))
    wrsp_name = str.translate(wrsp_name, wrsp_deny_punctuation).replace('___', '__')
    while wrsp_name.endswith('_'):
        wrsp_name = wrsp_name[:-1]

    search_key = 'All'
    # if file['Inf']['inf_key'] == 'ResponseHeaderFile':
    #     search_key = 'Headers'

    web_reg_save_param_dict = dict(
        lb=lb,
        rb=rb,
        param_ord=param_ord,
        web_reg_num=wrsp_name,
        param_part=param_num,
        param_count=param_count,
        param_files=len_param_files,
        file_index=defaults.FilesWithParam.index(file) + 1,
        files_all=len(defaults.AllFiles),
        param_all=sum(f['Param']['Count'] for f in defaults.FilesWithParam),
        create_time=time.strftime('%H:%M:%S-%d/%m/%y'),
        inf_nums=file['Inf']['Nums'],
        Lb_len=len(Lb),
        Rb_len=len(Rb),
        lb_len=len(lb),
        rb_len=len(rb),
        lb_NotPrintable=lr_other.not_printable(lb),
        rb_NotPrintable=lr_other.not_printable(rb),
        param_text_index=param_index,
        all_inf_min=min(all_infs),
        all_inf_max=max(all_infs),
        all_inf_len=len(all_infs),
        _param_inf_min=min(param_infs),
        _param_inf_max=max(param_infs),
        _param_inf_all=len(param_infs),
        search_key=search_key,
        param=param,
    )

    m1, m2 = file['Param']['inf_min'], file['Param']['inf_max']
    web_reg_save_param_dict['search_inf_len'] = len(list(i for i in all_infs if m1 <= i <= m2))
    # file['File'] ключи
    web_reg_save_param_dict.update(file['File'])
    # param_* ключи - file['Param']
    web_reg_save_param_dict.update({'param_{}'.format(k): v for k, v in file['Param'].items()})

    return web_reg_save_param_dict


def screening_wrsp(s: str, t={ord(c): '\\{}'.format(c) for c in defaults.Screening}) -> str:
    '''экранирование для web_reg_save_param'''
    return str.translate(s, t)


def _search_param_in_file(file: dict) -> dict:
    '''найти кол-во {param} в файле, count - те все, без проверки на корректность'''
    File = file['File']
    Param = file['Param']
    param = Param['Name']

    with open(File['FullName'], encoding=File['encoding'], errors='ignore') as text:
        count = sum(line.count(param) for line in text)
        if count:
            Param['Count'] = count
            return file


def search_param_in_file(file: dict) -> (dict or None):
    '''найти кол-во {param} в файле, с контролем LB RB'''
    File = file['File']
    Param = file['Param']
    param = Param['Name']
    Param['Count'] = 0
    Param['Count_indexs'] = []

    with open(File['FullName'], encoding=File['encoding'], errors='ignore') as text:
        # for line in text:
        split_line = text.read().split(param)
        split_len = len(split_line)
        if split_len < 2:
            return

        indx = 0
        for indx in range(1, split_len):
            i = indx - 1
            left = split_line[i]
            right = split_line[indx]
            if lr_other.check_bound_lb_rb(left, right):
                Param['Count_indexs'].append(i)

    if Param['Count_indexs']:
        Param['Count'] = indx
        Param['Count_indexs_len'] = len(Param['Count_indexs'])
        return file


def create_files_with_search_data(files: (dict, ), search_data: dict, action=None, action_infs=()) -> iter((dict,)):
    '''с учетом inf - создать копию файла и обновить search_data'''
    d = search_data['Param']
    inf_min = d['inf_min']
    inf_max = d['inf_max']

    if action:
        d['action_id'] = action.id_
        action_infs = action.action_infs

        inf_min = d['inf_min'] = min(action_infs or [-1])
        inf_max = d['inf_max'] = max(action_infs or [-1])
        d['max_action_inf'] = param_inf = set_param_in_action_inf(action, d['Name'])
        if not action.add_inf_cbx_var.get():
            param_inf -= 1  # inf, педшествующий номеру inf, где первый раз встречается pram
        if action.max_inf_cbx_var.get() and param_inf and (inf_max > param_inf):
            inf_max = d['inf_max'] = param_inf

    for __file in files:
        inf_list = []

        for n in __file['Inf']['Nums']:
            if ((n in action_infs) or (not action_infs)) and (inf_min <= n <= inf_max):
                inf_list.append(n)

        if inf_list:
            file = copy.deepcopy(__file)  # не изменять оригинальный файл
            file['Inf']['Nums'] = sorted(inf_list)
            for data in search_data:  # обновить(не заменить) ключи
                file[data].update(search_data[data])

            yield file

def set_param_in_action_inf(action, param: str) -> int:
    '''первый action-inf в котором расположен param, тк inf-номер запроса <= inf-номер web_reg_save_param'''
    for web_ in action.web_action.get_web_snapshot_all():
        allow, deny = web_.param_find_replace(param)
        if allow:
            return web_.snapshot
    return 0

def get_files_with_param(param: str, action=None, set_file=True) -> None:
    '''найти файлы с param'''
    param = param or defaults.VarParam.get()
    search_data = dict(
        Param=dict(
            Name=param,
            inf_min=defaults.VarSearchMinInf.get(),
            len=(len(param) if hasattr(param, '__len__') else None),
            inf_max=defaults.VarSearchMaxInf.get(),
            NotPrintable=lr_other.not_printable(param),
        ),
        File=dict(
            encoding=defaults.VarEncode.get(),
        ),
    )  # данные, для поиска param в AllFiles

    files = tuple(create_files_with_search_data(defaults.AllFiles, search_data, action=action))
    assert files, 'Не найдены файлы, подходящие, под условия поиска. {a}\nsearch_data: {d}'.format(d=search_data, a=action)
    param_searcher = search_param_in_file if defaults.VarStrongSearchInFile.get() else _search_param_in_file
    map_executer = lr_pool.M_POOL.imap_unordered if defaults.FindParamPOOLEnable else map

    defaults.FilesWithParam = sorted(filter(bool, map_executer(param_searcher, files)), key=lr_other.sort_by_file_keys)

    if not defaults.FilesWithParam:
        if action: lai, a_min, a_max, afa = (len(action.action_infs), min(action.action_infs), max(action.action_infs), (len(defaults.AllFiles) - len(action.drop_files)))
        else: lai = a_min = a_max = afa = None
        raise UserWarning('Не найдены файлы содержащие param "{param}"\n\nsearch_data: {d}\n\nВсего Snapshot {i}=[ t{ai_min}:t{ai_max} ]/файлов={f}\nВ action.c: Snapshot {ai}=[ t{a_min}:t{a_max} ] / Файлов={afa}\nПоиск происходил в: Snapshot {lf}=[ t{min_iaf}:t{max_iaf} ] / файлах={f_}\nДиректория поиска: {folder}\nоткл чекб "strong", вероятно может помочь найти варианты'.format(
            ai_min=min(tuple(lr_other.get_files_infs(defaults.AllFiles))), ai=lai, afa=afa, ai_max=max(lr_other.get_files_infs(defaults.AllFiles)), folder=defaults.VarFilesFolder.get(), min_iaf=files[0]['Param']['inf_min'], max_iaf=files[0]['Param']['inf_max'], a_min=a_min, a_max=a_max, d=search_data, f=len(defaults.AllFiles), f_=len(files), lf=len(tuple(lr_other.get_files_infs(files))), param=param, i=len(tuple(lr_other.get_files_infs(defaults.AllFiles)))))

    if set_file:
        file = defaults.FilesWithParam[-1 if defaults.VarFirstLastFile.get() else 0]
        defaults.VarFileName.set(file['File']['Name'])

    if defaults.VarFileNamesNumsShow.get():
        lr_log.Logger.info(lr_other.param_files_info())


def find_param_ord() -> (int, int):
    '''получить Ord'''
    if defaults.VarOrdVersion.get():
        ord_index = new_find_param_ord()
    else:  # можно сравнить результат, при изменении алгоритма
        ord_index = old_find_param_ord()

    if ord_index:
        return ord_index

    raise UserWarning('Ord не найден\n{f}\n{w}'.format(f=defaults.VarFile.get(), w=defaults.VarWrspDict.get()))


def new_find_param_ord() -> (int, int):
    '''получить Ord, версия после 7.2.0'''
    items = param, lb, rb, text = (defaults.VarParam.get(), defaults.VarLB.get(), defaults.VarRB.get(),
                                   defaults.VarFileText.get())
    lb_text_index = [len(part) for part in text.split(lb)]  # индексы для определения param в тексте
    len_lbti = len(lb_text_index)

    assert all(items), 'Формирование Ord для web_reg_save_param невозможно, тк поле пусто\n[param, lb, rb, text] == {empty}\nVarWrspDict={wrsp}\nVarPartNum={pn}, max={len_lbti}\nVarFile={fl}'.format(
        wrsp=defaults.VarWrspDict.get(), empty=list(map(bool, items)), pn=defaults.VarPartNum.get(), len_lbti=len_lbti, fl=defaults.VarFile.get(),)

    assert len_lbti > 1, 'Формирование web_reg_save_param невозможно, тк файл не содержит LB(5)\n{wrsp}'.format(
        wrsp=defaults.VarWrspDict.get())

    Ord, index = 0, 0  # искомый Ord, текущий LB index
    iter_index = iter(lb_text_index)  # следующий LB index
    next(iter_index, None)  # тк следующий
    param_rb = param + rb
    param_rb_len, len_lb = len(param_rb), len(lb)

    for i in lb_text_index:
        index += (i + len_lb)  # нижняя граница
        add_index = next(iter_index, 0)  # верхняя граница
        if add_index < param_rb_len:  # увеличить add_index, если символы LB(начало) и RB(конец) пересекаются(при достаточной defaults.VarMaxLen), те если близко расположены два param, RB не должно быть обрезано, например для text с param = Des8: 'cms;session=1qpxcc3g?tid=Des8" url="http://aaa.bb/cms;session=1qpxcc3g?tid=Des8"'
            add_index = param_rb_len

        part = text[index:index+add_index]  # text[текущий : следующий] LB index
        if rb in part:
            Ord += 1
            if part.startswith(param_rb):
                return Ord, index


def old_find_param_ord() -> (int, int):
    '''получить Ord, версия до 7.2.0 - не ищет ord если символы LB(начало) и RB(конец) пересекаются'''
    lb = defaults.VarLB.get()
    assert lb, 'Формирование web_reg_save_param невозможно, тк поле LB(5) пусто'
    rb = defaults.VarRB.get()
    assert rb, 'Формирование web_reg_save_param невозможно, тк поле RB(5) пусто'
    text = defaults.VarFileText.get()
    assert text, 'Формирование web_reg_save_param невозможно, тк файл пустой {}'.format(defaults.VarFile.get())
    param = defaults.VarParam.get()
    assert param, 'Формирование web_reg_save_param невозможно, тк param пустой'
    split_lb_text = text.split(lb)  # разбить по левой(LB) части
    split_len = len(split_lb_text)
    assert split_len > 1, 'Формирование web_reg_save_param невозможно, тк файл не содержит LB( {lb} )'.format(lb=lb)
    param_rb = param + rb
    Ord = 0
    for part in split_lb_text[1:]:  # слева, от первой LB части, не может быть RB
        if rb in part:
            Ord += 1
            if part.startswith(param_rb):
                _param_text_index = text.index(lb + param_rb) + len(lb)
                return Ord, _param_text_index