#
# Loxodo -- Password Safe V3 compatible Password Vault
# Copyright (C) 2014 Okami <okami@fuzetsu.info>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
import os
import re
import time
import Queue

from hashlib import md5

from HTMLParser import HTMLParser

from PyQt4 import QtGui
from PyQt4.QtNetwork import (QNetworkAccessManager, QNetworkCookieJar,
    QNetworkRequest)
from PyQt4.QtCore import (Qt, QUrl, QEventLoop, QThread, SIGNAL)

from .settings import COLUMNS_BY_FIELD

from ...config import config


class FaviconFinder(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.favicon_url = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'link' and 'href' in attributes and 'icon' in attributes.get('rel'):
            if not self.favicon_url:
                self.favicon_url = attributes['href']


class FaviconUpdater(QThread):
    def __init__(self):
        super(FaviconUpdater, self).__init__()
        self.cache = config.get_cache_dir()
        self.queue = Queue.Queue()
        self.running = True
        self.faviconReady = SIGNAL('faviconReady')

    def __del__(self):
        self.wait()

    def stop_me(self):
        self.running = False

    def _get(self, url):
        loop = QEventLoop()
        request = QNetworkRequest()
        request.setAttribute(QNetworkRequest.CacheLoadControlAttribute,
            QNetworkRequest.PreferCache);
        request.setRawHeader('User-agent',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64)')
        request.setUrl(url)
        cookies = QNetworkCookieJar()
        manager = QNetworkAccessManager()
        manager.setCookieJar(cookies)
        reply = manager.get(request)
        reply.finished.connect(loop.quit)
        loop.exec_()
        data = reply.readAll()
        code, ok = reply.attribute(
            QNetworkRequest.HttpStatusCodeAttribute).toInt()
        if code in (301, 302):
            redirect = reply.attribute(
                QNetworkRequest.RedirectionTargetAttribute).toUrl()
            return self._get(redirect)
        else:
            return data

    def _parse_favicon(self, page):
        favicon_url = None
        #### HTMLParser method
        # finder = FaviconFinder()
        # finder.feed(page)
        # favicon_url = finder.favicon_url
        #### BeautifulSoup method
        # from BeautifulSoup import BeautifulSoup
        # soup = BeautifulSoup(page)
        # link = soup.html.head.find(
        #     lambda x: x.name == 'link' and 'icon' in x['rel'])
        # if link:
        #     favicon_url = link['href']
        #### RegExp method
        if not favicon_url:
            link = r'(?P<link><link[^>]+rel=[\'\"][\w ]*icon[\'\"][^>]*/?>)'
            href = r'href=[\'\"](?P<href>[^\'\"]+)[\'\"]'
            s = re.search(link, str(page))
            if s and s.group('link'):
                s = re.search(href, s.group('link'))
                if s and s.group('href'):
                    favicon_url = s.group('href')
        return favicon_url

    def _get_favicon(self, item):
        url = item.data(COLUMNS_BY_FIELD['url'], Qt.EditRole).toString()
        path = os.path.join(self.cache, md5(str(url)).hexdigest())
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size <= 1:
                return
            f = open(path)
            favicon = f.read()
            f.close()
        else:
            page = self._get(QUrl(url))
            favicon_url = self._parse_favicon(str(page)) or '/favicon.ico'
            favicon = self._get(QUrl(url).resolved(QUrl(favicon_url)))
            f = open(path, 'w+')
            f.write(favicon)
            f.close()
        image = QtGui.QImage()
        image.loadFromData(favicon)
        self.emit(self.faviconReady, item, image)

    def run(self):
        while self.running:
            try:
                item = self.queue.get()
                try:
                    self._get_favicon(item)
                except Exception as e:
                    print(e)
                    # pass
                self.queue.task_done()
            except Queue.Empty:
                time.sleep(0.1)

    def on_url_updated(self, item):
        self.queue.put(item)
