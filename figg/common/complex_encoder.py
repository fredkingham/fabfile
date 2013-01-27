from django.utils import simplejson as json
from datetime import datetime, date, time

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime) or isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, time):
            return obj.strftime("%H:%M %p")
        else:
            try:
                return json.JSONEncoder.default(self, obj)
            except:
                return obj.as_json()

def encodeModel(queryset, mapping):
        keys = mapping.keys()
        queryset = queryset.values(keys)
        result = []

        for i in queryset:
            row = {}
            for k in keys:
                row[mapping[k]] = i[k]

            result.append(row)

        return result

