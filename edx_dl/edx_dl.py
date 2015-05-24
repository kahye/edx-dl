#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
edx-dl is a simple tool to download video lectures from edx.org.

It requires a Python interpreter (>= 2.6), youtube-dl, BeautifulSoup4 and
should be platform independent, meaning that it should work fine in your
Unix box, in Windows or in Mac OS X.
"""
from __future__ import print_function


import argparse
import json
import logging
import re
import sys
import os
import glob
from bs4 import BeautifulSoup

from . import compat
from .utils import (get_initial_token, get_course_list, get_page_contents)


def parse_args():
    """
    Parse the arguments/options passed to the program on the command line.
    """

    parser = argparse.ArgumentParser(prog='edx-dl',
                                     description='Get videos from edX-based sites',
                                     epilog='For further use information, '
                                     'see the file README.md')

    # positional
    parser.add_argument('course_id',
                        nargs='*',
                        action='store',
                        default=None,
                        help='target course id '
                        '(e.g., https://courses.edx.org/courses/BerkeleyX/CS191x/2013_Spring/courseware/)'
                        )

    # optional
    parser.add_argument('-u',
                        '--username',
                        action='store',
                        help='your edX username (email)')
    parser.add_argument('-p',
                        '--password',
                        action='store',
                        help='your edX password')
    parser.add_argument('-w',
                        '--weeks',
                        dest='weeks',
                        action='store',
                        default=None,
                        help='weeks of classes to download (default: all)')
    parser.add_argument('-f',
                        '--format',
                        dest='format',
                        action='store',
                        default=None,
                        help='format of videos to download (default: best)')
    parser.add_argument('-l',
                        '--list-courses',
                        dest='list_courses',
                        action='store_true',
                        default=False,
                        help='list courses currently enrolled')
    parser.add_argument('-s',
                        '--with-subtitles',
                        dest='subtitles',
                        action='store_true',
                        default=False,
                        help='download subtitles with the videos')
    parser.add_argument('--debug',
                        dest='debug',
                        action='store_true',
                        default=False,
                        help='print debugging information')

    args = parser.parse_args()

    # FIXME: check arguments
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if not args.username:
        logging.error('No username specified.')
        sys.exit(1)
    if not args.password:
        logging.error('No password specified.')
        sys.exit(1)

    if not args.list_courses and len(args.course_id) == 0:
        logging.error('You must specify at least one course_id'
                      ' or the \'-l\' switch. Please see the documentation.')
        sys.exit(1)

    return args


def main():
    args = parse_args()

    user_email = args.username
    user_pswd = args.password
    video_fmt = args.format

    # FIXME: Proof of concept---refactor this to a function to the utils
    # module.

    # FIXME: We consider only the first course that is passed as argument.
    # We should fix this.

    # "Old-style" course URLs
    # URLs like https://courses.edx.org/courses/UTAustinX/UT.5.02x/1T2015/info
    regex = r'(?:https?://)(?P<site>[^/]+)/(?P<baseurl>[^/]+)/(?P<institution>[^/]+)/(?P<class>[^/]+)/(?P<offering>[^/]+).*'
    m = re.match(regex, args.course_id[0])  # FIXME: considering only the first one
    old_style_url = True

    if m is None:
        # URLs like https://courses.edx.org/courses/course-v1:Microsoft+DEV204x+2015_T2/info
        regex = r'(?:https?://)(?P<site>[^/]+)/(?P<baseurl>[^/]+)/(?P<course_version>[^:]+):(?P<institution>[^+]+)\+(?P<class>[^+]+)\+(?P<offering>[^/]+).*'
        m = re.match(regex, args.course_id[0])  # FIXME: considering only the first one
        old_style_url = False


    if m is None:
        logging.error('The URL provided is not valid for edX.')
        sys.exit(0)

    if m.group('site') in ['courses.edx.org', 'class.stanford.edu']:
        login_suffix = 'login_ajax'
    else:
        login_suffix = 'login'


    homepage = 'https://' + m.group('site')
    login_url = homepage + '/' + login_suffix
    dashboard = homepage + '/dashboard'
    if old_style_url:
        course_id = '%s/%s/%s' % (m.group('institution'),
                                  m.group('class'),
                                  m.group('offering'))
    else:
        course_id = '%s:%s+%s+%s' % (m.group('course_version'),
                                     m.group('institution'),
                                     m.group('class'),
                                     m.group('offering'))

    logging.debug('Old-style url: %s', old_style_url)
    logging.debug('Homepage: %s', homepage)
    logging.debug('Login URL: %s', login_url)
    logging.debug('Dashboard: %s', dashboard)
    logging.debug('Course ID: %s', course_id)

    logging.debug('Preparing headers.')
    headers = {
        'User-Agent': 'edX-downloader/0.01',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        'Referer': homepage,
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': get_initial_token(homepage),
    }

    logging.debug('Preparing login information.')
    post_data = compat.urlencode({'email': user_email,
                                  'password': user_pswd,
                                  'remember': False}).encode('utf-8')
    request = compat.Request(login_url, post_data, headers)
    response = compat.urlopen(request)
    logging.debug('Opened request to %s', login_url)

    logging.debug('Grabbing response data')
    data = response.read().decode('utf-8')
    resp = json.loads(data)
    logging.debug('Got: %s', data)
    if not resp.get('success', False):
        logging.error('Problems suppling credentials to edX.')
        exit(2)

    # FIXME: This doesn't belong here, probably, but in the validation of
    # the command line options, instead.
    if args.list_courses:
        courses = get_course_list(headers, dashboard)
        for course in courses:
            print('%s:%s:%s' % course)
        sys.exit(0)

    course_urls = []

    # FIXME: Kludgy
    new_url = "%s/courses/%s/courseware" % (homepage, course_id)
    logging.info('Found new course URL: %s', new_url)
    course_urls.append(new_url)

    # FIXME: Put this in a function called get_week_urls_for_course() or
    # similar in intent.

    # FIXME: Consider all courses here.
    # ...
    url = course_urls[0]

    courseware = get_page_contents(url, headers)
    # with open('page.html', 'w') as f:
    #    f.write(courseware)
    soup = BeautifulSoup(courseware)
    data = soup.find('nav',
                     {'aria-label':'Course Navigation'})

    if data is None:
        data = soup.find('section',
                         {'class':'container'})

    weeks = []

    weeks_soup = data.find_all('div')
    for week_soup in weeks_soup:
        week_name = week_soup.h3.a.string
        week_urls = [
            '%s/%s' % (homepage, a['href'])
            for a in week_soup.ul.find_all('a')
        ]

        weeks.append((week_name, week_urls))

    # FIXME: Take the week into consideration
    # FIXME: Transform this into a function
    # FIXME: Consider all courses here.
    c_id = args.course_id[0]
    logging.info('%s has %d weeks so far.', c_id, len(weeks))

    weeknum = 1
    for (week_name, week_urls) in weeks:
        directory = week_name.strip().rstrip('.').replace(':', ' -')
        directory = "%02d - %s" % (weeknum, directory)
        weeknum += 1
                
        if not os.path.exists(directory):
            os.makedirs(directory)
        os.chdir(directory)
        
        lecturenum = 1
        for url in week_urls:
            page = get_page_contents(url, headers)
            
            soup = BeautifulSoup(page)
            page_title = soup.title.text
            page_title = page_title.strip()
            page_title2 = re.search(b'(.*?)\|', page_title)
            if page_title2 != None:
                page_title = page_title2.group(1)

            page_title = "%02d - %s" % (lecturenum, page_title.replace(':', ' -'))
            lecturenum += 1

            if not os.path.exists(page_title):
                os.makedirs(page_title)
            os.chdir(page_title)

            regexps = [b'data-streams=&#34;(?:0.75:.{11},)?1.00?:(.{11})',
                        b'data-youtube-id-1-0=&#34;(.{11})&#34;']
            for regexp in regexps:
                id_container = re.findall(regexp, page)
                logging.debug('New style got: %s', id_container)
                
                videonum = 1
                for vid in id_container:
                    video_filename = "%02d.mp4" % videonum
                    cmd = "youtube-dl --all-subs -f mp4 -o %s" % video_filename
                    os.system(cmd + " -- %s" % vid)
                    videonum += 1

            try:
                fnames = glob.glob('*.en.srt')
            
                for fname in fnames:
                    os.rename(fname, fname[:-6] + 'srt')
            except OSError:
                pass
    
            os.chdir('..')
        os.chdir('..')

if __name__ == '__main__':
    main()
