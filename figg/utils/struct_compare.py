
class StructCompare(object):

    def __init__(self,new, old):
        self.new = new
        self.old = old


    def only_in_new(self,):
        return [i for i in self.new if i not in self.old]

    def only_in_old(self,):
        return [i for i in self.old if i not in self.new]

    
    def get_old(self,event_time_id):
        return self.get_from_event_id(event_time_id)


    def get_new(self,event_time_id):
        return self.get_from_event_id(event_time_id, old = False)

    def get_from_event_id(self,event_time_id, old = True):

        result = []

        if old:
            old_or_new = self.old
        else:
            old_or_new = self.new

        for i in old_or_new:
            if i["time_id"] == event_time_id:
                result.append(i)

        return result

    def delete_field(self, field):
        for i in self.new:
            del(i[field])

        for i in self.old:
            del(i[field])
