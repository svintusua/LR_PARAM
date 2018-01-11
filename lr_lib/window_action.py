# -*- coding: UTF-8 -*-
# action.с окно

import os
import re
import contextlib
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as tkf
from tkinter import messagebox

from lr_lib import (
    defaults,
    param as lr_param,
    pool as lr_pool,
    template as lr_template,
    other as lr_other,
    web_ as lr_web_,
    window_lib as lr_wlib,
    window_widj as lr_widj,
    help as lr_help,
    logger as lr_log,
)


class ActionWindow(tk.Toplevel):
    '''окно action.c'''
    def __init__(self, *args, auto_param_creator=False):
        super().__init__(padx=0, pady=0)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.title('LoadRunner action.c | %s' % id(self))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.geometry('{}x{}'.format(*defaults._Tk_ActionWIND_SIZE))

        # текущий action текст
        self.web_action = lr_web_.ActionWebsAndLines(self)

        self.transaction = []  # имена action transaction
        __a, __b = '', ''
        self.action_file = None
        self._search_index = -1

        self.id_ = id(self)
        self._backup_index = 0

        self.action_infs = []  # номера inf в action
        self.drop_infs = set()  # отсутствующие номера inf в action
        self.drop_files = []  # файлы из отсутствующих inf

        defaults.Window.action_windows[self.id_] = self  # !

        self.searchPosVar = tk.StringVar(value='')
        self.searchVar = tk.StringVar(value=__a)
        self.font_var = tk.StringVar(value=defaults.DefaultActionHighlightFont)
        self.background_var = tk.StringVar(value=defaults.Background)
        self.size_var = tk.IntVar(value=defaults.DefaultActionHighlightFontSize)
        self.SearchReplace_searchVar = tk.StringVar(value=__a)
        self.SearchReplace_replaceVar = tk.StringVar(value=__b)
        self.cp1251_var = tk.BooleanVar(value=defaults.DefaultActionFontcp1251)
        self.final_wnd_var = tk.BooleanVar(value=defaults.DefaultActionFinalWind)
        self.force_ask_var = tk.BooleanVar(value=defaults.DefaultActionForceAsk)
        self.no_var = tk.BooleanVar(value=defaults.DefaultActionNoVar)
        self.max_inf_cbx_var = tk.BooleanVar(value=defaults.DefaultActionMaxInf)
        self.add_inf_cbx_var = tk.BooleanVar(value=defaults.DefaultActionAddInf)
        self.force_yes_inf = tk.BooleanVar(value=defaults.DefaultActionForceYes)

        self.weight_var = tk.BooleanVar(value=defaults.DefaultActionHighlightFontBold)
        self.underline_var = tk.BooleanVar(value=defaults.DefaultActionHighlightFontUnderline)
        self.slant_var = tk.BooleanVar(value=defaults.DefaultHighlightActionFontSlant)
        self.overstrike_var = tk.BooleanVar(value=defaults.DefaultHighlightActionFontOverstrike)

        self.help1 = tk.Label(self, text='?', foreground='grey')
        self.help2 = tk.Label(self, text='?', foreground='grey')
        self.help3 = tk.Label(self, text='?', foreground='grey')

        self.toolbar = tk.LabelFrame(
            self, relief='ridge', bd=5, labelanchor=tk.N, font=defaults.DefaultFont + ' italic', padx=0, pady=0,
            text='для корректной работы, раскладку клавиатуры установить в ENG')

        self.middle_bar = tk.LabelFrame(self, relief='ridge', bd=2, text='', labelanchor=tk.S, padx=0, pady=0,
                                        font=defaults.DefaultFont)
        self.transaction_bar = tk.LabelFrame(
            self.middle_bar, relief='groove', bd=0, text='transaction', labelanchor=tk.S, font=defaults.DefaultFont,
            padx=0, pady=0)
        self.inf_bar = tk.LabelFrame(
            self.transaction_bar, relief='groove', bd=0, text='inf', labelanchor=tk.W, font=defaults.DefaultFont,
            padx=0, pady=0)
        self.wrsp_bar = tk.LabelFrame(
            self.middle_bar, relief='groove', bd=0, text='web_reg_save_param', labelanchor=tk.S,
            font=defaults.DefaultFont, padx=0, pady=0)
        self.font_toolbar = tk.LabelFrame(
            self.toolbar, relief='groove', bd=0, text='', labelanchor=tk.S, font=defaults.DefaultFont, padx=0, pady=0)
        self.file_bar = tk.LabelFrame(self.toolbar, relief='groove', bd=0, text='', labelanchor=tk.N)
        self.cbx_bar = tk.LabelFrame(self.toolbar, relief='groove', bd=0, text='', labelanchor=tk.S)

        self.tk_text = lr_widj.HighlightText(
            self, background=defaults.Background, wrap=tk.NONE, bind=True, padx=0, pady=0, bd=0)

        #
        self.inf_combo = ttk.Combobox(self.inf_bar, justify='center', font=defaults.DefaultFont)

        @lr_pool.T_POOL_execute_decotator
        def goto_inf(*a) -> None:
            with contextlib.suppress(tk.TclError):
                self.search_in_action(word=lr_param.Snap.format(num=self.inf_combo.get().strip()), hist=False)

        self.inf_combo.bind("<KeyRelease-Return>", goto_inf)
        self.inf_combo.bind("<<ComboboxSelected>>", goto_inf)

        #
        self.wrsp_combo = ttk.Combobox(self.wrsp_bar, justify='center', font=defaults.DefaultFont)

        @lr_pool.T_POOL_execute_decotator
        def goto_wrsp(*a) -> None:
            with contextlib.suppress(tk.TclError):
                self.search_in_action(word=self.wrsp_combo.get(), hist=False)

        self.wrsp_combo.bind("<KeyRelease-Return>", goto_wrsp)
        self.wrsp_combo.bind("<<ComboboxSelected>>", goto_wrsp)

        self.param_combo = ttk.Combobox(self.wrsp_bar, justify='center', font=defaults.DefaultFont)

        @lr_pool.T_POOL_execute_decotator
        def goto_param(*a) -> None:
            with contextlib.suppress(tk.TclError):
                self.search_in_action(word=self.param_combo.get(), hist=False)

        self.param_combo.bind("<KeyRelease-Return>", goto_param)
        self.param_combo.bind("<<ComboboxSelected>>", goto_param)

        #
        self.transaction_combo = ttk.Combobox(self.transaction_bar, justify='center', font=defaults.DefaultFont)

        @lr_pool.T_POOL_execute_decotator
        def goto_transaction(*a) -> None:
            with contextlib.suppress(tk.TclError):
                self.search_in_action(word=self.transaction_combo.get(), hist=False)

        self.transaction_combo.bind("<KeyRelease-Return>", goto_transaction)
        self.transaction_combo.bind("<<ComboboxSelected>>", goto_transaction)

        self.font_size_entry = tk.Spinbox(
            self.font_toolbar, width=2, justify='center', from_=0, to=99, command=self.tk_text.set_font,
            textvariable=self.tk_text.size_var, font=defaults.DefaultFont)
        self.font_size_entry.bind("<KeyRelease-Return>", self.tk_text.set_font)

        self.selection_font_size_entry = tk.Spinbox(
            self.font_toolbar, width=2, justify='center', from_=0, to=99, textvariable=self.size_var,
            font=defaults.DefaultFont, command=lambda *a: self.tk_text.set_tegs(parent=self, remove=False))
        self.selection_font_size_entry.bind(
            "<KeyRelease-Return>", lambda *a: self.tk_text.set_tegs(parent=self, remove=False))

        self.bold_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=defaults.DefaultFont + ' bold', variable=self.tk_text.weight_var,
            command=self.tk_text.set_font, padx=0, pady=0)
        self.slant_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=defaults.DefaultFont + ' italic', variable=self.tk_text.slant_var,
            command=self.tk_text.set_font, padx=0, pady=0)
        self.underline_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=defaults.DefaultFont + ' underline', variable=self.tk_text.underline_var,
            command=self.tk_text.set_font, padx=0, pady=0)
        self.overstrike_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=defaults.DefaultFont + ' overstrike', variable=self.tk_text.overstrike_var,
            command=self.tk_text.set_font, padx=0, pady=0)

        self.selection_bold_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=defaults.DefaultFont + ' bold', variable=self.weight_var,
            command=self.bold_selection_set, padx=0, pady=0)
        self.selection_slant_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=defaults.DefaultFont + ' italic', variable=self.slant_var,
            command=self.bold_selection_set, padx=0, pady=0)
        self.selection_underline_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=defaults.DefaultFont + ' underline', variable=self.underline_var,
            command=self.bold_selection_set, padx=0, pady=0)
        self.selection_overstrike_cbx = tk.Checkbutton(
            self.font_toolbar, text='', font=defaults.DefaultFont + ' overstrike', variable=self.overstrike_var,
            command=self.bold_selection_set, padx=0, pady=0)

        self.font_combo = ttk.Combobox(
            self.font_toolbar, textvariable=self.tk_text.font_var, justify='center', font=defaults.DefaultFont)
        self.font_combo['values'] = list(sorted(tk.font.families()))
        self.font_combo.bind("<KeyRelease-Return>", self.tk_text.set_font)
        self.font_combo.bind("<<ComboboxSelected>>", self.tk_text.set_font)

        self.selection_font_combo = ttk.Combobox(
            self.font_toolbar, textvariable=self.font_var, justify='center', font=defaults.DefaultFont)
        self.selection_font_combo['values'] = list(sorted(tk.font.families()))
        self.selection_font_combo.bind("<KeyRelease-Return>", self.bold_selection_set)
        self.selection_font_combo.bind("<<ComboboxSelected>>", self.bold_selection_set)

        self.tk_text.set_font()
        self.bold_selection_set()

        self.background_color_combo = ttk.Combobox(
            self.cbx_bar, textvariable=self.background_var, justify='center', font=defaults.DefaultFont)
        self.background_color_combo['values'] = list(sorted(lr_help.COLORS.keys()))

        self.background_color_combo.bind("<KeyRelease-Return>", self.background_color_set)
        self.background_color_combo.bind("<<ComboboxSelected>>", self.background_color_set)
        self.config(background=self.background_color_combo.get())

        self.search_entry = ttk.Combobox(
            self.toolbar, textvariable=self.searchVar, font=defaults.DefaultFont + ' italic', justify='center')
        self.search_entry.bind("<KeyRelease-Return>", self.search_in_action)
        self.search_button = tk.Button(
            self.toolbar, text='> search >', command=self.search_in_action, font=defaults.DefaultFont + ' bold',
            padx=0, pady=0)
        self._uptext = '<-up %s'
        self.up_search_button = tk.Button(
            self.toolbar, text=self._uptext, command=self.search_up, font=defaults.DefaultFont + ' bold',
            padx=0, pady=0)
        self.down_search_button = tk.Button(
            self.toolbar, text='down->', command=self.search_down, font=defaults.DefaultFont + ' bold', padx=0, pady=0)

        self.unblock = tk.Button(
            self.file_bar, text='unblock', font=defaults.DefaultFont + ' bold', command=lambda *a: self._block(False),
            padx=0, pady=0)

        self.backup_open_button = tk.Button(
            self.file_bar, text='backup_open', background='orange', font=defaults.DefaultFont + ' bold',
            command=lambda *a: self.open_action_dialog(title=True, folder=defaults.BackupFolder), padx=0, pady=0)
        self.save_action_button = tk.Button(
            self.file_bar, text='save', font=defaults.DefaultFont + ' bold', command=self.save_action_file,
            padx=0, pady=0)
        # self.clear_text_button = tk.Button(self.cbx_bar, text='clear', font=defaults.DefaultFont, command=self.clear_text, padx=0, pady=0)
        self.open_button = tk.Button(
            self.file_bar, text='open', font=defaults.DefaultFont, command=self.open_action_dialog, padx=0, pady=0)
        self.editor_button = tk.Button(
            self.file_bar, text='editor', font=defaults.DefaultFont + ' bold', padx=0, pady=0,
            command=lambda: lr_log.openTextInEditor(self.tk_text.get(1.0, tk.END)))

        self.text_scrolly = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tk_text.yview)
        self.text_scrollx = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tk_text.xview)
        self.tk_text.configure(yscrollcommand=self.report_position_Y, xscrollcommand=self.report_position_X, bd=0)

        self.scroll_lab = ttk.Label(self, text='0')
        self.scroll_lab2 = ttk.Label(self, text='0 %', background=defaults.Background)

        self.tk_text.action = self  # !!! доступ извне

        self.search_res_combo = ttk.Combobox(
            self.toolbar, textvariable=self.searchPosVar, justify='center', font=defaults.DefaultFont,
            background=defaults.Background)

        self.search_res_combo.bind("<<ComboboxSelected>>", self.tk_text_see)
        self.search_res_combo.bind("<KeyRelease-Return>", self.tk_text_see)

        self.SearchReplace_searchCombo = ttk.Combobox(
            self.toolbar, textvariable=self.SearchReplace_searchVar, justify='center',
            font=defaults.DefaultFont + ' italic', foreground="purple")

        self.SearchReplace_replaceCombo = ttk.Combobox(
            self.toolbar, textvariable=self.SearchReplace_replaceVar, justify='center', font=defaults.DefaultFont,
            foreground="maroon")

        self.SearchReplace_searchCombo['values'] = [__a]
        self.SearchReplace_replaceCombo['values'] = [__b]
        self.search_entry['values'] = [__a]

        self.auto_param_creator_button = tk.Button(
            self.toolbar, text='Найти\n*param*', font=defaults.DefaultFont + ' bold', command=self.auto_param_creator,
            background='orange', padx=0, pady=0)

        self.final_wnd_cbx = tk.Checkbutton(
            self.toolbar, text='final\nwind', font=defaults.DefaultFont, variable=self.final_wnd_var, padx=0, pady=0)

        def force_ask_cmd(*a) -> None:
            if self.force_ask_var.get():
                self.no_var.set(0)

        self.force_ask_cbx = tk.Checkbutton(
            self.toolbar, text='force\nAsk', font=defaults.DefaultFont, variable=self.force_ask_var,
            command=force_ask_cmd, padx=0, pady=0)

        self.highlight_cbx = tk.Checkbutton(
            self.cbx_bar, text='highlight', font=defaults.DefaultFont, background=defaults.Background,
            variable=self.tk_text.highlight_var, command=self.tk_text.set_highlight, padx=0, pady=0)
        self.cp1251_cbx = tk.Checkbutton(
            self.file_bar, text='1251', font=defaults.DefaultFont, variable=self.cp1251_var,
            command=self.set_cp1251_action_encode, padx=0, pady=0)

        def no_var_cmd(*a) -> None:
            if self.no_var.get():
                self.force_ask_var.set(0)

        self.no_cbx = tk.Checkbutton(
            self.toolbar, text='No\nAsk', font=defaults.DefaultFont, variable=self.no_var, command=no_var_cmd,
            padx=0, pady=0)

        self.backup_entry = tk.Entry(self.file_bar, font=defaults.DefaultFont, width=5, justify='center')
        self.backup_entry.insert('1', defaults.BackupActionFile)

        @lr_pool.T_POOL_execute_decotator
        def repl_butt(*a) -> None:
            '''кнопка замены текста'''
            if messagebox.askyesno(str(ActionWindow), "action.c: Заменить ? :\n\n{s}\n\n на :\n\n{r}".format(
                    s=self.SearchReplace_searchVar.get(), r=self.SearchReplace_replaceVar.get()), parent=self):
                self.backup()
                text = self.tk_text.get(1.0, tk.END)
                text = text.replace(self.SearchReplace_searchVar.get(), self.SearchReplace_replaceVar.get())
                self.tk_text.delete(1.0, tk.END)
                self.tk_text.insert(1.0, text)
                self.save_action_file(file_name=False)

        self.SearchReplace_button = tk.Button(
            self.toolbar, text='> replace >', font=defaults.DefaultFont, command=repl_butt, padx=0, pady=0)

        self.buttonColorReset = tk.Button(
            self.cbx_bar, text='reset', font=defaults.DefaultFont, command=self.resColor, padx=0, pady=0)

        self.highlight_Thread = tk.Checkbutton(
            self.cbx_bar, text='', variable=defaults.HighlightThread, padx=0, pady=0, font=defaults.DefaultFont)

        self.highlight_LineThread = tk.Checkbutton(
            self.cbx_bar, text='', variable=defaults.LineTagAddThread, padx=0, pady=0, font=defaults.DefaultFont)

        self.highlight_TagThread = tk.Checkbutton(
            self.cbx_bar, text='', variable=defaults.TagAddThread, padx=0, pady=0, font=defaults.DefaultFont)

        self.highlight_MThread = tk.Checkbutton(
            self.cbx_bar, text='', variable=defaults.HighlightMPool, padx=0, pady=0, font=defaults.DefaultFont)

        self.highlight_LinesPortionSize = tk.Spinbox(
            self.cbx_bar, from_=0, to=100, textvariable=defaults.HighlightLinesPortionSize, width=2,
            font=defaults.DefaultFont)

        def max_inf_set(*a) -> None:
            if self.max_inf_cbx_var.get():
                self.add_inf_cbx.configure(state='normal')
            else:
                self.add_inf_cbx.configure(state='disabled')
        self.max_inf_cbx = tk.Checkbutton(
            self.toolbar, text='ограничить\nmax inf', font=defaults.DefaultFont + ' bold', padx=0, pady=0,
            variable=self.max_inf_cbx_var, command=max_inf_set)
        self.add_inf_cbx = tk.Checkbutton(
            self.toolbar, anchor=tk.E, text='max\nmode', font=defaults.DefaultFont, padx=0, pady=0,
            variable=self.add_inf_cbx_var)

        def legend() -> None:
            t = lr_widj.WebLegend(self)
            t.add_web_canavs()
            t.print()

        self.lr_legend = tk.Button(
            self.toolbar, text='web_legend', font=defaults.DefaultFont + ' bold', padx=0, pady=0,
            command=legend)

        def thinktime_remove() -> None:
            '''удалить thinktime'''
            text = self.tk_text.get(1.0, tk.END)
            counter = 0

            def no_tt_lines() -> iter((str, )):
                nonlocal counter
                for line in text.split('\n'):
                    if line.strip().startswith('lr_think_time'):
                        counter += 1
                    else:
                        yield line
            new_text = '\n'.join(no_tt_lines())
            if messagebox.askokcancel('thinktime', 'удалить thinktime из action?\n{} шт.'.format(counter), parent=self):
                self.backup()
                self.tk_text.delete(1.0, tk.END)
                self.tk_text.insert(1.0, new_text)
                self.save_action_file(file_name=False)

        self.lr_think_time = tk.Button(
            self.toolbar, text='lr_think_time', font=defaults.DefaultFont + ' bold', padx=0, pady=0,
            command=thinktime_remove)

        self.lr_report_B = tk.Button(
            self.toolbar, text='reportB', font=defaults.DefaultFont + ' bold', padx=0, pady=0,
            command=lambda *a: lr_wlib.repB(self.tk_text))

        self.lr_report_A = tk.Button(
            self.toolbar, text='reportA', font=defaults.DefaultFont + ' bold', padx=0, pady=0,
            command=lambda *a: lr_wlib.repA(self.tk_text))

        @lr_pool.T_POOL_execute_decotator
        def all_transaction_rename(*a) -> None:
            '''переименавать все транзакции'''
            _transactions = [t.split('"', 1)[1] for t in self.transaction]
            transactions = list(sorted(set(_transactions), key=_transactions.index))
            mx = max(map(len, transactions or ['']))
            m = '"{:<%s}" -> "{}"' % mx
            all_transaction = '\n'.join(m.format(old, new) for old, new in zip(transactions, transactions))
            y = lr_wlib.YesNoCancel(
                ['Переименовать', 'Отмена'], 'Переименовать transaction слева', 'в transaction справа', 'transaction',
                parent=self, is_text=all_transaction)
            st = 'lr_start_transaction("'
            en = 'lr_end_transaction("'
            if y.ask() == 'Переименовать':
                new_transaction = [t.split('-> "', 1)[1].split('"', 1)[0].strip() for t in y.text.strip().split('\n')]
                assert len(transactions) == len(new_transaction)
                text = self.tk_text.get('1.0', tk.END)
                for old, new in zip(transactions, new_transaction):
                    text = text.replace((st + old), (st + new))
                    text = text.replace((en + old), (en + new))
                self.backup()
                self.tk_text.new_text_set(text)  # вставить
                with self.block():
                    self.save_action_file(file_name=False)

        self.transaction_rename = tk.Button(
            self.toolbar, text='rename\ntransaction', font=defaults.DefaultFont + ' bold', background='orange',
            padx=0, pady=0, command=all_transaction_rename)

        self.dummy_button = tk.Button(
            self.toolbar, text="Snapshot remove", font=defaults.DefaultFont + ' bold', background='orange',
            padx=0, pady=0, command=self.dummy_btn_cmd)
        self.force_yes_inf_checker_cbx = tk.Checkbutton(
            self.toolbar, text='force\nYes inf', font=defaults.DefaultFont, variable=self.force_yes_inf, padx=0, pady=0)

        self.search_entry.grid(row=5, column=0, columnspan=8, sticky=tk.NSEW, padx=0, pady=0)
        self.search_button.grid(row=5, column=8, sticky=tk.NSEW, padx=0, pady=0)
        self.down_search_button.grid(row=5, column=9, sticky=tk.NSEW, padx=0, pady=0)
        self.search_res_combo.grid(row=5, column=10, sticky=tk.NSEW, columnspan=3, padx=0, pady=0)
        self.up_search_button.grid(row=5, column=13, sticky=tk.NSEW, padx=0, pady=0)

        self.backup_open_button.grid(row=5, column=16, columnspan=2, sticky=tk.NSEW, padx=0, pady=0)
        self.save_action_button.grid(row=6, column=17, sticky=tk.NSEW, padx=0, pady=0)

        self.highlight_cbx.grid(row=1, column=1, padx=0, pady=0, sticky=tk.NSEW, columnspan=5)
        self.background_color_combo.grid(row=2, column=1, sticky=tk.NSEW, padx=0, pady=0, columnspan=5)
        self.buttonColorReset.grid(row=3, column=1, padx=0, pady=0, sticky=tk.NSEW, columnspan=5)
        self.highlight_Thread.grid(row=4, column=1, padx=0, pady=0, sticky=tk.NSEW)
        self.highlight_LineThread.grid(row=4, column=2, padx=0, pady=0, sticky=tk.NSEW)
        self.highlight_TagThread.grid(row=4, column=3, padx=0, pady=0, sticky=tk.NSEW)
        self.highlight_MThread.grid(row=4, column=4, padx=0, pady=0, sticky=tk.NSEW)
        self.highlight_LinesPortionSize.grid(row=4, column=5, padx=0, pady=0, sticky=tk.NSEW)

        self.open_button.grid(row=6, column=16, sticky=tk.NSEW, padx=0, pady=0)
        self.editor_button.grid(row=7, column=17, padx=0, pady=0, sticky=tk.NSEW)
        # self.clear_text_button.grid(row=4, column=1, padx=0, pady=0, sticky=tk.NSEW)
        self.no_cbx.grid(row=7, column=10, sticky=tk.NSEW, padx=0, pady=0, rowspan=2)
        self.cp1251_cbx.grid(row=7, column=16, padx=0, pady=0, sticky=tk.NSEW)
        self.auto_param_creator_button.grid(row=7, column=8, sticky=tk.NSEW, padx=0, pady=0, rowspan=2)
        self.force_ask_cbx.grid(row=7, column=11, sticky=tk.NSEW, padx=0, pady=0, rowspan=2)
        self.unblock.grid(row=9, column=17, sticky=tk.NSEW, padx=0, pady=0)
        self.final_wnd_cbx.grid(row=7, column=9, sticky=tk.NSEW, padx=0, pady=0, rowspan=2)

        self.font_size_entry.grid(row=12, column=4, sticky=tk.NSEW, padx=0, pady=0)
        self.font_combo.grid(row=10, column=0, columnspan=10, sticky=tk.NSEW, padx=0, pady=0)
        self.bold_cbx.grid(row=12, column=5, sticky=tk.NSEW, padx=0, pady=0)
        self.overstrike_cbx.grid(row=12, column=6, sticky=tk.NSEW, padx=0, pady=0)
        self.underline_cbx.grid(row=12, column=7, sticky=tk.NSEW, padx=0, pady=0)
        self.slant_cbx.grid(row=12, column=8, sticky=tk.NSEW, padx=0, pady=0)
        self.backup_entry.grid(row=9, column=16, sticky=tk.NSEW, padx=0, pady=0)

        self.selection_font_combo.grid(row=11, column=0, columnspan=10, sticky=tk.NSEW, padx=0, pady=0)
        self.selection_font_size_entry.grid(row=13, column=4, sticky=tk.NSEW, padx=0, pady=0)
        self.selection_bold_cbx.grid(row=13, column=5, sticky=tk.NSEW, padx=0, pady=0)
        self.selection_overstrike_cbx.grid(row=13, column=6, sticky=tk.NSEW, padx=0, pady=0)
        self.selection_underline_cbx.grid(row=13, column=7, sticky=tk.NSEW, padx=0, pady=0)
        self.selection_slant_cbx.grid(row=13, column=8, sticky=tk.NSEW, padx=0, pady=0)

        self.SearchReplace_searchCombo.grid(row=6, column=0, columnspan=8, sticky=tk.NSEW, padx=0, pady=0)
        self.SearchReplace_replaceCombo.grid(row=6, column=9, columnspan=8, sticky=tk.NSEW, padx=0, pady=0)
        self.SearchReplace_button.grid(row=6, column=8, sticky=tk.NSEW, padx=0, pady=0)

        self.toolbar.grid(row=2, column=0, sticky=tk.N, columnspan=100, padx=0, pady=0)

        self.middle_bar.grid(row=3, column=0, sticky=tk.N, padx=0, pady=0)
        self.inf_bar.grid(row=1, column=0, sticky=tk.N, padx=0, pady=0)
        self.transaction_bar.grid(row=3, column=0, sticky=tk.E, padx=0, pady=0)
        self.wrsp_bar.grid(row=3, column=1, sticky=tk.W, padx=0, pady=0)

        self.file_bar.grid(row=5, column=20, sticky=tk.NSEW, rowspan=5, padx=0, pady=0)
        self.cbx_bar.grid(row=5, column=50, sticky=tk.NSEW, rowspan=5, padx=0, pady=0)
        self.font_toolbar.grid(row=5, column=21, sticky=tk.NSEW, rowspan=4, padx=0, pady=0)

        self.text_scrolly.grid(row=0, column=201, sticky=tk.NSEW, padx=0, pady=0)
        self.text_scrollx.grid(row=1, column=0, sticky=tk.NSEW, columnspan=201, padx=0, pady=0)
        self.scroll_lab.grid(row=1, column=300, sticky=tk.NSEW, padx=0, pady=0)
        self.scroll_lab2.grid(row=2, column=300, sticky=tk.NSEW, padx=0, pady=0, rowspan=2)

        self.inf_combo.grid(row=1, column=1, sticky=tk.NSEW, padx=0, pady=0)
        self.transaction_combo.grid(row=1, column=2, sticky=tk.NSEW, padx=0, pady=0)
        self.wrsp_combo.grid(row=1, column=3, sticky=tk.NSEW, padx=0, pady=0)
        self.param_combo.grid(row=1, column=4, sticky=tk.NSEW, padx=0, pady=0)

        self.help1.grid(row=1, column=201, sticky=tk.NSEW, padx=0, pady=0)
        self.help2.grid(row=2, column=201, sticky=tk.NSEW, padx=0, pady=0)
        self.help3.grid(row=3, column=201, sticky=tk.NSEW, padx=0, pady=0)

        self.tk_text.grid(row=0, column=0, sticky=tk.NSEW, columnspan=201, padx=0, pady=0)
        self.tk_text.linenumbers.grid(row=0, column=300, sticky=tk.NS, padx=0, pady=0)
        self.tk_text.linenumbers.config(width=30)

        self.max_inf_cbx.grid(row=7, column=1, sticky=tk.NSEW, padx=0, pady=0, rowspan=2)
        self.add_inf_cbx.grid(row=7, column=2, sticky=tk.NSEW, padx=0, pady=0, rowspan=2)
        self.dummy_button.grid(row=7, column=13, sticky=tk.NSEW, padx=0, pady=0, rowspan=2)
        self.force_yes_inf_checker_cbx.grid(row=7, column=12, sticky=tk.NSEW, padx=0, pady=0, rowspan=2)
        self.lr_legend.grid(row=7, column=3, sticky=tk.NSEW, padx=0, pady=0)
        self.lr_think_time.grid(row=7, column=4, sticky=tk.NSEW, padx=0, pady=0)
        self.lr_report_B.grid(row=8, column=4, sticky=tk.NSEW, padx=0, pady=0)
        self.lr_report_A.grid(row=8, column=3, sticky=tk.NSEW, padx=0, pady=0)
        self.transaction_rename.grid(row=7, column=5, sticky=tk.NSEW, padx=0, pady=0, rowspan=2)

        lr_wlib.createToolTip(self.editor_button, 'открыть текст action в блокноте\n\t# editor_button')
        lr_wlib.createToolTip(self.backup_entry, 'макс кол-во backup файлов(запись по кругу)\nперед автозаменой, в '
                                                 'директорию {folder}, делается action бэкап\n\t# backup_entry'.format(
            folder=os.path.join(os.getcwd(), defaults.BackupFolder)))
        lr_wlib.createToolTip(self.buttonColorReset, 'сбросить цвет текста\n\t# buttonColorReset')
        lr_wlib.createToolTip(self.highlight_Thread, 'выполнять в фоне, весь код подсветки\n\t# highlight_Thread')
        lr_wlib.createToolTip(self.highlight_LineThread, 'выполнять в фоне, код подсветки для одной линии\n\t'
                                                         '# highlight_LineThread')
        lr_wlib.createToolTip(self.highlight_TagThread, 'выполнять в фоне, код подсветки для одного тега\n\t'
                                                        '# highlight_TagThread')
        lr_wlib.createToolTip(self.highlight_MThread, 'искать индексы для подсветки линий, в M_POOL\n\t'
                                                      '# highlight_MThread')
        lr_wlib.createToolTip(self.highlight_LinesPortionSize, 'для скольки линий, искать индексы, за один проход/поток'
                                                               '\n\t# highlight_LinesPortionSize')

        lr_wlib.createToolTip(self.open_button, 'открыть action.c файл\n\t# open_button')
        lr_wlib.createToolTip(self.highlight_cbx, 'On - применить подсветку\nOff - убрать подсветку\nЧтобы применмть '
                                                  'новую подсветку, необходимо снять/установить повторно\n\t'
                                                  '# highlight_cbx')
        lr_wlib.createToolTip(self.search_res_combo, 'результаты(координаты) поиска слова в тексте action.c:\n'
                                                     '"201.33+2c" - [Строка].[Столбец]+[ДлинаСлова]c\nпри выборе - '
                                                     'переход в область,колесом мыши - переход между областями\n'
                                                     'учной ввод координат по <<Enter>>\n\t# search_res_combo')
        lr_wlib.createToolTip(self.search_button, 'Поиск слова из search_entry в тексте action\n результат - заполняет '
                                                  'комбобокс координат search_res_combo\n\t# search_button')
        lr_wlib.createToolTip(self.search_entry, 'слово для поиска в тексте action\n\t# search_entry')

        lr_wlib.createToolTip(self.SearchReplace_searchCombo, 'слово, для замены\n\t# SearchReplace_searchCombo')
        lr_wlib.createToolTip(self.SearchReplace_replaceCombo, 'слово, на которое заменить\n\t'
                                                               '# SearchReplace_replaceCombo')
        lr_wlib.createToolTip(self.SearchReplace_button, 'Найти и Заменить, для SearchReplace_комбобоксов\n'
                                                         'Обычная(как в блокноте) автозамена\n\t# SearchReplace_button')
        lr_wlib.createToolTip(self.cp1251_cbx, 'принудительно перекодировать action.c текст в кодировку\n'
                                               'On="cp1251" / Off="UTF-8"\nдля преобразования сразу всех строк '
                                               '"РџРµСЂРІРёС‡РЅС‹" -> "Первичны"\nТк может пропасть часть текста('
                                               'если всречаются несколько разных кодировок), лучше не пользоватся\n\t'
                                               '# cp1251_cbx')
        lr_wlib.createToolTip(self.up_search_button, 'перейти вверх, по результатам поиска\n\t# up_search_button')
        lr_wlib.createToolTip(self.down_search_button, 'перейти вниз, по результатам поиска\n\t# down_search_button')
        lr_wlib.createToolTip(self.backup_open_button, 'открыть бэкап файл, для текущего окна\n\t# backup_open_button')
        lr_wlib.createToolTip(self.force_ask_cbx, 'Автозамена - подтверждать любую замену.\nТе показывать окно диалога '
                                                  'подтверждения, для каждой замены.\n\t# force_ask_cbx')
        lr_wlib.createToolTip(self.no_cbx, 'Автозамена - Принудительно отвечать "Нет, для Всех" в вопросе замены,\n'
                                           'В обычной ситуации, от пользователя, требуетcя подтверждение,\n'
                                           'если заменяемое слово, является частью другого, более длинного слова\n'
                                           'Например при замене "zkau_2", для "zkau_201", "zkau_20", "Azkau_2", ...\n'
                                           'В результате - не показывать окно диалога подтверждения.\n\t# no_cbx')
        lr_wlib.createToolTip(self.final_wnd_cbx, 'окно результата создания param\nперед показом окна, '
                                                  'в action.c тексте, будет сделан переход на блок с web_reg_save_param'
                                                  '\nи пока не нажата кнопка OK, можно визуально проконтролировать '
                                                  '"корректность" LR/RB.\nпосле закрытия окна, будет сделан переход '
                                                  'на первый замененный param\n\t# final_wnd_cbx')
        lr_wlib.createToolTip(self.auto_param_creator_button, 'автоматичейский поиск и создание web_reg_save_param\n '
                                                              'для param, имя которых начинается на ...\n '
                                                              'аналог нескольких меню_мыши/web_reg_save_param/группа'
                                                              '\n\t# auto_param_creator_button')
        lr_wlib.createToolTip(self.help1, lr_help.ACTION1)
        lr_wlib.createToolTip(self.help2, lr_help.ACTION2)
        lr_wlib.createToolTip(self.help3, lr_help.ACTION3)
        lr_wlib.createToolTip(self.save_action_button, 'сохранить текст action окна\n+ обновить "служебную" инфу '
                                                       'об удаленных "inf-блоках", если чтото удаляли вручную'
                                                       '\n\t# save_action_button')

        lr_wlib.createToolTip(self.selection_font_combo, 'шрифт, для выделения\n\t# selection_font_combo')
        lr_wlib.createToolTip(self.selection_font_size_entry, 'размер шрифта, для выделения\n\t'
                                                              '# selection_font_size_entry')
        lr_wlib.createToolTip(self.selection_bold_cbx, 'жирный шрифт, для выделения\n\t# selection_bold_cbx')
        lr_wlib.createToolTip(self.selection_underline_cbx, 'подчеркнутый шрифт, для выделения\n\t'
                                                            '# selection_underline_cbx')
        lr_wlib.createToolTip(self.selection_overstrike_cbx, 'зачеркнутый шрифт, для выделения\n\t'
                                                             '# selection_overstrike_cbx')
        lr_wlib.createToolTip(self.selection_slant_cbx, 'курсив шрифт, для выделения\n\t# selection_slant_cbx')

        lr_wlib.createToolTip(self.wrsp_combo, 'имя web_reg_save_param\nпереход в область action.c текста\n\t'
                                               '# wrsp_combo')
        lr_wlib.createToolTip(self.param_combo, 'имя param\nпереход в область action.c текста\n\t# param_combo')
        lr_wlib.createToolTip(self.inf_combo, 'номер inf блока\nпереход в область action.c текста\n\t# inf_combo')
        lr_wlib.createToolTip(self.transaction_combo, 'имя транцакции\nпереход в область action.c текста\n\t'
                                                      '# transaction_combo')

        lr_wlib.createToolTip(self.font_combo, 'шрифт\n\t# font_combo')
        lr_wlib.createToolTip(self.font_size_entry, 'размер шрифта\n\t# font_size_entry')
        lr_wlib.createToolTip(self.bold_cbx, 'жирный шрифт\n\t# bold_cbx')
        lr_wlib.createToolTip(self.underline_cbx, 'подчеркнутый шрифт\n\t# underline_cbx')
        lr_wlib.createToolTip(self.overstrike_cbx, 'зачеркнутый шрифт\n\t# overstrike_cbx')
        lr_wlib.createToolTip(self.slant_cbx, 'курсив шрифт\n\t# slant_cbx')

        lr_wlib.createToolTip(self.dummy_button, 'удалить все dummy web_submit_data из action.c текста\n\t'
                                                 '# dummy_button')
        lr_wlib.createToolTip(self.background_color_combo, 'цвет фона tk.Text\n\t# background_color_combo')
        lr_wlib.createToolTip(
            self.force_yes_inf_checker_cbx, 'принудительно отвечать "Да", при вопросе о создании param\nесли inf-номер '
                                            'запроса <= inf-номер web_reg_save_param\n\t# force_yes_inf_checker_cbx')
        lr_wlib.createToolTip(self.unblock, 'разблокировать виджеты, во время работы\n\t# unblock')
        lr_wlib.createToolTip(self.lr_think_time, 'удалить все lr_think_time\n\t# lr_think_time')
        lr_wlib.createToolTip(self.lr_report_A, 'краткий отчет об action.c, с учетом вложенности транзакций\n\t# lr_report_A')
        lr_wlib.createToolTip(self.lr_report_B, 'полный отчет об action.c\n\t# lr_report_B')
        lr_wlib.createToolTip(self.transaction_rename, 'переименовать имена транзакций\n\t# transaction_rename')
        lr_wlib.createToolTip(self.max_inf_cbx, 'ограничить диапазон поиска param - максимальный номер inf\nЭто номер '
                                                'inf, в action.c, где первый раз встречается pram\n\t# max_inf_cbx')
        lr_wlib.createToolTip(self.add_inf_cbx, 'макс номер inf, для поиска param, в LoadRunner файлах ответов\n '
                                                'On - inf, где первый раз встречается pram, в action.c\n'
                                                '\tчто неправильно но необходимо, тк LoadRunner так записывает\n'
                                                ' Off - inf, предшествующий, номеру inf, где первый раз встречается '
                                                'pram, в action.c\n\tиспользуется, совместно с чекбоксом last, для '
                                                'поиска inf-ответа,\n\tмаксимально близкого, к param-inf, те поиску с '
                                                'конца\n\t# add_inf_cbx')

        ws = self.search_res_combo, self.SearchReplace_searchCombo, self.SearchReplace_replaceCombo, self.search_entry,
        for widj in ws:
            with contextlib.suppress(Exception):
                self.bind_class(widj, sequence='<Button-3>', func=lr_wlib.rClicker, add='')

        self.open_action()
        if auto_param_creator and len(defaults.Window.action_windows) < 2:
            self.auto_param_creator()

    @lr_pool.T_POOL_execute_decotator
    def bold_selection_set(self, *a) -> None:
        self.tk_text.set_tegs(parent=self)

    def background_color_set(self, *args, color='') -> None:
        '''установить цвет фона'''
        if color is None:  # смена по кругу
            color = next(defaults.ColorIterator)
        if not color:  # выбранный
            color = self.background_color_combo.get()

        self.config(background=color)
        self.scroll_lab2.config(background=color)
        self.tk_text.config(background=color)
        self.tk_text.linenumbers.config(background=color)

    def report_position(self) -> None:
        '''при скролле tk.Text, вывести номера линий'''
        top = int(self.tk_text.index("@0,0").split('.', 1)[0])
        bottom = int(self.tk_text.index("@0,%d" % self.tk_text.winfo_height()).split('.', 1)[0])

        self.title('{txt} lines[{top}:{bottom}] | {v} | undo(ctrl-z)/redo(ctrl-y)'.format(
            txt=self._set_title(), top=top, bottom=bottom, v=defaults.VERSION))
        if self.tk_text.highlight_var.get():  # подсветить линии
            self.tk_text.highlight_lines.set_top_bottom(top, bottom)

    def report_position_X(self, *argv) -> None:
        '''get (beginning of) first visible line'''
        self.text_scrollx.set(*argv)
        self.report_position()

    def report_position_Y(self, *argv) -> None:
        '''get (beginning of) first visible line'''
        self.text_scrolly.set(*argv)
        self.report_position()

    @lr_pool.T_POOL_execute_decotator
    def dummy_btn_cmd(self, *a) -> None:
        '''удалить dummy из action'''
        self.set_template_list(force=True)

    def inf_combo_set(self) -> None:
        self.inf_combo['values'] = list(self.action_infs)
        if self.inf_combo['values']:
            self.inf_combo.current(0)

    def wrsp_combo_set(self) -> None:
        self.wrsp_combo['values'] = list(self.web_action.websReport.wrsp_and_param_names.keys())

    def param_combo_set(self) -> None:
        with contextlib.suppress(Exception):
            self.param_combo['values'] = list(self.web_action.websReport.wrsp_and_param_names.values())

    def transaction_combo_set(self) -> None:
        self.transaction_combo['values'] = self.transaction

    def set_combo_len(self):
        if defaults.Window._block_:
            return
        min_len = defaults.VarActComboLenMin.get()
        max_len = defaults.VarActComboLenMax.get()
        for w in dir(self):
            attr = getattr(self, w)
            if isinstance(attr, ttk.Combobox):
                m = max([len(str(f)) for f in attr['values']] or [min_len])
                attr.configure(width=m if min_len <= m <= max_len else min_len if m < min_len else max_len)
        self.selection_font_combo.configure(width=20)
        self.font_combo.configure(width=20)

    def on_closing(self) -> None:
        '''спросить, при закрытии окна'''
        if messagebox.askokcancel("Закрыть action.c", "Закрыть action.c ?", parent=self):
            self.backup()
            del defaults.Window.action_windows[self.id_]
            self.destroy()

    def search_down(self, *a) -> None:
        '''поиск вниз, по тексту action.c'''
        bhl = self.backgr_butt()
        next(bhl)
        i = len(list(self.search_res_combo['values']))
        if i:
            self._search_index += 1
            if self._search_index >= i:
                self._search_index = 0
            self.search_res_combo.current(self._search_index)
            self.tk_text_see()
            self.tk_text._on_change()
        next(bhl, None)

    def search_up(self, *a) -> None:
        '''поиск вверх, по тексту action.c'''
        bhl = self.backgr_butt()
        next(bhl)
        i = len(list(self.search_res_combo['values']))
        if i:
            self._search_index -= 1
            if self._search_index < 0:
                self._search_index = i - 1
            self.search_res_combo.current(self._search_index)
            self.tk_text_see()
        next(bhl, None)

    def search_in_action(self, *a, word=None, hist=True) -> None:
        '''поиск в tk_text'''
        if defaults.Window._block_:
            return

        bhl = self.backgr_butt()
        next(bhl)
        self._search_index = -1
        self.search_res_combo.set('')

        if word is None:
            word = self.search_entry.get()
        else:
            self.search_entry.set(word)

        if hist:
            vals = self.search_entry['values']
            if word not in vals:
                self.search_entry['values'] = list(reversed(list(vals) + [word]))
                self.search_entry.current(0)

        self.search_res_combo['values'] = self._search_text(word=word)
        _, a, b = lr_wlib.widget_values_counter(self.search_res_combo)
        self.up_search_button['text'] = self._uptext % '{0}/{1}'.format(a, b)

        if not self.search_res_combo['values']:
            return lr_log.Logger.warning('в action.c тексте не найдено:\nword="{w}"\ntype={t}\nlen={ln}'.format(
                w=word, t=type(word), ln=(len(word) if hasattr(word, '__len__') else None)), parent=self)
        else:
            self.search_res_combo.current(0)
            self.tk_text_see()

        next(bhl, None)

    def backgr_butt(self) -> iter:
        '''менять/вернуть цвет кнопок'''
        if defaults.Window._block_:
            try:
                yield
            finally:
                return

        def change() -> None:
            '''менять'''
            self.search_entry.config(font='Arial 7 bold')
            self.down_search_button.config(background='orange')
            self.up_search_button.config(background='orange')
            self.search_res_combo.config(font='Arial 7 bold')
            self.update()

        def restore() -> None:
            '''вернуть'''
            self.search_entry.config(font=defaults.DefaultFont)
            self.search_res_combo.config(font=defaults.DefaultFont)
            self.down_search_button.config(background='lightgray')
            _, a, b = lr_wlib.widget_values_counter(self.search_res_combo)
            self.up_search_button.config(text=self._uptext % '{0}/{1}'.format(a, b), background='lightgrey')
            self.update()

        try:
            self.after(10, change)
            yield
        finally:
            self.after(100, restore)
            return

    def _search_text(self, *a, word=None, pos='1.0', coord='{i}+{w}c') -> [str, ]:
        '''поиск в tk_text'''
        if defaults.Window._block_:
            return []
        if word is None:
            word = self.searchVar.get()
        if word:
            len_word = len(word)
            word_pos = []
            while True:
                idx = self.tk_text.search(word, pos, tk.END)
                if not idx:
                    break
                pos = coord.format(i=idx, w=len_word)
                word_pos.append(pos)
            return word_pos
        else:
            return []

    def clear_text(self) -> None:
        '''очистить tk_text'''
        if messagebox.askquestion('очистить', 'очистить окно?', parent=self) == 'yes':
            self.backup()
            self.tk_text.delete(1.0, tk.END)

    def tk_text_see(self, *a) -> None:
        '''перейти на позицию в тексте'''
        if defaults.Window._block_:
            return
        self.tk_text.mark_set("insert", self.searchPosVar.get())
        self.tk_text.focus_set()
        self.tk_text.see("insert")
        _, a, b = lr_wlib.widget_values_counter(self.search_res_combo)
        self.up_search_button.config(text=self._uptext % '{0}/{1}'.format(a, b))

    def resColor(self) -> None:
        '''сбросить self.tk_text.highlight_dict настройки цветов'''
        if messagebox.askquestion('сброс', 'сбросить текст настройки цветов?', parent=self) == 'yes':
            self.tk_text.reset_highlight()

    @lr_pool.T_POOL_execute_decotator
    def open_action_dialog(self, *a, title=False, folder=os.getcwd()) -> None:
        '''открыть файл'''
        if title:
            af = tk.filedialog.askopenfilename(initialdir=folder, parent=self, filetypes=(
                ("%s_backup_*.c" % self.id_, "%s_backup_*.c" % self.id_),
                ("all", "*.*")), title='backup({})'.format(self.id_))
        else:
            af = tk.filedialog.askopenfilename(initialdir=folder, parent=self, filetypes=(
                ("action.c", "*.c"), ("all", "*.*")))
        if af:
            self.open_action(file=af)

    def set_title(self) -> None:
        self.title('{} {} undo: ctrl-z / redo: ctrl-y)'.format(self._set_title(), defaults.VERSION))

    def _set_title(self) -> str:
        return '{a} | {i} | backup={b} |'.format(
            a=self.action_file, b=self._backup_index, i=self.id_)

    def set_template_list(self, force=True) -> None:
        '''очистить Text для WebDummyTemplate_List'''
        lr_template.Dummy.setattrs(lr_template.WebDummyTemplate_Part_Endswith)
        ok = self.tk_text_dummy_remove(force=force, mode='endswith')

        for template in lr_template.WebDummyTemplate_List:
            lr_template.Dummy.setattrs(template)
            if ok:
                ok = self.tk_text_dummy_remove(force=False)

        del_all = yask = is_del = False
        for web in self.web_action.get_web_snapshot_all():
            if web.snapshot in self.web_action.websReport.google_webs:
                if not del_all:
                    gws = str(self.web_action.websReport.google_webs)[:50]
                    wt = ''.join(web.to_str())
                    sn = '"Snapshot=t{}.inf"'.format(web.snapshot)
                    yask = lr_wlib.YesNoCancel(
                        ['Удалить текущий', "Удалить все Snapshot's {}".format(gws), 'Пропустить', 'Выход'],
                        "удалить {sn} содержащий {d}".format(d={k: wt.count(k) for k in defaults.DENY_WEB_}, sn=sn),
                        'всего можно удалить {} шт'.format(len(self.web_action.websReport.google_webs)), parent=self,
                        is_text=wt, title='{i} | {sn}'.format(i=self.id_, sn=sn)).ask()
                    del_all = yask.startswith('Удалить все')
                if del_all or yask.startswith('Удалить'):
                    self.web_action.webs_and_lines.remove(web)
                    is_del = True
                elif yask == 'Выход':
                    break
        if is_del:
            self.web_action_to_tk_text()

    def save_action_file(self, file_name=None) -> None:
        '''текст to WEB_ACTION - сохранить текст action.c окна'''
        self.web_action.set_text_list(self.tk_text.get(1.0, tk.END))
        self.web_action_to_tk_text()

        if file_name is None:
            file_name = tk.filedialog.asksaveasfilename(initialdir=os.getcwd(), filetypes=(
                ("action.c", "*.c"), ("all", "*.*")), title='сохранить текст action.c окна', parent=self)

        if file_name:
            with open(file_name, 'w', errors='replace', encoding=defaults.VarEncode.get()) as act:
                act.write(self.tk_text.get(1.0, tk.END))
        else:
            self.backup()

    def web_action_to_tk_text(self) -> None:
        '''WEB_ACTION to tk_text'''
        self.web_action.websReport.create()
        self.tk_text.new_text_set(self.web_action.to_str())
        self.tk_text.set_highlight()
        self.widj_reset()

    @lr_pool.T_POOL_execute_decotator
    # @lr_log.exec_time
    def open_action(self, file=None) -> None:
        '''окно action.c'''
        self.action_file = file or _action_file()

        if os.path.isfile(self.action_file):
            with defaults.Window.block(), \
                 open(self.action_file, errors='replace', encoding=defaults.VarEncode.get()) as act:
                text = act.read()
                self.tk_text.new_text_set(text)
                self.web_action.set_text_list(text)
                # self.set_template_list()

            self.tk_text.reset_highlight(highlight=False)
            # self.web_action.print_transaction()
            lr_log.Logger.info('{f} > {s}'.format(f=self.action_file, s=self.id_))

        if self.cp1251_var.get():
            self.set_cp1251_action_encode()
        else:
            self.save_action_file(file_name=False)

        if self.web_action.websReport.rus_webs:
            lr_log.Logger.warning(
                'В следующих номерах inf, обнаружены Русские(NoASCII) символы, возможно требуется перекодировка'
                '(выделение/encoding из меню мыши)\n{}'.format(self.web_action.websReport.rus_webs))
        if self.web_action.websReport.google_webs:
            lr_log.Logger.warning(
                'Возможно следующие номера inf лишние, тк содержат слова {s}\n'
                'их можно удалить(+"commit/backup/обновить action.c" из меню мыши)\n{w}'.format(
                    w=self.web_action.websReport.google_webs, s=defaults.DENY_WEB_))

        self.background_color_set(color='')  # оригинальный цвет

    def set_cp1251_action_encode(self, enc='CP1251'):
        if self.cp1251_var.get():
            self.backup()
        else:
            enc = defaults.VarEncode.get()

        text = self.tk_text.get(1.0, tk.END)
        text = text.encode(enc).decode(errors='replace')
        self.tk_text.delete(1.0, tk.END)
        self.tk_text.insert(1.0, text)
        self.save_action_file(file_name=False)

    def get_transaction(self, text: str) -> iter((str, )):
        '''имена транзакций'''
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('lr_') and line.endswith(');') and '_transaction("' in line:
                t_name = line.rsplit('"', 1)[0]
                yield t_name

    def widj_reset(self) -> None:
        '''обновить виджеты'''
        self.transaction.clear()
        self.transaction.extend(self.get_transaction(self.tk_text.get(1.0, tk.END)))
        self.transaction_combo_set()
        self.drop_file_none_inf_num_in_action()
        self.inf_combo_set()
        self.toolbar['text'] = self.param_counter(all_param_info=False)
        self.set_title()
        self.set_combo_len()

    @lr_pool.T_POOL_execute_decotator
    def auto_param_creator(self, *a) -> None:
        '''group params по кнопке PARAM'''
        y = lr_wlib.YesNoCancel(['Найти', 'Отменить'], is_text='\n'.join(defaults.Params_names), parent=self,
                                text_before='Будет произведен поиск param, имя которых начинается на указанные имена.',
                                title='начало param-имен', text_after='При необходимости - добавить/удалить')
        ans = y.ask()
        if ans == 'Найти':
            param_parts = list(filter(bool, map(str.strip, y.text.split('\n'))))
            params = [self.session_params()]
            params.extend(map(self.group_param_search, param_parts))
            params = set(p for ps in params for p in ps)
            params = [p for p in params if ((p not in defaults.DENY_PARAMS) and (not (
                len(p) > 2 and p.startswith('on') and p[2].isupper())))]
            params.sort(key=lambda param: len(param), reverse=True)
            y = lr_wlib.YesNoCancel(['Создать', 'Отменить'], is_text='\n'.join(params),
                                    parent=self, text_before='создание + автозамена. %s шт' % len(params),
                                    title='Имена param', text_after='При необходимости - добавить/удалить')
            ans = y.ask()
            if ans == 'Создать':
                params = list(filter(bool, map(str.strip, y.text.split('\n'))))
                lr_wlib.group_param(None, widget=self.tk_text, params=params, ask=False)

    @contextlib.contextmanager
    def block(self, w=('tk_text', 'unblock', 'search_entry', 'search_res_combo', 'toolbar', )) -> iter:
        '''заблокировать/разблокировать виджеты в gui'''
        try:
            yield self._block(True, w=w)
        finally:
            self._block(False, w=w)

    def _block(self, bl: bool, w=()) -> None:
        '''заблокировать/разблокировать виджеты в gui'''
        state = 'disabled' if bl else 'normal'
        for a in dir(self):
            if not a.startswith('_') and a not in w:
                with contextlib.suppress(Exception):
                    getattr(self, a).configure(state=state)
        with contextlib.suppress(Exception):
            self.update()  # not in main loop

    def backup_name(self) -> str:
        '''имя backup-файла'''
        return os.path.join(defaults.BackupFolder, defaults.BackupName.format(i=self.id_, ind=self._backup_index))

    def param_counter(self, all_param_info=False) -> str:
        '''подсчитать кол-во созданных web_reg_save_param'''
        self.wrsp_combo_set()
        self.param_combo_set()

        if all_param_info:
            lr_log.Logger.debug(self.web_action.websReport.web_snapshot_param_in_count)
        return 'всего web_reg_save_param : {w}'.format(w=len(self.web_action.websReport.wrsp_and_param_names))

    def param_inf_checker(self, wrsp_dict: dict, wrsp: str) -> None:
        '''inf-номер запроса <= inf-номер web_reg_save_param'''
        if not wrsp_dict:
            return

        max_action_inf = wrsp_dict['param_max_action_inf']
        if defaults.VarIsInfFiles.get():
            try:
                if not max_action_inf:
                    raise UserWarning('Перед param, не найдено никаких блоков c inf запросами.')
                elif max_action_inf <= min(wrsp_dict['inf_nums']):
                    inf_nums = wrsp_dict['inf_nums'] or [-2]
                    raise UserWarning(
                        'Snapshot=t{p}.inf, в котором расположен,\nпервый заменяемый {_p}\n\nне может быть меньше '
                        'или равен,\nSnapshot=t{w}.inf, перед которым вставляется\nweb_reg_save_param запрос\n\n'
                        '{p} <= {inf_nums}'.format(
                            _p='{%s}' % wrsp_dict['param_Name'], p=max_action_inf, w=inf_nums[0], inf_nums=inf_nums))
            except Exception as ex:
                self.search_in_action(word=lr_param.Snap.format(num=max_action_inf), hist=False)
                qb = 'param: "{p}"\nweb_reg_save_param: {n}'.format(
                    p=wrsp_dict['param_Name'], n='{%s}' % wrsp_dict['web_reg_num'])

                if self.force_yes_inf.get():
                    lr_log.Logger.warning('{q}\n\n{e}\n{wrsp}'.format(e=ex, q=qb, wrsp=wrsp))
                else:
                    y = lr_wlib.YesNoCancel(buttons=['Создать', 'Пропустить'], text_after=qb, text_before=str(ex),
                                            title='создать web_reg_save_param ?', parent=self).ask()
                    if y == 'Пропустить':
                        raise
                    else:
                        lr_log.Logger.info('{q}\n\n{e}'.format(e=ex, q=qb))

    def SearchAndReplace(self, search: str, replace='', wrsp_dict=None, wrsp=None, backup=False, is_param=True,
                         is_wrsp=True, replace_callback=None, rep_stat=False) -> None:
        '''VarWrspDict автозамена: [заменить param на {web_reg_save_param}]
        + [добавить блок с // web_reg_save_param, перед блоком c inf_line]'''
        assert search, 'пустой search "{s}" {ts}'.format(s=search, ts=type(search))

        if is_wrsp:
            if not wrsp_dict:  # текущий
                wrsp_dict = defaults.VarWrspDict.get()
            if not wrsp:
                wrsp = lr_param.web_reg_save_param.format(**wrsp_dict)

        if not replace:
            replace = wrsp_dict['web_reg_num']
        if is_param:
            replace = lr_param.param_bounds_setter(replace)

        self.param_inf_checker(wrsp_dict, wrsp)
        if backup:
            self.backup()

        # заменить
        if replace_callback:  # групповая замена
            replace_callback((search, replace))
        elif defaults.ReplaceParamDialogWindow:  # заменять с диалоговыми окнами, но без пула
            ask_dict = {}
            stats = {}
            for web_ in self.web_action.get_web_snapshot_all():
                res = web_.param_find_replace(search, replace, ask_dict)

                if rep_stat and any(res):
                    stats[web_.snapshot] = res
            if rep_stat:
                lr_log.Logger.debug(search + ':\n' + '\n'.join('{} inf: заменено [да|нет] раз: [{}|{}]'.format(
                    k, *stats[k]) for k in sorted(stats)))
        else:  # "быстрая" замена
            self.web_action.replace_bodys([(search, replace), ])

        if is_wrsp:  # вставить web_reg_save_param
            self.web_action.web_reg_save_param_insert(wrsp_dict, wrsp)

        if not replace_callback:
            self.web_action.websReport.create()
            self.web_action_to_tk_text()  # показать
            self.tk_text.set_highlight()

    def drop_file_none_inf_num_in_action(self) -> None:
        '''в LoadRunner могут быть inf-файлы, которых нету в action.c(например удалили лишний код), такие файлы надо
        отсеять, тк web_reg_save_param потом может на него сослатся'''
        self.action_infs[:] = [a.snapshot for a in self.web_action.get_web_snapshot_all()]
        self.drop_infs.clear()
        self.drop_files.clear()

        for file in defaults.AllFiles:
            check = False
            for inf in file['Inf']['Nums']:
                if inf in self.action_infs:
                    check = True
                else:
                    self.drop_infs.add(inf)
            if not check:
                self.drop_files.append(file['File']['Name'])

        self.show_info()

    def show_info(self) -> None:
        '''всякая инфа'''
        ldaf = len(defaults.AllFiles)
        lif = len(list(lr_other.get_files_infs(defaults.AllFiles)))
        lf = len([f for f in defaults.AllFiles if any(i in self.action_infs for i in f['Inf']['Nums'])])
        li = len(self.action_infs)
        alw = len(tuple(self.web_action.get_web_all()))

        defaults.Window.last_frame['text'] = '{d} > в {i} inf > {f} файлов'.format(
            d=defaults.VarFilesFolder.get(), f=len(defaults.AllFiles),
            i=len(list(lr_other.get_files_infs(defaults.AllFiles))))

        self.middle_bar['text'] = 'В action.c web_*: объектов[любых={alw} шт, snapshot={i} шт], файлов ответов[{f} шт] / Удалено: объектов[snapshot={ni} шт]' \
                                  '-> файлов ответов[{nf} шт]'.format(alw=alw, i=li, f=lf, ni=lif-li, nf=ldaf-lf)
        if self.drop_infs or self.drop_files:
            lr_log.Logger.debug('Отсутствует в action.c: inf: {il}, файлов : {fl} | Найдено: {ai} inf'.format(
                il=len(self.drop_infs), fl=len(self.drop_files), ai=li), parent=self)

    def backup(self) -> None:
        '''сделать action.c бэкап'''
        self._backup_index += 1
        if self._backup_index > int(self.backup_entry.get()):
            self._backup_index = 1

        d = defaults.BackupFolder
        if not os.path.isdir(d):
            os.makedirs(d)
        b_name = self.backup_name()
        with open(b_name, 'w', errors='replace', encoding=defaults.VarEncode.get()) as f:
            f.write(self.tk_text.get(1.0, tk.END))
        self.set_title()
        lr_log.Logger.debug('{} = {} byte'.format(b_name, os.path.getsize(b_name)))

    def session_params(self, lb_list=None, ask=True) -> list:
        '''поиск param в action? по LB='''
        if lb_list is None:
            lb_list = defaults.LB_PARAM_FIND_LIST

        if ask:
            text = self.tk_text.get(1.0, tk.END)
            lb_uuid = re.findall(r'uuid_\d=', text)
            lb_col_count = re.findall(r'p_p_col_count=\d&', text)

            text = '\n'.join(set(lb_list + lb_uuid + lb_col_count))
            y = lr_wlib.YesNoCancel(buttons=['Найти', 'Пропуск'], text_before='найти param по LB=',
                                    text_after='указать LB, с новой строки', is_text=text, title='автозамена по LB=',
                                    parent=self, default_key='Найти')
            if y.ask() == 'Найти':
                lb_list = y.text.split('\n')
            else:
                return []

        params = []
        for p in filter(bool, lb_list):
            params.extend(self._group_param_search(p, part_mode=False))
        return list(reversed(sorted(p for p in set(params) if p not in defaults.DENY_PARAMS)))

    def group_param_search(self, param_part: "zkau_") -> ["zkau_5650", "zkau_5680",]:
        '''поиск в action.c, всех уникальных param, в имени которых есть param_part'''
        params = list(set(self._group_param_search(param_part)))  # уникальных
        params.sort(key=lambda param: len(param), reverse=True)
        return params

    def _group_param_search(self, param_part: "zkau_", part_mode=True) -> iter(("zkau_5650", "zkau_5680", )):
        '''поиск в action.c, всех param, в имени которых есть param_part / или по LB'''
        for web_ in self.web_action.get_web_snapshot_all():
            split_text = web_.get_body().split(param_part)

            for index in range(len(split_text) - 1):
                left = split_text[index].rsplit('\n', 1)[-1].lstrip()
                right = split_text[index + 1].split('\n', 1)[0].rstrip()

                if lr_other.check_bound_lb(left) if part_mode else (right[0] in lr_param.wrsp_allow_symb):
                    param = []  # "5680"

                    for s in right:
                        if s in lr_param.wrsp_allow_symb:
                            param.append(s)
                        else:
                            break

                    if param:
                        param = ''.join(param)
                        if part_mode:  # param_part или по LB
                            param = param_part + param
                        yield param  # "zkau_5680"

    def tk_text_dummy_remove(self, force=False, mode='') -> bool:
        '''удалить все dummy web_submit_data'''
        text = self.tk_text.get(1.0, tk.END).strip()
        _web_action = lr_web_.ActionWebsAndLines(self)
        _web_action.set_text_list(text)

        if mode == 'endswith':
            is_remove = lr_template.dummy_endswith_remove
        else:
            is_remove = lr_template.dummy_remove

        rem = 0
        for web_ in tuple(_web_action.get_web_all()):
            if is_remove(web_.lines_list):
                _web_action.webs_and_lines.remove(web_)
                rem += 1

        _web_action.websReport.create()
        text_without_dummy = _web_action.to_str()
        dum_len = len(text)
        no_dum_len = len(text_without_dummy)

        if force or (dum_len != no_dum_len):
            text_t = tuple(self.web_action.get_web_all())
            text_w = tuple(_web_action.get_web_all())
            t1 = len(tuple(self.web_action.get_web_snapshot_all()))
            t2 = len(tuple(_web_action.get_web_snapshot_all()))
            ltn = len(text.split('\n')) - 1
            ldn = len(text_without_dummy.split('\n')) - 1
            if mode:
                _type = mode
                lwnt = len(text_t)
                lwnd = len(text_w)
            else:
                _type = lr_template.Dummy.web_dummy_template.split('("', 1)[0].strip()
                lwnt = len(tuple(w for w in text_t if w.type == _type))
                lwnd = len(tuple(w for w in text_w if w.type == _type))
            cd = max((t1 - t2, lwnt - lwnd))
            buttons = ['Удалить/Пересканировать', 'Пропустить', 'Выход']
            n1, n2, n3, n4 = '{}|Snapshot|строк|символов'.format(_type).split('|')

            ync = lr_wlib.YesNoCancel(
                buttons=buttons,
                text_before='Удалить {cd} шт. "dummy" - {web_name} из action.c текста?\n'
                            'Если изменить web_dummy_template текст,\n'
                            'action.c пересканируется, с повторным показом диалог окна.\n'
                            'inf удаляется, если его строки, начинаются\nна соответствующие им строки, '
                            'в web_dummy_template,\nбез учета начальных пробелов.'.format(web_name=_type, cd=cd),
                text_after='action.c до и после удаления {web_name}:\n'
                           '{n1:>20} {n2:>20} {n3:>20} {n4:>20}\n'
                           '{lwnt:>20} | {t1:>20} | {ltn:>20} | {d:>20} |\n'
                           '{lwnd:>20} | {t2:>20} | {ldn:>20} | {nd:>20} |'.format(
                    n1=n1, n2=n2, n3=n3, n4=n4, lwnt=lwnt, lwnd=lwnd, d=dum_len, nd=no_dum_len, t1=t1, t2=t2, ltn=ltn,
                    ldn=ldn, web_name=_type),
                title='web_dummy_template | удалить {rem} шт ?'.format(rem=rem),
                parent=self,
                is_text=lr_template.Dummy.web_dummy_template
            )
            y = ync.ask()

            if y == buttons[2]:
                return False

            template = ync.text.strip()
            if ((len(template) != lr_template.Dummy.web_len) or
                    (len(template.split('\n')) != lr_template.Dummy.dummy_len)):
                lr_template.Dummy.setattrs(template)
                return self.tk_text_dummy_remove()

            if y == buttons[0]:
                self.backup()
                self.tk_text.new_text_set(text_without_dummy)
                self.web_action = _web_action
                self.web_action_to_tk_text()

            if y in buttons[:2]:
                return True


def _action_file(file='action.c') -> str:
    '''найти action.c'''
    if os.path.isfile(file):
        return file
    else:
        fff = os.path.join(defaults.VarFilesFolder.get(), file)
        if os.path.isfile(fff):
            return fff
        else:
            return ''