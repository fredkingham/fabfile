from mainPage.models import Tag, SelectedCal
from twitter import data_extract
from django.db.models import Q, Count


def get_user_tag_count(user):
    return Tag.objects.filter(cals=user).count()


def get_event_tag_count(tag_name):
    if Tag.objects.filter(name=tag_name).exists():
        return Tag.objects.get(name=tag_name).events.filter(deleted=False).count()
    else:
        return 0


def save_tags_for_notes(description, user, note, event_obj):
    '''deals with saving tags for both notes and events, if the tag
    already exists add it, if not create it'''

    tags = data_extract.get_tags(description)
    existing_tag_objs = Tag.objects.filter(name__in=tags)
    existing_tags = dict((x.name, x) for x in existing_tag_objs)

    for tag in tags:
        if tag not in existing_tags:
            tag_obj = Tag(name=tag)
            tag_obj.save()
        else:
            tag_obj = existing_tags[tag]

        tag_obj.cals.add(user)
        tag_obj.notes.add(note)
        tag_obj.events.add(event_obj)


def save_tags_for_events(user, events, added_tag_names=[]):
    nested_tags = [data_extract.get_tags("%s %s" % (event.title, event.description)) for event in events]
    tag_names = [item for sublist in nested_tags for item in sublist]
    tag_names.extend(added_tag_names)
    tags = create_tags(tag_names)
    user.tag_cals.add(*tags)
    added_tags = list(tags.filter(name__in = added_tag_names))

    for event in events:
        tag_names = data_extract.get_tags("%s %s" % (event.title, event.description))
        tags = list(Tag.objects.filter(name__in = tag_names))
        tags.extend(added_tags)
        event.tags.add(*tags)


def create_tags(tag_names):
    existing_tags = set(Tag.objects.filter(
        name__in=tag_names).values_list("name", flat=True))
    new_tag_names = set(tag_names) - existing_tags

    new_tags = [Tag(name=new_tag_name) for new_tag_name in new_tag_names]
    Tag.objects.bulk_create(new_tags)

    # bring in the tags again as bulk create doesn't add ids
    return Tag.objects.filter(name__in = tag_names)


def get_calculated_tags(cal, tag_names):
    selected_tag_names = SelectedCal.objects.filter(
        tag__name__in=tag_names, cal=cal).values_list("tag__name", flat=True)

    calculated_tags = []

    for tag_name in tag_names:
        calculated_tags.append(
            TagCalculated(tag_name, tag_name in selected_tag_names))

    return calculated_tags


def get_tags(event_id):
    return Tag.objects.filter(events__id=event_id).values_list("name", flat=True)


def get_tag(tag_name):
    return Tag.objects.get(name=tag_name)


class TagCalculated:

    def __init__(self, tag, selected=False):
        self.tag = tag
        self.selected = selected

    def __repr__(self):
        return "%s: %s %s" % (self.__class__, self.tag, self.selected)


def get_popular_tags(for_date, amount=8):

    if not for_date:
        tags = Tag.objects.annotate(count_viewed_cals=Count('viewedcalendar')).order_by('count_viewed_cals').distinct()[:amount]
    else:
        tags = Tag.objects.filter(Q(events__event_times__date__gte=for_date) |
                                  Q(notes__event_times__date__gte=for_date))
        tags = tags.annotate(count_viewed_cals=Count('viewedcalendar')).order_by('count_viewed_cals').distinct()[:amount]

    still_needed = amount - len(tags)

    if still_needed:
        ids = [t.id for t in tags]
        not_viewed = Tag.objects.exclude(
            id__in=ids).distinct()[:still_needed]
        tags = list(tags)
        tags.extend(not_viewed)

    return tags
