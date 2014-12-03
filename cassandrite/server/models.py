from cqlengine import columns, models


class Event(models.Model):
    path = columns.Text(primary_key=True, partition_key=True)
    time = columns.BigInt(primary_key=True)
    data = columns.BigInt()
    ceiling = columns.BigInt(index=True)
    floor = columns.BigInt(index=True)

    def __str__(self):
        return '({}, {}-{}) {}'.format(self.path, self.ceiling, self.floor, self.data)

    def __repr__(self):
        return '<Event {} />'.format(str(self))

    def get_interval(self):
        return self.floor, self.ceiling
