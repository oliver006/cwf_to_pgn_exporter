#!/usr/bin/python
"""

The MIT License (MIT)

Copyright (c) 2016 - Oliver

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import argparse
import json
import requests
import uuid
import xmltodict
import random
import sys

SIDE_WHITE = 'W'
SIDE_BLACK = 'B'

RESULT_CHECKMATE = 'CHECKMATE'
RESULT_RESIGNED  = 'RESIGNED'
RESULT_DECLINED  = 'DECLINED'

VERSION = "0.1.1"


def get_games(username, password):
    device_token = '%20'.join([''.join([random.choice("1234567890abcdef") for i in range(8)]) for i in range(8)])
    headers = {
        "Accept": "text/xml",
        'Content-Type': 'application/xml',
        'Device-Model': 'iPad',
        "User-Agent": "ChessWithFriends/4.30.0 CFNetwork/711.4.6 Darwin/14.0.0",
        "Device-OS": "9.1",
        "wfpw": str(uuid.uuid4()).upper(),
        "zdid": str(uuid.uuid4()).upper(),
        "zpid": str(uuid.uuid4()).upper(),
    }
    url = "https://chesswithfriends.zyngawithfriends.com/games?game_type=ChessGame&get_current_user=true&device_token=" + device_token + "&moves_since=0&games_since=0001-12-30%2000:00:00+00:00"

    try:
        r = requests.get(url, auth=(username, password), headers=headers)
        if not r.text or r.status_code != 200:
            return False, ""

        d = xmltodict.parse(r.text)
        parsed_games = [game_to_pgn(game) for game in d.get('games', {}).get('game', [])]

        return parsed_games, r.text

    except Exception as ex:
        print (ex)

    return False, ""


trans_map = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}


def xy_to_coord(xy):
    return "%s%d" % (trans_map[int(xy[0])], 8 - int(xy[1]))


def xy_to_board_loc(xy):
    loc = int(xy[0]) + int(xy[1]) * 8
    return loc


def move_to_san(move):
    move_from_xy = (int(move['from-x']), int(move['from-y']))
    move_to_xy = (int(move['to-x']), int(move['to-y']))

    if move_from_xy[0] == 97:
        return RESULT_DECLINED

    if move_from_xy[0] == 99:
        return RESULT_RESIGNED

    if move_from_xy[0] == 100:
        return RESULT_CHECKMATE

    prev_board = json.loads(move['data'])['prev_board'].replace("e", " ")
    piece_src = prev_board[xy_to_board_loc(move_from_xy)].upper()
    piece_dst = prev_board[xy_to_board_loc(move_to_xy)].upper()
    square_from = xy_to_coord(move_from_xy)
    square_to = xy_to_coord(move_to_xy)

    san_movetext = ''

    if piece_src != 'P':
        san_movetext = piece_src

    if piece_dst == ' ':

        san_movetext += square_to

        # todo: still missing, en passant

        # pawn promotion
        # todo: currently, this is handling promotion to queen only
        if piece_src == 'P' and (move_to_xy[1] == 7 or move_to_xy[1] == 0):
            pawn_promo_map = {'101': 'Q', '201': 'Q'} # black and white queen got separate codes?
            san_movetext += "=" + pawn_promo_map[move['promoted']]

        # castling
        if piece_src == 'K' and abs(move_from_xy[0] - move_to_xy[0]) == 2:
            if move_to_xy[0] > move_from_xy[0]:
                san_movetext = "O-O"  # kingside
            else:
                san_movetext = 'O-O-O'  # queenside

    else:
        # uh oh, someone got hurt

        # unless it's a King or Queen we'll add the full "from" field
        if not piece_src in ['Q', 'K']:
            san_movetext += square_from

        san_movetext += "x"
        san_movetext += square_to

    return san_movetext

def game_to_pgn(game):
    res = list()

    try:
        game_id = game['id']
        player_white = game['users']['user'][0]
        player_black = game['users']['user'][1]

        game_date = game['created-at'][:10].replace("-", ".")

        # remove "@type"
        assert game['moves'].popitem(False) == (u'@type', u'array')

        # needed cause single moves are not returned as an array via [0] but as ['move']
        temp_moves = game['moves'].popitem(False)[1]
        moves = temp_moves if isinstance(temp_moves, list) else [temp_moves]

        move_num = 1
        movetext = ""
        game_ending = False

        while moves:
            move = moves.pop(0)
            move_san = move_to_san(move)
            current_side = SIDE_WHITE if move_num % 2 == 1 else SIDE_BLACK

            # todo: need to figure out what a daw looks like
            if move_san == RESULT_CHECKMATE:
                game_ending = current_side
                movetext += "# "
                break

            if move_san == RESULT_RESIGNED:
                game_ending, player_resigning = ('B', 'white') if current_side == SIDE_WHITE else ('W', 'black')
                movetext += " {%s resigned}" % (player_resigning)
                break

            if current_side == SIDE_WHITE:
                movetext += " %d." % int(move_num / 2 + 1)

            movetext += " %s" % move_san
            move_num += 1

        if game_ending:
            pgn_round = "-"

            # todo: not handling a draw yet
            pgn_result = "1-0" if game_ending == SIDE_WHITE else '0-1'
            movetext += " %s" % pgn_result
        else:
            pgn_round = int(move_num / 2)
            pgn_result = "*"

        res.append('[Event "CWF Game between %s and %s (id: %s)"]' % (player_white['name'],
                                                                     player_black['name'],
                                                                     game_id))
        res.append('[Site "Chess With Friends"]')
        res.append('[Annotator "https://github.com/oliver006/cwf_to_pgn_exporter"]')
        res.append('[Date "%s"]' % game_date)
        res.append('[Round "%s"]' % pgn_round)
        res.append('[White "%s"]' % player_white['name'])
        res.append('[Black "%s"]' % player_black['name'])
        res.append('[Result "%s"]' % pgn_result)
        res.append(movetext.strip())

    except Exception as ex:
        res.append("Failed to generate PGN for game:")
        res.append(str(game))
        res.append("Exception:")
        res.append(str(ex))

    return res

def main():
    print ("CWF to PGN Exporter v%s" % VERSION)
    parser = argparse.ArgumentParser(description='Export Chess With Friends games to PGN')
    parser.add_argument('--username', dest='username', help='CWF account username')
    parser.add_argument('--password', dest='password', help='CWF account password')
    parser.add_argument('--xml-file-out', dest='xml_file_out', help='Save xml response to file')
    args = parser.parse_args()

    if not args.username or not args.password:
        parser.print_help(sys.stdout)
        exit(-1)

    import ipdb; ipdb.set_trace()
    games, raw_xml = get_games(args.username, args.password)

    if games is False:
        print ("Couldn't retrieve games - wrong login info?")
    else:
        print ("Authenticated and downloaded XML data")

        if args.xml_file_out:
            print ("Writing XML data to %s" % args.xml_file_out)
            with open(args.xml_file_out, 'w+') as fout:
                fout.write(raw_xml.encode("utf-8"))

        print ("Found %d games" % len(games))
        print ("\nGames in PGN:\n\n")
        for game in games:
            print ("\n".join(game))
            print ("\n\n\n")


if __name__ == "__main__":
    main()
