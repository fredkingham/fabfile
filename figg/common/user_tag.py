from twitter.models import UserDetails
# from id is a hash of the type, cal and tag
class UserTag(object):
    def __init__(self, user_tag_tuple = False, cal_type = None, user = None, tag = None, img = None):
        if user_tag_tuple:
            raise "user tag tuple arg no longer accepted"
            if len(user_tag_tuple) == 2:
                self.user, self.tag = user_tag_tuple
                self.cal_type = None
            else:    
                self.cal_type, self.user, self.tag = user_tag_tuple
        else:
            self.user = user
            self.tag = tag
            self.cal_type = cal_type
            self.img = img

    def __repr__(self):
        return "%s: %s" % (self.__class__, self.__dict__)

    def __str__(self):
        return "%s: %s" % (self.__class__, self.__dict__)

    def __key(self):
        return (self.cal_type, self.user, self.tag)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(x, y):
        return x.__key() == y.__key()

    def only_cal_type(self):
        return not self.user and not self.tag

    def convert_to_display(self):
        result = {}

        result["only_tag"] = self.tag and not self.user

        if self.tag:
            result["tag"] = self.tag

        if self.user:
            result["name"] = self.user
        
        if not result["only_tag"]:
            if self.img:
                result["img"] = self.img
            else:
                result["img"] = UserDetails.DEFAULT
        return result

    def as_json(self):
        return {
                "cal_type": self.cal_type,
                "user": self.user,
                "tag": self.tag,
                "img": self.img
                }

class UserTagWithSelected(UserTag):
    def __init__(self, cal_type = None, user = None, tag = None, img = None, selected = False, revealed = False):
        super(UserTagWithSelected, self).__init__(cal_type = cal_type, user = user, tag = tag, img = img)
        self.selected = selected
        self.revealed = revealed

    def as_json(self):
        return {
                "cal_type": self.cal_type,
                "user": self.user,
                "tag": self.tag,
                "img": self.img,
                "selected": self.selected,
                "revealed": self.revealed
                }





