"""
    urlresolver XBMC Addon
    Copyright (C) 2015 tknorris

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
from lib import jsunpack
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError
import string

rot13 = string.maketrans(
    "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
    "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")

class CdaResolver(UrlResolver):
    name = "cda"
    domains = ['cda.pl', 'www.cda.pl', 'ebd.cda.pl']
    pattern = '(?://|\.)(cda\.pl)/(?:.\d+x\d+|video)/([0-9a-zA-Z]+).*?'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        headers = {'Referer': web_url, 'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        try: html = html.encode('utf-8')
        except: pass
        match = re.compile('<a data-quality="(.*?)" href="(.*?)".*?>(.*?)</a>', re.DOTALL).findall(html)
        match20 = re.search("['\"]file['\"]:['\"](.*?\.mp4)['\"]", html)


        if match:
            mylinks =sorted(match, key=lambda x: x[2])
            html = self.net.http_GET(mylinks[-1][1], headers=headers).content
            match20 = re.search("['\"]file['\"]:['\"](.*?\.mp4)['\"]", html)
            if match20:
                mylink = match20.group(1).replace("\\", "")
                return self.check_vid(mylink) + self.appendHeaders('http://static.cda.pl/flowplayer/flash/flowplayer.commercial-3.2.18.swf')

            html = jsunpack.unpack(re.search("eval(.*?)\{\}\)\)", html, re.DOTALL).group(1))
            match7 = re.search('src="(.*?).mp4"',html)
            if match7:
                return self.check_vid(match7.group(1)) + '.mp4' + self.appendHeaders('http://static.cda.pl/flowplayer/flash/flowplayer.commercial-3.2.18.swf')
        else:
            match20 = re.search("['\"]file['\"]:['\"](.*?)['\"]", html)
            if match20:
                mylink = match20.group(1).replace("\\", "")
                return self.check_vid(mylink) + self.appendHeaders('http://static.cda.pl/flowplayer/flash/flowplayer.commercial-3.2.18.swf')
            html1 = jsunpack.unpack(re.search("eval(.*?)\{\}\)\)", html, re.DOTALL).group(1))
            match7 = re.search('src="(.*?).mp4"',html1)

            if match7:
                return self.check_vid(match7.group(1)) + '.mp4'+self.appendHeaders('http://static.cda.pl/flowplayer/flash/flowplayer.commercial-3.2.18.swf')
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return 'http://ebd.cda.pl/620x368/%s' % media_id

    def check_vid(self, videolink):
        if re.match('uggc', videolink):
            videolink = string.translate(videolink, rot13)
            videolink = videolink[:-7] + videolink[-4:]
        return videolink

    def appendHeaders(self, playerUrl):
        return helpers.append_headers({'Cookie': 'PHPSESSID = 1', 'Referer': playerUrl})