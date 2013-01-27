from collections import defaultdict
from django.contrib.auth.models import User
from mainPage.models import SelectedCal, RevealedCal
from twitter import user_calculation
from mainPage import note_calculation
from twitter.models import UserDetails
import twitter
import copy
from django.utils import simplejson
from user_tag import UserTagWithSelected

class CalHolder(object):

    # cal users is a calculated_cal object with user and tag options
    def __init__(self, user_tags = [], user_username = False):
        self.user_tags = set(user_tags)
        self.update_required = True
        self.cal_tag_to_type = False
        self.username = user_username

    def append(self, user_tag):
        self.user_tags.add(user_tag)
        self.update_required = True

    def extend(self, user_tags):
        self.user_tags.update(user_tags)
        self.update_required = True

    def remove(self, user_tags):
        self.user_tags -= set(user_tags)

    def cals_without_tags(self):
        return [user_tag.user for user_tag in self.user_tags if not user_tag.tag]

    def cals_with_tags(self):
        cals_to_tags = defaultdict(list)

        for user_tag in self.user_tags:
            if user_tag.user and user_tag.tag:
                cals_to_tags[user_tag.user].append(user_tag.tag)

        return cals_to_tags

    def user_in_selection(self, username):
        return bool([i for i in self.user_tags if i.user == username])

    def isEmpty(self):
        return not bool(self.user_tags)

    def get_cal_type_only(self):
        return set([user_tag.cal_type for user_tag in self.user_tags if not user_tag.user and not user_tag.tag])

    def get_tag_only(self):
        return set([user_tag.tag for user_tag in self.user_tags if not user_tag.user])

    def get_cal_tags_for_cal_type(self, cal_type):
        return [x for x in self.user_tags if x.cal_type == cal_type.cal_type and x.user]

    def get_cal_usernames(self):
        cals = set() 

        for user_tag in self.user_tags:
            if user_tag.user:
                cals.add(user_tag.user)

        return cals

    def split_on_cals(self, cals):
        with_cals = []
        without_cals = []

        for user_tag in self.user_tags:
            if user_tag.user in cals:
                with_cals.append(user_tag)
            else:
                without_cals.append(user_tag)

        return with_cals, without_cals

    def cursor(self):
        for user_tag in self.user_tags:
            yield user_tag

    def get_display_info(self, size = twitter.MINI):
        from_cals = []
        user_info = user_calculation.get_imgs(self.get_cal_usernames(), size = size)
        for user_tag in self.user_tags:
            if user_tag.user:
                user_tag.img = user_info.get(user_tag.user)

            for_display = user_tag.convert_to_display()
            if not for_display in from_cals:
                from_cals.append(for_display)

        return from_cals

    def get_cal_details(self):
        '''returns a tuple representation of the cal holders user tags'''
        return [(user_tag.cal_type, user_tag.user, user_tag.tag) for user_tag in self.user_tags]

    def get_type_for_cal_tag(self, user_tag):
        ''' pass in a user tag return all user tags that this would fall in'''

        return_user_tags = []
        for self_user_tag in self.user_tags:
            if self_user_tag.tag and not self_user_tag.user:
                if user_tag.tag == self_user_tag.tag:
                    return_user_tags.append(self_user_tag)
            elif self_user_tag.user and not self_user_tag.tag:
                if user_tag.user == self_user_tag.user:
                    return_user_tags.append(self_user_tag)
            elif self_user_tag.user and self_user_tag.tag:
                if user_tag.user == self_user_tag.user and self_user_tag.tag == user_tag.tag:
                    return_user_tags.append(self_user_tag)

        return return_user_tags

    def get_cal_children(self, cal):
        '''returns a cal_holder of all usertags that have this cal'''
        return_user_tags = []
        for user_tag in self.user_tags:
            if user_tag.user == cal:
                return_user_tags.append(user_tag)

        return CalHolder(return_user_tags)

    def __str__(self):
        result = ""
        for user_tag in self.user_tags:
            result = "%s \n %s" % (result, user_tag)
        return result

    def __repr__(self):
        result = ""
        for user_tag in self.user_tags:
            result = "%s \n %s" % (result, user_tag)
        return result

    def unique_user_display(self):
        result = ()

    def as_json(self):
        result = [];
        for user_tag in self.user_tags:
            result.append(user_tag.as_json())

        return result

class CalHolderWithSelected(CalHolder):
    '''used by the cal_calculation to filter add selected and revealed
    fields'''
    from mainPage.models import SelectedCal, RevealedCal

    def __init__(self, user_tags = [], user_username = False):
        super(CalHolderWithSelected, self).__init__(user_tags = user_tags, user_username = user_username)

    def get_selected(self):
        result = []

        for user_tag in self.user_tags:
            if user_tag.selected:
                if user_tag.user or user_tag.tag:
                    result.append(user_tag)
                else:
                    result.extend(self.get_cal_tags_for_cal_type(user_tag))

        # if nothing is selected, select everything
        if not result:
            for user_tag in self.user_tags:
                if not user_tag.user and not user_tag.tag:
                    result.extend(self.get_cal_tags_for_cal_type(user_tag))



        return result

    def get_revealed(self):
        result = []

        for user_tag in self.user_tags:
            if user_tag.revealed:
                result.append(user_tag)

        return result

    def calculate_selected_revealed(self):
        def convert_selected_to_user_tag(x, revealed = False):
            result = UserTagWithSelected()
            result.cal_type = x.cal_type
            result.user = x.cal

            if not revealed:
                result.tag = x.tag

            return result

        selected = SelectedCal.objects.filter(user = self.username)
        selected_user_tags = set([convert_selected_to_user_tag(x) for x in selected])
        revealed_user_tags = set([convert_selected_to_user_tag(x, revealed = True) for x in selected])

        return (selected_user_tags, revealed_user_tags)


    def update_selected_and_revealed(self):
        selected_user_tags, revealed_user_tags = self.calculate_selected_revealed()

        for revealed in revealed_user_tags:
            if revealed.user:
                #tags = note_calculation.calculate_tags(revealed.user)
                tags = []
                tagged_user_tags = [UserTagWithSelected(cal_type = revealed.cal_type, user = revealed.user, tag = tag) for tag in tags]
                self.extend(tagged_user_tags)

        for user_tag in self.user_tags:
            user_tag.selected = user_tag in selected_user_tags
            user_tag.revealed = user_tag in revealed_user_tags



    def exclude_cal_type_only(self):
        result = []
        for user_tag in self.user_tags:
            if user_tag.user or user_tag.tag:
                result.append(user_tag)

        return result









