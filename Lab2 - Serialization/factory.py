from player import Player
from datetime import datetime
import xml.etree.ElementTree as ET
import player_pb2

class PlayerFactory:
    def to_json(self, players):
        '''
            This function should transform a list of Player objects into a list with dictionaries.
        '''
        player_json = []
        for player in players:
            player_dict = {
                "nickname": player.nickname,
                "email": player.email,
                "date_of_birth": player.date_of_birth.strftime("%Y-%m-%d"),
                "xp": player.xp,
                "class": player.cls,
            }
            player_json.append(player_dict)
        return player_json
        # pass

    def from_json(self, list_of_dict):
        '''
            This function should transform a list of dictionaries into a list with Player objects.
        '''
        players = []
        for player_dict in list_of_dict:
            player = Player(
                player_dict["nickname"],
                player_dict["email"],
                player_dict["date_of_birth"],
                player_dict["xp"],
                player_dict["class"],
            )
            players.append(player)
        return players
        # pass

    def from_xml(self, xml_string):
        '''
            This function should transform a XML string into a list with Player objects.
        '''
        players = []
        root = ET.fromstring(xml_string)
        for player_element in root.findall("player"):
            nickname = player_element.find("nickname").text
            email = player_element.find("email").text
            date_of_birth_str = player_element.find("date_of_birth").text  # Get the date as a string
            date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%d")  # Convert the string to a datetime object
            xp = int(player_element.find("xp").text)
            player_class = player_element.find("class").text

            player = Player(nickname, email, date_of_birth.strftime("%Y-%m-%d"), xp, player_class)
            players.append(player)
        return players
        # pass

    def to_xml(self, list_of_players):
        '''
            This function should transform a list with Player objects into a XML string.
        '''
        root = ET.Element("data")
        for player in list_of_players:
            player_element = ET.SubElement(root, "player")
            ET.SubElement(player_element, "nickname").text = player.nickname
            ET.SubElement(player_element, "email").text = player.email
            ET.SubElement(player_element, "date_of_birth").text = player.date_of_birth.strftime("%Y-%m-%d")
            ET.SubElement(player_element, "xp").text = str(player.xp)
            ET.SubElement(player_element, "class").text = player.cls

        xml_string = ET.tostring(root, encoding="utf-8")
        return xml_string.decode("utf-8")
        # pass

    def from_protobuf(self, binary):
        '''
            This function should transform a binary protobuf string into a list with Player objects.
        '''
        proto_players_list = player_pb2.PlayersList()
        proto_players_list.ParseFromString(binary)
        players = []
        
        for proto_player in proto_players_list.player:
            player = Player(
                proto_player.nickname,
                proto_player.email,
                proto_player.date_of_birth,
                proto_player.xp,
                player_pb2.Class.Name(proto_player.cls),
            )
            players.append(player)

        return players
        # pass

    def to_protobuf(self, list_of_players):
        '''
            This function should transform a list with Player objects intoa binary protobuf string.
        '''
        proto_players_list = player_pb2.PlayersList()

        for player in list_of_players:
            proto_player = proto_players_list.player.add()
            proto_player.nickname = player.nickname
            proto_player.email = player.email
            proto_player.date_of_birth = player.date_of_birth.strftime("%Y-%m-%d")
            proto_player.xp = player.xp
            proto_player.cls = player.cls
        protobuf_data = proto_players_list.SerializeToString()

        return protobuf_data
        # pass
