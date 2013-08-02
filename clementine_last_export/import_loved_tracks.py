#!/usr/bin/python
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Script which allows to gives 5 stars in the Clementine database for last.fm loved tracks
"""

import sqlite3
import re
import codecs

import os, platform

from optparse import OptionParser
import logging
from logging import info, warning, error, debug

from lastexport import main as lastexporter
from db_management import backup_db, update_rating, is_in_db

#########################################################################
#    Functions
#########################################################################

def parse_line(ligne):
    """
    Read a last.fm extract line and return the artist and song part
    """
    regexp = re.compile(""".*?\t(.*?)\t(.*?)\t.*""")
    if regexp.match(ligne):
        titre,artiste = regexp.findall(ligne)[0]
    else:
        titre, artiste = None,None
        debug("""The following line cannot be parsed: %s""" %ligne[:-1])
    return titre, artiste

def update_db_file(database, extract, force_update=True):
    """
    Update a database according to an extract file
    """
    connection = sqlite3.connect(database)
    extract_file = codecs.open(extract, encoding='utf-8')
    biblio = {}    
    matched = []
    not_matched = []
    already_ok = []
        
    #Loop which will read the extract and store each play to a dictionary
    for line in extract_file.readlines():
        titre, artiste = parse_line(line)
        if biblio.has_key(artiste):
            if biblio[artiste].has_key(titre):
                biblio[artiste][titre] = biblio[artiste][titre] +1
            else:
                biblio[artiste][titre] = 1
        elif artiste == None or titre == None:
            pass
        else:
            biblio[artiste] = {}
            biblio[artiste][titre] = 1
            
    #Loop which will try to update the database with each entry of the dictionnary           
    for artiste in biblio.keys():
        for titre in biblio[artiste].keys():
            original_rating, playcount = is_in_db(connection, artiste, titre)
            if original_rating == None:
                not_matched.append(artiste+' '+titre)
                debug("""Song %s from %s cannot be found in the database""" %(titre,artiste))
            elif original_rating == 4.5/5 and not force_update:
                already_ok.append(artiste+' '+titre)
            elif original_rating < 1:
                update_rating(connection, artiste, titre, 1)
                matched.append(artiste+' '+titre)
            else:
                already_ok.append(artiste+' '+titre)
    try:
        connection.commit()
    except sqlite3.Error, err:
        connection.rollback()
        error(unicode(err.args[0]))            
        
    extract_file.close()
    connection.close()
    return matched, not_matched, already_ok
    
#######################################################################
#    Main
#######################################################################

def import_loved_tracks(username, input_file, server, extract_file, startpage, backup, force_update=True, use_cache=False):
    operating_system = platform.system()
    if operating_system == 'Linux':
        db_path = '~/.config/Clementine/'
    if operating_system == 'Darwin':
        db_path = '~/Library/Application Support/Clementine/'
    if operating_system == 'Windows':
        db_path = '%USERPROFILE%\\.config\\Clementine\\'''
    
    if not input_file:
        info("No input file given, extracting directly from %s servers" %server)
        lastexporter(server, username, startpage, extract_file, infotype='lovedtracks', use_cache=use_cache)

    if backup:
        backup_db(db_path)
    
    info("Reading extract file and updating database")    
    matched, not_matched, already_ok = update_db_file(os.path.expanduser("%s/clementine.db" %db_path), extract_file, force_update)
    
    info("%d entries have been updated, %d entries have already the correct note, no match was found for %d entries" %(len(matched), len(already_ok), len(not_matched)))


if __name__ == "__main__":
    parser = OptionParser()
    parser.usage = """Usage: %prog <username> [options]
    
    Script which will extract data from the server and update clementine database
    <username> .......... Username used in the server
    """

    parser.add_option("-p", "--page", dest="startpage", type="int", default="1", help="page to start fetching tracks from, default is 1")
    parser.add_option("-e", "--extract-file", dest="extract_file", default="loved_tracks.txt", help="extract file name, default is loved_tracks.txt")
    parser.add_option("-s", "--server", dest="server", default="last.fm", help="server to fetch track info from, default is last.fm")
    parser.add_option("-b", "--backup", dest="backup", default=False, action="store_true", help="backup db first")
    parser.add_option("-i", "--input-file", dest="input_file", default=False, action="store_true", help="use the already extracted file as input")
    parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true", help="debug mode")
    parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true", help="activate verbose mode")
    
    options, args = parser.parse_args()
    if options.verbose:
        logging.basicConfig(level="INFO")
    if options.debug:
        logging.basicConfig(level="DEBUG")
        
    import_loved_tracks(args[0], options.input_file, options.server, options.extract_file, options.startpage, options.backup, options.use_cache)
