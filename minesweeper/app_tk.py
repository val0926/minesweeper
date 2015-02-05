# coding=utf8
"""
由Tkinter实现的扫雷GUI
"""
import os
import webbrowser
import Tkinter as tk
import tkMessageBox

import settings
from core.minesweeper import Game
from core.helpers import LevelMapConfig
from core.helpers import create_from_mine_number
from widgets.style import ButtonStyle
from widgets import textView
from widgets.widgets import CounterLabel
from widgets.widgets import TimerLabel
from widgets.widgets import MapParamsInputDialog


class App(tk.Frame):
    def __init__(self):
        tk.Frame.__init__(self)
        self.master.title(settings.APP_NAME)
        self.master.resizable(False, False)
        self.pack(expand=tk.NO, fill=tk.BOTH)
        self.create_top_menu()
        mine_map = LevelMapConfig.level_map(LevelMapConfig.LEVEL_BEGINNER)
        self.map_frame = None
        self._create_map_frame(mine_map)

    def create_top_menu(self):
        top = self.winfo_toplevel()
        self.menu_bar = tk.Menu(top)
        top['menu'] = self.menu_bar

        game_menu = tk.Menu(self.menu_bar)
        game_menu.add_command(label='退出', command=self._exit_handler)
        self.menu_bar.add_cascade(label='游戏', menu=game_menu)

        map_menu = tk.Menu(self.menu_bar)
        level_menu = tk.Menu(map_menu)
        self.level = tk.IntVar()
        self.level.set(LevelMapConfig.LEVEL_BEGINNER)
        for level, label in LevelMapConfig.CHOICES:
            level_menu.add_radiobutton(label=label,
                                       variable=self.level,
                                       value=level,
                                       command=self._level_map_handler)
        map_menu.add_cascade(label='选择水平', menu=level_menu)
        map_menu.add_separator()
        map_menu.add_command(label='自定义地图参数', command=self._show_nap_set_dialog)
        self.menu_bar.add_cascade(label='地图', menu=map_menu)

        about_menu = tk.Menu(self.menu_bar)
        about_menu.add_command(label='访问项目主页', command=self._redirect_project_homepage)
        about_menu.add_command(label='关于...', command=self._show_about_info)
        self.menu_bar.add_cascade(label='关于', menu=about_menu)

    def _level_map_handler(self):
        level = self.level.get()
        mine_map = LevelMapConfig.level_map(level)
        self._create_map_frame(mine_map)

    def _create_map_frame(self, mine_map):
        if self.map_frame:
            self.map_frame.pack_forget()
        self.map_frame = GameFrame(mine_map)
        self.map_frame.pack(side=tk.TOP)

    def _show_nap_set_dialog(self):
        return MapParamsInputDialog(self, callback=App.get_map_params)

    def get_map_params(self, params_dict):
        new_map = create_from_mine_number(**params_dict)
        self._create_map_frame(new_map)

    def _exit_handler(self):
        self.quit()

    def _redirect_project_homepage(self):
        webbrowser.open_new_tab(settings.OSC_URL)

    def _show_about_info(self):
        self.display_file_text('关于', 'project.txt')

    def display_file_text(self, title, filename, encoding=None):
        fn = os.path.join(settings.STATIC_DIR, filename)
        textView.view_file(self, title, fn, encoding)


class GameFrame(tk.Frame):
    def __init__(self, mine_map):
        tk.Frame.__init__(self)
        self._create_controller_frame()
        self._create_info_frame()
        self.map_frame = tk.Frame(self)
        self.map_frame.pack(side=tk.TOP, expand=tk.YES, padx=10, pady=10)
        self.game = Game(mine_map)
        height, width = mine_map.height, mine_map.width
        self.bt_map = [[None for i in xrange(0, width)] for i in xrange(0, height)]
        for x in xrange(0, height):
            for y in xrange(0, width):
                self.bt_map[x][y] = tk.Button(self.map_frame, text='', width=3, height=1,
                                              command=lambda x=x, y=y: self._sweep_mine(x, y))
                self.bt_map[x][y].config(ButtonStyle.grid_unknown_style)

                def _mark_mine(event, self=self, x=x, y=y):
                    return self.mark_grid_as_mine(event, x, y)

                self.bt_map[x][y].bind('<Button-3>', _mark_mine)
                self.bt_map[x][y].grid(row=x, column=y)

    def _create_controller_frame(self):
        self.controller_bar = tk.Frame(self)
        self.controller_bar.pack(side=tk.TOP, fill=tk.X, expand=tk.YES, padx=2, pady=2)
        self.start_bt = tk.Button(self.controller_bar, text='新游戏', relief=tk.GROOVE, command=self._start)
        self.start_bt.pack(side=tk.LEFT, expand=tk.NO)
        self.reset_bt = tk.Button(self.controller_bar, text='重置', relief=tk.GROOVE, command=self._reset)
        self.reset_bt.pack(side=tk.LEFT, expand=tk.NO)
        self.map_info_bt = tk.Button(self.controller_bar, text='地图', relief=tk.GROOVE, command=self._show_map_info)
        self.map_info_bt.pack(side=tk.LEFT, expand=tk.NO)

    def _show_map_info(self):
        map_info_str = '当前地图大小：%d X %d\n地雷数目：%d' % (self.game.height, self.game.width, self.game.mine_number)
        tkMessageBox.showinfo('当前地图', map_info_str, parent=self)

    def _create_info_frame(self):
        self.info_frame = tk.Frame(self)
        self.info_frame.pack(side=tk.TOP, fill=tk.X, expand=tk.YES)
        self.step_text_label = tk.Label(self.info_frame, text='当前步数')
        self.step_text_label.pack(side=tk.LEFT, fill=tk.X, expand=tk.NO)
        self.step_count_label = CounterLabel(self.info_frame, init_value=0, step=1)
        self.step_count_label.pack(side=tk.LEFT, fill=tk.X, expand=tk.NO)
        self.flag_text_label = tk.Label(self.info_frame, text='地雷标记')
        self.flag_text_label.pack(side=tk.LEFT, fill=tk.X, expand=tk.NO)
        self.flag_count_label = CounterLabel(self.info_frame, init_value=0, step=1)
        self.flag_count_label.pack(side=tk.LEFT, fill=tk.X, expand=tk.NO)
        self.timer_text_label = tk.Label(self.info_frame, text='时间')
        self.timer_text_label.pack(side=tk.LEFT, fill=tk.X, expand=tk.NO)
        self.timer_count_label = TimerLabel(self.info_frame)
        self.timer_count_label.pack(side=tk.LEFT, fill=tk.X, expand=tk.NO)

    def _start(self):
        mine_map = create_from_mine_number(self.game.height, self.game.width, self.game.mine_number)
        self.game = Game(mine_map)
        self.draw_map()
        self.step_count_label.set_counter_value()
        self.flag_count_label.set_counter_value()
        self.timer_count_label.reset()

    def _reset(self):
        self.game.reset()
        self.draw_map()
        self.step_count_label.set_counter_value()
        self.flag_count_label.set_counter_value()
        self.timer_count_label.reset()

    def _sweep_mine(self, x, y):
        if self.game.swept_state_map[x][y]:
            return
        if not self.timer_count_label.state:
            self.timer_count_label.start_timer()
        state = self.game.play((x, y))
        self.step_count_label.set_counter_value(str(self.game.cur_step))
        self.draw_map()
        if state == Game.STATE_SUCCESS:
            self.timer_count_label.stop_timer()
            tkMessageBox.showinfo('提示', '恭喜你通关了！', parent=self)
        elif state == Game.STATE_FAIL:
            self.timer_count_label.stop_timer()
            tkMessageBox.showerror('提示', '很遗憾，游戏失败！', parent=self)

    def mark_grid_as_mine(self, event, x, y):
        if self.game.state == Game.STATE_PLAY and not self.game.swept_state_map[x][y]:
            cur_text = self.bt_map[x][y]['text']
            if cur_text == '?':
                cur_text = ''
                self.flag_count_label.decrease()
            elif cur_text == '':
                cur_text = '?'
                self.flag_count_label.increase()
            self.bt_map[x][y]['text'] = cur_text


    def draw_map(self):
        # 重画地图
        for i in xrange(0, self.game.height):
            for j in xrange(0, self.game.width):
                if self.game.swept_state_map[i][j]:
                    if self.game.mine_map.is_mine((i, j)):
                        self.bt_map[i][j].config(ButtonStyle.grid_mine_style)
                    else:
                        tmp = self.game.mine_map.distribute_map[i][j]
                        self.bt_map[i][j].config(ButtonStyle.grid_tip_style(tmp))
                else:
                    if self.bt_map[i][j]['text'] == '?':
                        self.bt_map[i][j].config(ButtonStyle.grid_marked_style)
                    else:
                        self.bt_map[i][j].config(ButtonStyle.grid_unknown_style)


def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()