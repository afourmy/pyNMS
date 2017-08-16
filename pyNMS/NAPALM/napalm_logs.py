# Copyright (C) 2017 Antoine Fourmy <antoine dot fourmy at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pyQT_widgets.Q_console_edit import QConsoleEdit

class NapalmLogs(QConsoleEdit):
    
    # Logs

    def __init__(self, node):
        super().__init__()
        self.node = node
        self.update()
        
    def update(self):
        self.clear()
        if 'cli' in self.node.napalm_data:
            self.insertPlainText(self.node.napalm_data['cli']['show logging'])
            

                        