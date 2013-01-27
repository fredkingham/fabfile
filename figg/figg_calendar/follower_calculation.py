from figg_calendar.models import *


def remove(user, venue=None, tag=None, cal_id=None):
	""" needs to be changed to pass ids back """
	Tracking.objects.filter(user=user, venue__name=venue, tag__name=tag, cal__id=cal_id).delete()

def select(user, add_or_remove, venue=None, tag=None, cal_id=None):
	""" allows you to add or remove a cal/tag/venue"""
	args={}

	if venue != None:
		args["venue"]=Veneu.objects.get(name=venue)
	if tag != None:
		args["tag"]=Tag.objects.get(name= tag)
	if cal_id != None:
		args["cal"]=User.objects.get(id=cal_id)

	args["user"]=user

	#in case we're allowing for multiple filters fill in the rest with nulls
	for field in ["venue", "tag", "cal"]:
		if field not in args:
			args[field]=None

	if add_or_remove:
		#not using get_or_create because we've overrided the field save field to add an updated field
		selected_trackers=Tracking.objects.filter(**args)
		if selected_trackers:
			if len(selected_trackers) > 1:
				raise Exception("multiple selected, this shouldn't be possible")
			selected=selected_trackers[0]
			selected.selected=True	
			selected.save()
		else:
			following=Tracking(**args)
			following.save()
	else:
		selected_trackers=Tracking.objects.filter(**args)
		if selected_trackers:
			selected=selected_trackers[0]
			selected.selected=False
			selected.save()	


class CalTo(object):
	def __init__(self, cal__username, cal__id, cal__user_details__user_img_normal, cal__user_details__user_img_mini, cal__user_details__user_img_bigger):
		self.name=cal__username
		self.id=cal__id
		self.img_normal=cal__user_details__user_img_normal
		self.img_mini=cal__user_details__user_img_mini
		self.img_large=cal__user_details__user_img_bigger

	def as_json(self):
		return self.__dict__

class TagTo(object):
	def __init__(self, tag__name, tag__id):
		self.name=tag__name
		self.id=tag__id

	def as_json(self):
		return self.__dict__

class VenueTo(object):
	def __init__(self, venue__name, venue__id, venue__postcode):
		self.name=venue__name
		self.id=venue__id
		self.postcode=venue__postcode

	def as_json(self):
		return self.__dict__

class Trackee(object):
	def __init__(self, cal__username, cal__user_details__user_img_bigger, cal__user_details__user_img_mini, cal__user_details__user_img_normal, selected, cal_type, venue__name, venue__postcode, tag__name):
		self.cal_type=cal_type
		self.selected=selected

		if cal__username:
			self.cal_to=CalTo(cal__username, cal__id, cal__user_details__user_img_normal, cal__user_details__user_img_mini, cal__user_details__user_img_bigger)

		if venue__name:
			self.venue_to=VenueTo(venue__name, venue__id, venue__postcode)

		if tag__name:
			self.tag_to=TagTo(tag__name, tag__id)

	def as_json(self):
		return self.__dict__

def get_tracking(user):
	""" get all cal tags that the user is following and whether they are selected """

	values=["selected", "cal_type"]
	values.extend(["cal__username", "cal__user_details__user_img_mini", "cal__user_details__user_img_normal", "cal__user_details__user_img_bigger"])
	values.extend(["venue__id", "venue__name", "venue__postcode"])
	values.extend(["tag__name", "tag__id"])

	query=Tracking.objects.filter(user=user)
	query=query.values(*values)
	return [Trackee(**i) for i in query]

def get_selected_users(user, user_ids):
	""" returns all the ids that are selected """
	return Tracking.objects.filter(user=user).filter(selected=True).filter(cal__id__in=user_ids).values_list("cal__id", flat=True)

def get_selected_tags(user, tag_names):
	return Tracking.objects.filter(user=user).filter(selected=True).filter(tag__name__in=tag_names).values_list("tag__name", flat=True)










